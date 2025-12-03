from typing import Optional, List
from datetime import datetime
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
import json
import io

# MongoDB 設定
MONGODB_URI = "mongodb+srv://lai:Hs910738@lqi.pbmygvj.mongodb.net/"
DB_NAME = "data"

app = FastAPI(title="Experience Sampling API", version="1.0.0")

# CORS 設定（允許 Expo app 調用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生產環境建議限制來源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class SampleCreate(BaseModel):
    created_at: str
    sentiment: Optional[int] = None
    activity: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    video_uri: Optional[str] = None
    user_id: str = "default_user"  # 可擴充多使用者

class SampleResponse(BaseModel):
    id: str
    created_at: str
    sentiment: Optional[int]
    activity: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    video_uri: Optional[str]
    user_id: str

# MongoDB 連線生命週期
@app.on_event("startup")
async def startup_db_client():
    app.mongodb_client = AsyncIOMotorClient(MONGODB_URI)
    app.mongodb = app.mongodb_client[DB_NAME]
    print("✅ Connected to MongoDB")

@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()
    print("❌ Disconnected from MongoDB")

# API 端點
@app.get("/")
async def root():
    return {
        "message": "Experience Sampling API",
        "version": "1.0.0",
        "endpoints": {
            "POST /samples": "Create new sample",
            "GET /samples": "Get all samples",
            "GET /samples/{user_id}": "Get samples by user"
        }
    }

@app.post("/samples", response_model=dict, status_code=201)
async def create_sample(sample: SampleCreate):
    """建立新的經驗取樣記錄"""
    sample_dict = sample.dict()
    # 將 ISO 字串轉成 naive UTC datetime（PyMongo 不接受 timezone-aware datetime）
    created_dt = datetime.fromisoformat(sample.created_at.replace("Z", "+00:00"))
    sample_dict["created_at_datetime"] = created_dt.replace(tzinfo=None)
    
    result = await app.mongodb["samples"].insert_one(sample_dict)
    
    return {
        "id": str(result.inserted_id),
        "message": "Sample created successfully",
        "data": sample_dict
    }

@app.get("/samples", response_model=List[dict])
async def get_all_samples(limit: int = 100):
    """取得所有記錄（最多 100 筆）"""
    samples = await app.mongodb["samples"].find().sort("created_at_datetime", -1).limit(limit).to_list(limit)
    
    for sample in samples:
        sample["id"] = str(sample.pop("_id"))
    
    return samples

@app.get("/samples/{user_id}", response_model=List[dict])
async def get_samples_by_user(user_id: str, limit: int = 100):
    """依使用者 ID 取得記錄"""
    samples = await app.mongodb["samples"].find({"user_id": user_id}).sort("created_at_datetime", -1).limit(limit).to_list(limit)
    
    if not samples:
        raise HTTPException(status_code=404, detail="No samples found for this user")
    
    for sample in samples:
        sample["id"] = str(sample.pop("_id"))
    
    return samples

@app.get("/health")
async def health_check():
    """健康檢查端點"""
    try:
        await app.mongodb.command("ping")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {str(e)}")

@app.get("/export")
async def export_all_samples(format: str = "json", limit: int = 1000):
    """匯出所有記錄（JSON 格式）"""
    samples = await app.mongodb["samples"].find().sort("created_at_datetime", -1).limit(limit).to_list(limit)
    
    for sample in samples:
        sample["id"] = str(sample.pop("_id"))
        # 移除內部欄位
        sample.pop("created_at_datetime", None)
    
    if format == "json":
        # 產生 JSON 檔案並回傳下載
        json_data = json.dumps(samples, indent=2, ensure_ascii=False)
        stream = io.BytesIO(json_data.encode('utf-8'))
        
        return StreamingResponse(
            stream,
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=samples_export.json"}
        )
    
    return samples

@app.post("/upload-video/")
async def upload_video(file: UploadFile = File(...), user_id: str = "default_user"):
    """上傳 vlog 影片（參考 tutorial）"""
    import os
    import aiofiles
    
    # 使用絕對路徑確保檔案存在正確位置
    base_dir = os.path.abspath("data")
    file_dir = os.path.join(base_dir, user_id)
    os.makedirs(file_dir, exist_ok=True)
    
    file_path = os.path.join(file_dir, file.filename)
    
    async with aiofiles.open(file_path, "wb") as buffer:
        while True:
            chunk = await file.read(1024 * 1024)  # 1MB chunks
            if not chunk:
                break
            await buffer.write(chunk)
    
    print(f"✅ Video uploaded: {file_path}, exists: {os.path.exists(file_path)}")
    
    return {
        "filename": file.filename,
        "saved_to": file_path,
        "user_id": user_id,
        "message": "Video uploaded successfully"
    }

# 影片下載端點 (移到 app = FastAPI(...) 之後)
@app.get("/download-video/{user_id}/{filename}")
async def download_video(user_id: str, filename: str):
    import os
    
    # 使用絕對路徑
    base_dir = os.path.abspath("data")
    file_path = os.path.join(base_dir, user_id, filename)
    
    print(f"🔍 Looking for file: {file_path}")
    print(f"📁 File exists: {os.path.exists(file_path)}")
    
    if not os.path.exists(file_path):
        # 列出目錄內容以便除錯
        user_dir = os.path.join(base_dir, user_id)
        if os.path.exists(user_dir):
            files = os.listdir(user_dir)
            print(f"📂 Files in {user_dir}: {files}")
        else:
            print(f"❌ Directory not found: {user_dir}")
        
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    
    return FileResponse(file_path, media_type="video/mp4", filename=filename)
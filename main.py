from typing import Optional, List
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

# MongoDB 設定
MONGODB_URI = "mongodb+srv://lai:Hs910738@lqi.pbmygvj.mongodb.net/"
DB_NAME = "lai"

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
    sample_dict["created_at_datetime"] = datetime.fromisoformat(sample.created_at.replace("Z", "+00:00"))
    
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
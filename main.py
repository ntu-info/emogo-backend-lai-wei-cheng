from typing import Optional, List
from datetime import datetime
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, Response, HTMLResponse
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
from pydantic import BaseModel
from bson import ObjectId
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
    app.fs = AsyncIOMotorGridFSBucket(app.mongodb)
    print("✅ Connected to MongoDB with GridFS")

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
            "GET /dashboard": "View all data (HTML page)",
            "POST /samples": "Create new sample",
            "GET /samples": "Get all samples",
            "GET /samples/{user_id}": "Get samples by user",
            "GET /export": "Export data as JSON",
            "POST /upload-video/": "Upload video to GridFS",
            "GET /download-video/{user_id}/{filename}": "Download video from GridFS"
        }
    }

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """HTML 頁面：顯示所有資料（vlogs, sentiments, GPS）"""
    # 取得所有樣本
    samples = await app.mongodb["samples"].find().sort("created_at_datetime", -1).limit(100).to_list(100)
    
    # 取得所有 GridFS 影片
    cursor = app.fs.find({})
    videos = await cursor.to_list(length=None)
    
    # 準備樣本資料
    samples_html = ""
    for sample in samples:
        sample_id = str(sample.get("_id", ""))
        created_at = sample.get("created_at", "N/A")
        sentiment = sample.get("sentiment", "N/A")
        activity = sample.get("activity", "N/A")
        lat = sample.get("latitude", "N/A")
        lon = sample.get("longitude", "N/A")
        user_id = sample.get("user_id", "N/A")
        
        samples_html += f"""
        <tr>
            <td>{created_at}</td>
            <td>{user_id}</td>
            <td>{sentiment}</td>
            <td>{activity}</td>
            <td>{lat}, {lon}</td>
        </tr>
        """
    
    # 準備影片列表
    videos_html = ""
    if videos:
        for video in videos:
            filename = video.get("filename", "unknown")
            file_id = str(video.get("_id", ""))
            metadata = video.get("metadata", {})
            user_id = metadata.get("user_id", "unknown")
            upload_date = video.get("uploadDate", "N/A")
            length = video.get("length", 0)
            size_mb = round(length / (1024 * 1024), 2)
            
            download_url = f"/download-video/{user_id}/{filename}"
            videos_html += f"""
            <tr>
                <td>{filename}</td>
                <td>{user_id}</td>
                <td>{size_mb} MB</td>
                <td>{upload_date}</td>
                <td><a href="{download_url}" download class="download-btn">Download</a></td>
            </tr>
            """
    else:
        videos_html = '<tr><td colspan="5">No videos uploaded yet</td></tr>'
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>EmoGo Data Dashboard</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
                min-height: 100vh;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 12px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                padding: 40px;
            }}
            h1 {{
                color: #667eea;
                margin-bottom: 10px;
                font-size: 2.5em;
            }}
            .subtitle {{
                color: #666;
                margin-bottom: 30px;
                font-size: 1.1em;
            }}
            .section {{
                margin-bottom: 40px;
            }}
            h2 {{
                color: #333;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 3px solid #667eea;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                background: white;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
            th {{
                background: #667eea;
                color: white;
                padding: 15px;
                text-align: left;
                font-weight: 600;
            }}
            td {{
                padding: 12px 15px;
                border-bottom: 1px solid #eee;
            }}
            tr:hover {{
                background: #f8f9ff;
            }}
            .download-btn {{
                background: #667eea;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                text-decoration: none;
                display: inline-block;
                transition: all 0.3s;
            }}
            .download-btn:hover {{
                background: #5568d3;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
            }}
            .export-btn {{
                background: #10b981;
                color: white;
                padding: 12px 24px;
                border-radius: 8px;
                text-decoration: none;
                display: inline-block;
                font-weight: 600;
                transition: all 0.3s;
                margin-top: 20px;
            }}
            .export-btn:hover {{
                background: #059669;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
            }}
            .stats {{
                display: flex;
                gap: 20px;
                margin-bottom: 30px;
            }}
            .stat-card {{
                flex: 1;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
            }}
            .stat-number {{
                font-size: 2.5em;
                font-weight: bold;
            }}
            .stat-label {{
                margin-top: 5px;
                opacity: 0.9;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎭 EmoGo Data Dashboard</h1>
            <p class="subtitle">Experience Sampling Data Viewer & Exporter</p>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{len(samples)}</div>
                    <div class="stat-label">Total Samples</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(videos)}</div>
                    <div class="stat-label">Total Videos</div>
                </div>
            </div>
            
            <div class="section">
                <h2>📊 Sample Data (Sentiments & GPS Coordinates)</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Time</th>
                            <th>User ID</th>
                            <th>Sentiment</th>
                            <th>Activity</th>
                            <th>GPS (Lat, Lon)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {samples_html if samples_html else '<tr><td colspan="5">No samples found</td></tr>'}
                    </tbody>
                </table>
            </div>
            
            <div class="section">
                <h2>🎥 Video Data (Vlogs)</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Filename</th>
                            <th>User ID</th>
                            <th>Size</th>
                            <th>Upload Date</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {videos_html}
                    </tbody>
                </table>
            </div>
            
            <div class="section">
                <h2>📥 Export Options</h2>
                <a href="/export" class="export-btn">📦 Download All Data (JSON)</a>
            </div>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

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
    """上傳 vlog 影片到 MongoDB GridFS"""
    # 讀取檔案內容
    file_data = await file.read()
    
    # 上傳到 GridFS，包含 metadata
    file_id = await app.fs.upload_from_stream(
        file.filename,
        file_data,
        metadata={
            "user_id": user_id,
            "content_type": "video/mp4",
            "original_filename": file.filename
        }
    )
    
    print(f"✅ Video uploaded to GridFS: {file.filename}, file_id: {file_id}")
    
    return {
        "filename": file.filename,
        "file_id": str(file_id),
        "user_id": user_id,
        "message": "Video uploaded to MongoDB GridFS successfully"
    }

# 影片下載端點 (從 GridFS 下載)
@app.get("/download-video/{user_id}/{filename}")
async def download_video(user_id: str, filename: str):
    """從 MongoDB GridFS 下載影片"""
    # 查詢 GridFS 中符合條件的檔案
    cursor = app.fs.find({"metadata.user_id": user_id, "filename": filename})
    files = await cursor.to_list(length=1)
    
    if not files:
        raise HTTPException(status_code=404, detail=f"Video not found: {filename} for user {user_id}")
    
    file_doc = files[0]
    file_id = file_doc["_id"]
    
    # 從 GridFS 下載檔案
    grid_out = await app.fs.open_download_stream(file_id)
    file_data = await grid_out.read()
    
    print(f"✅ Video downloaded from GridFS: {filename}, size: {len(file_data)} bytes")
    
    return Response(content=file_data, media_type="video/mp4", headers={
        "Content-Disposition": f'attachment; filename="{filename}"'
    })
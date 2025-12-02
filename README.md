# EmoGo Backend - FastAPI + MongoDB

Experience Sampling App 的後端 API 服務

## 🔗 Public Server

**Base URL**: https://fastapi-example-ykqs.onrender.com

---

## 📡 API Endpoints

### 1. **Root**
```
GET /
```
回傳 API 基本資訊與可用端點列表

**範例**:
```bash
curl https://fastapi-example-ykqs.onrender.com/
```

---

### 2. **Health Check**
```
GET /health
```
檢查伺服器與資料庫連線狀態

**範例**:
```bash
curl https://fastapi-example-ykqs.onrender.com/health
```

**回應**:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

---

### 3. **Create Sample** 📝
```
POST /samples
```
建立新的經驗取樣記錄

**Request Body**:
```json
{
  "created_at": "2025-12-02T10:30:00Z",
  "sentiment": 4,
  "activity": "上課",
  "latitude": 25.033964,
  "longitude": 121.564472,
  "video_uri": "file:///path/to/video.mp4",
  "user_id": "b12207073"
}
```

**範例**:
```bash
curl -X POST https://fastapi-example-ykqs.onrender.com/samples \
  -H "Content-Type: application/json" \
  -d '{
    "created_at": "2025-12-02T10:30:00Z",
    "sentiment": 4,
    "activity": "測試",
    "latitude": 25.033,
    "longitude": 121.565,
    "user_id": "test_user"
  }'
```

---

### 4. **Get All Samples** 📊
```
GET /samples?limit=100
```
取得所有記錄（依時間降序）

**Query Parameters**:
- `limit` (optional): 回傳筆數上限，預設 100

**範例**:
```bash
curl https://fastapi-example-ykqs.onrender.com/samples
```

---

### 5. **Get Samples by User** 👤
```
GET /samples/{user_id}?limit=100
```
取得特定使用者的記錄

**範例**:
```bash
curl https://fastapi-example-ykqs.onrender.com/samples/b12207073
```

---

### 6. **Export Data** 📥 *(作業要求)*
```
GET /export?format=json&limit=1000
```
匯出所有記錄為 JSON 檔案（可下載）

**Query Parameters**:
- `format` (optional): 匯出格式，目前支援 `json`，預設 `json`
- `limit` (optional): 匯出筆數上限，預設 1000

**範例**:
```bash
# 瀏覽器直接開啟（會下載檔案）
https://fastapi-example-ykqs.onrender.com/export

# 使用 curl 下載
curl -O https://fastapi-example-ykqs.onrender.com/export
```

**回應**: 下載 `samples_export.json` 檔案

---

### 7. **Upload Video** 🎥
```
POST /upload-video/
```
上傳 vlog 影片檔案

**Form Data**:
- `file`: 影片檔案 (multipart/form-data)
- `user_id` (optional): 使用者 ID，預設 `default_user`

**範例**:
```bash
curl -X POST https://fastapi-example-ykqs.onrender.com/upload-video/ \
  -F "file=@/path/to/video.mp4" \
  -F "user_id=b12207073"
```

---

## 🗄️ MongoDB 測試資料

### 使用 MongoDB Compass 建立假資料

1. **連接到 MongoDB Atlas**
   ```
   mongodb+srv://lai:Hs910738@lqi.pbmygvj.mongodb.net/
   ```

2. **選擇資料庫**: `lai`

3. **選擇集合**: `samples`

4. **插入測試文件**:
   ```json
   {
     "created_at": "2025-12-02T09:00:00.000Z",
     "created_at_datetime": ISODate("2025-12-02T09:00:00.000Z"),
     "sentiment": 4,
     "activity": "早餐",
     "latitude": 25.021,
     "longitude": 121.494,
     "video_uri": "ph://test-video-001",
     "user_id": "test_user_001"
   }
   ```

5. **建立多筆資料**（至少 3-5 筆，涵蓋不同時間與使用者）

---

## 🧪 API 測試

### Swagger UI (互動式文件)
```
https://fastapi-example-ykqs.onrender.com/docs
```

### ReDoc (API 規格文件)
```
https://fastapi-example-ykqs.onrender.com/redoc
```

---

## 🚀 本地開發

### 安裝依賴
```bash
pip install -r requirements.txt
```

### 啟動伺服器
```bash
uvicorn main:app --reload
```

本地端點: http://localhost:8000

---

## 📦 Dependencies

- **FastAPI**: Web framework
- **Motor**: MongoDB async driver
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server
- **aiofiles**: Async file operations
- **python-multipart**: File upload support

---

## 🔒 環境變數

在 Render 設定以下環境變數：

```
MONGODB_URI = mongodb+srv://lai:Hs910738@lqi.pbmygvj.mongodb.net/
DB_NAME = lai
```

---

## 👤 作者

**賴韋誠** (B12207073)  
國立臺灣大學

---

## 📝 作業檢查清單

- [x] FastAPI + MongoDB 後端
- [x] 部署到公開伺服器 (Render.com)
- [x] `/export` API 端點
- [x] MongoDB Compass 測試資料
- [x] README.md 列出 `/export` URI
- [x] CORS 設定
- [x] 檔案上傳功能
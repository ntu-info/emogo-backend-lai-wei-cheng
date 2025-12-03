# EmoGo Backend - FastAPI + MongoDB

Experience Sampling App 的後端 API 服務

## 🔗 作業要求 API URL

**Base URL**: https://fastapi-example-ykqs.onrender.com

### 匯出資料 (Export)
```
GET https://fastapi-example-ykqs.onrender.com/export
```

### 上傳影片 (Upload Video)
```
POST https://fastapi-example-ykqs.onrender.com/upload-video/?user_id={user_id}
```

### 下載影片 (Download Video)
```
GET https://fastapi-example-ykqs.onrender.com/download-video/{user_id}/{filename}
```

---

## 📡 API Endpoints

### 1. **Root**
```
GET /
```

### 2. **Health Check**
```
GET /health
```

### 3. **Create Sample**
```
POST /samples
```

### 4. **Get All Samples**
```
GET /samples?limit=100
```

### 5. **Get Samples by User**
```
GET /samples/{user_id}?limit=100
```

### 6. **Export Data**
```
GET /export?format=json&limit=1000
```

### 7. **Upload Video**
```
POST /upload-video/?user_id={user_id}
```

### 8. **Download Video**
```
GET /download-video/{user_id}/{filename}
```

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

---

## 📦 Dependencies

- **FastAPI**: Web framework
- **Motor**: MongoDB async driver (支援 GridFS)
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server
- **python-multipart**: File upload support
- **pymongo**: MongoDB BSON support (GridFS)

---

## 👤 作者

**賴韋誠** (B12207073)  
國立臺灣大學
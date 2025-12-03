# EmoGo Backend - FastAPI + MongoDB

Experience Sampling App 的後端 API 服務

## 作業要求：資料查看/下載頁面

**Dashboard HTML 頁面**（可查看所有 vlogs、sentiments、GPS 資料並下載）:
`
https://fastapi-example-ykqs.onrender.com/dashboard
`

---

## 其他 API Endpoints

**Base URL**: https://fastapi-example-ykqs.onrender.com

### 匯出資料 (Export JSON)
`
GET https://fastapi-example-ykqs.onrender.com/export
`

### 上傳影片 (Upload Video)
`
POST https://fastapi-example-ykqs.onrender.com/upload-video/?user_id={user_id}
`

### 下載影片 (Download Video)
`
GET https://fastapi-example-ykqs.onrender.com/download-video/{user_id}/{filename}
`

---

## 作者

**賴韋誠** (B12207073)  
國立臺灣大學

# Experience Sampling Backend - 部署指南

## 🚀 本地開發

### 1. 安裝依賴
```bash
cd emogo-backend-lai-wei-cheng-main
pip install -r requirements.txt
```

### 2. 啟動伺服器
```bash
uvicorn main:app --reload
```

伺服器會在 http://localhost:8000 啟動

### 3. 測試 API
- API 文件：http://localhost:8000/docs
- 健康檢查：http://localhost:8000/health

---

## ☁️ 部署到 Render.com（免費）

### 步驟 1：推送程式碼到 GitHub
```bash
cd emogo-backend-lai-wei-cheng-main
git init
git add .
git commit -m "Add Experience Sampling API"
git remote add origin https://github.com/你的帳號/repo名稱.git
git push -u origin main
```

### 步驟 2：連接 Render
1. 到 https://render.com 註冊/登入
2. 點擊 **New +** → **Web Service**
3. 連接你的 GitHub repository
4. 設定：
   - **Name**: `experience-sampling-api`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`

### 步驟 3：設定環境變數
在 Render Dashboard → Environment：
```
MONGODB_URI = mongodb+srv://lai:Hs910738@lqi.pbmygvj.mongodb.net/
DB_NAME = lai
```

### 步驟 4：部署
- 點擊 **Create Web Service**
- 等待建置完成（約 3-5 分鐘）
- 取得部署網址（例如：`https://experience-sampling-api.onrender.com`）

### 步驟 5：更新 Expo App
在 `expo-app/services/api.ts` 更新：
```typescript
const API_BASE_URL = __DEV__ 
  ? 'http://localhost:8000'
  : 'https://your-app.onrender.com';  // 替換成實際網址
```

---

## 🧪 測試 API

### 使用 curl
```bash
# 健康檢查
curl https://your-app.onrender.com/health

# 建立記錄
curl -X POST https://your-app.onrender.com/samples \
  -H "Content-Type: application/json" \
  -d '{
    "created_at": "2025-12-02T10:30:00Z",
    "sentiment": 4,
    "activity": "測試",
    "latitude": 25.033,
    "longitude": 121.565,
    "user_id": "test_user"
  }'

# 取得所有記錄
curl https://your-app.onrender.com/samples
```

### 使用 Expo App
1. 開啟 Vlog 分頁
2. 開啟「☁️ 雲端同步」開關
3. 填寫問卷並送出
4. 確認顯示「✅ 已同步」

---

## 📊 MongoDB Atlas 設定

### 確認連線字串
```
mongodb+srv://lai:Hs910738@lqi.pbmygvj.mongodb.net/
```

### 檢視資料
1. 登入 https://cloud.mongodb.com
2. 進入 cluster → Browse Collections
3. 資料庫：`lai`
4. 集合：`samples`

---

## 🔒 安全性建議（生產環境）

1. **環境變數**：不要把密碼寫在程式碼中
2. **CORS**：限制允許的來源
3. **驗證**：加入 API Key 或 JWT
4. **速率限制**：防止濫用

---

## 🐛 常見問題

### Render 免費版限制
- 15 分鐘無活動會休眠
- 第一次請求會較慢（冷啟動）
- 每月 750 小時免費

### MongoDB 連線失敗
- 檢查 IP 白名單（MongoDB Atlas → Network Access）
- 確認帳號密碼正確
- 測試連線字串

### Expo App 無法連線
- 檢查 API_BASE_URL 是否正確
- 確認 Render 服務正在運行
- 查看 Render logs

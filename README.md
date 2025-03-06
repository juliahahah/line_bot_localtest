# LINE Bot Lambda Function

這個專案包含一個AWS Lambda函數，用於處理LINE Bot的webhook請求和回覆訊息。

## 功能特點

- 接收並處理來自LINE平台的webhook事件
- 驗證請求簽名以確保安全性
- 支援本地測試環境（使用.env檔案）
- 獲取用戶資料並以個人化方式回覆

## 系統需求

- Python 3.6+
- LINE Bot SDK v3
- dotenv (用於本地開發)

## 安裝指南

1. 克隆此儲存庫：
   ```bash
   git clone <儲存庫URL>
   cd line_bot_localtest
   ```

2. 安裝依賴套件：
   ```bash
   pip install line-bot-sdk python-dotenv
   ```

3. 創建.env檔案並設定您的LINE Bot認證資訊：
   ```
   CHANNEL_ACCESS_TOKEN=你的頻道存取權杖
   CHANNEL_SECRET=你的頻道密鑰
   ```

## 本地測試

執行以下命令啟動本地測試伺服器：
```bash
python debug_local_test.py
```

測試伺服器會模擬LINE平台發送webhook事件到您的Lambda函數，便於本地除錯。

## 部署到AWS Lambda

1. 將程式碼打包成ZIP檔案：
   ```bash
   zip -r lambda_package.zip lambda_function.py
   ```

2. 在AWS Lambda控制台上傳ZIP檔案，或使用AWS CLI部署：
   ```bash
   aws lambda update-function-code --function-name YourLambdaFunctionName --zip-file fileb://lambda_package.zip
   ```

3. 設定環境變數：
   - CHANNEL_ACCESS_TOKEN
   - CHANNEL_SECRET

4. 將Lambda函數的API Gateway端點設為LINE Bot的webhook URL。

## 功能說明

當用戶發送訊息給LINE Bot時，系統會：
1. 驗證請求簽名
2. 獲取用戶資料（名稱等）
3. 回覆一則帶有用戶名稱的個人化訊息

## 常見問題排解

- **無效簽名錯誤**：確認您的CHANNEL_SECRET環境變數設置正確
- **API錯誤**：檢查CHANNEL_ACCESS_TOKEN是否有效且未過期
- **本地測試失敗**：確保您已安裝所有依賴套件並正確設置.env檔案

## 專案架構

- `lambda_function.py`：主要Lambda處理程式
- `debug_local_test.py`：本地測試伺服器
- `.env`：本地開發環境變數（不包含在儲存庫中）

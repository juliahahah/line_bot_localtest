# DEMO輸出格式 (user name + "自動回覆訊息"+ 重複使用者輸出的資訊)

![image](https://github.com/user-attachments/assets/78cfdd02-c0e5-49c5-be8c-55f6d8ef89db)


# LINE Bot Lambda Function

這個專案包含一個AWS Lambda函數，用於處理LINE Bot的webhook請求和回覆訊息。

## 功能特點

- 接收並處理來自LINE平台的webhook事件
- 驗證請求簽名以確保安全性
- 支援本地測試環境（使用.env檔案）
- 獲取用戶資料並以個人化方式回覆
- 整合AWS Bedrock Agent進行AI回覆

## 系統需求

- Python 3.6+
- LINE Bot SDK v3
- boto3 (AWS SDK)
- dotenv (用於本地開發)
- 註冊ngrok

## 安裝指南

1. 克隆此儲存庫：
   ```bash
   git clone <儲存庫URL>
   cd line_bot_localtest
   ```

2. 安裝依賴套件：
   ```bash
   pip install line-bot-sdk boto3 python-dotenv
   ```

3. 創建.env檔案並設定您的認證資訊：
   ```
   # LINE Bot 設定
   CHANNEL_ACCESS_TOKEN=你的頻道存取權杖
   CHANNEL_SECRET=你的頻道密鑰
   
   # AWS Bedrock 設定
   AWS_REGION=us-east-1
   BEDROCK_AGENT_ID=你的Bedrock代理ID
   BEDROCK_AGENT_ALIAS_ID=你的Bedrock代理別名ID
   ```

## AWS認證配置

如果要在本地運行並訪問AWS服務，請確保您已配置好AWS認證：

1. 使用AWS CLI配置認證：
   ```bash
   aws configure
   ```

2. 或者在環境變數中設置：
   ```
   AWS_ACCESS_KEY_ID=你的訪問密鑰
   AWS_SECRET_ACCESS_KEY=你的秘密訪問密鑰
   ```

## 本地測試

執行以下命令啟動本地測試伺服器：
```bash
python debug_local_test.py
```

測試伺服器會模擬LINE平台發送webhook事件到您的Lambda函數，便於本地除錯。

## 雙重回覆機制

當用戶發送訊息時，系統會回覆兩條訊息：
1. 初始回覆：確認收到訊息，格式為 "{用戶名} ({用戶ID}) 呀哈~等等唷!我在幫你分析, {用戶輸入}"
2. AI分析回覆：來自AWS Bedrock Agent的分析結果

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
<<<<<<< HEAD
   - AWS_REGION
   - BEDROCK_AGENT_ID
   - BEDROCK_AGENT_ALIAS_ID
=======
   - EXAMPLE
      # LINE 頻道訪問令牌
      CHANNEL_ACCESS_TOKEN = 'tmVirv6mNOrSUzdrIrrvJ61yErkjEbHbUsS07hn8WCwUkvpGIY7V9cHSESfhv95hYREcrlwifXJ/Yn4Dwi0LaTe7l45CKvSgfX1jFVfd11q70Sou47nMG+QKQUiNwWRkQge6ImvrHet2Cph5+ocCOwdB04t89/1O/w1cDnyilFU='
      # LINE 頻道密鑰
      CHANNEL_SECRET = 'd94056599e0bc1a71f3b006b4dd7bd58'
>>>>>>> 95f81bc657c05ae848d217a027f306aeaac6ff59

4. 確保Lambda函數有訪問AWS Bedrock的權限。

5. 將Lambda函數的API Gateway端點設為LINE Bot的webhook URL。

## 常見問題排解

- **無效簽名錯誤**：確認您的CHANNEL_SECRET環境變數設置正確
- **API錯誤**：檢查CHANNEL_ACCESS_TOKEN是否有效且未過期
- **Bedrock錯誤**：確保您的AWS認證有權訪問Bedrock服務，並檢查BEDROCK_AGENT_ID是否正確
- **本地測試失敗**：確保您已安裝所有依賴套件並正確設置.env檔案和AWS認證

## 專案架構

- `lambda_function.py`：主要Lambda處理程式
- `debug_local_test.py`：本地測試伺服器
- `.env`：本地開發環境變數（不包含在儲存庫中）
- `.env-example`：環境變數範例檔案

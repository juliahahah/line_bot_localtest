# LINE Bot Lambda 功能

這是一個運行在 AWS Lambda 上的 LINE Bot，可以透過本地測試環境進行開發。

## 設置步驟

1. 安裝必要的套件：
   ```bash
   pip install line-bot-sdk flask python-dotenv
   ```

2. 設置環境變數：
   - 複製 `.env.template` 並重新命名為 `.env`
   - 填入你的 LINE Channel Access Token 和 Channel Secret

   ```
   CHANNEL_ACCESS_TOKEN=你的LINE頻道存取令牌
   CHANNEL_SECRET=你的LINE頻道密碼
   ```

3. 啟動本地測試伺服器：
   ```bash
   python debug_local_test.py
   ```

4. 使用 ngrok 將本地伺服器暴露至網際網路：
   ```bash
   ngrok http 5000
   ```

5. 在 LINE Developers 控制台設置 Webhook URL：
   ```
   https://你的ngrok網址/callback
   ```

## 環境變數問題排查

如果 `debug_local_test.py` 顯示找不到環境變數：

1. 確認 `.env` 檔案存在且包含正確的設置
2. 確認 `.env` 檔案與 `debug_local_test.py` 在相同目錄
3. 手動設置環境變數：

   在 Windows:
   ```
   set CHANNEL_ACCESS_TOKEN=你的LINE頻道存取令牌
   set CHANNEL_SECRET=你的LINE頻道密碼
   ```

   在 Mac/Linux:
   ```
   export CHANNEL_ACCESS_TOKEN=你的LINE頻道存取令牌
   export CHANNEL_SECRET=你的LINE頻道密碼
   ```

## 部署到 AWS Lambda

1. 將所有檔案打包成 ZIP
2. 在 Lambda 控制台上傳 ZIP 檔
3. 設置環境變數 `CHANNEL_ACCESS_TOKEN` 和 `CHANNEL_SECRET`
4. 設置 API Gateway 觸發器，並將 URL 設為 LINE Bot 的 Webhook URL
#   l i n e _ b o t _ l o c a l t e s t  
 #   l i n e _ b o t _ l o c a l t e s t  
 
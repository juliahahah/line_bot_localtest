import os
import sys

# 優先處理環境變數
print("檢查環境變數...")
try:
    from dotenv import load_dotenv
    print("找到 dotenv 模組，正在加載環境變數...")
    load_dotenv(verbose=True)
    
    # 顯示環境變數（隱藏部分值以保護敏感資訊）
    channel_token = os.environ.get('CHANNEL_ACCESS_TOKEN')
    channel_secret = os.environ.get('CHANNEL_SECRET')
    
    if channel_token:
        masked_token = channel_token[:5] + "..." + channel_token[-5:] if len(channel_token) > 10 else "已設置但太短"
        print(f"已找到 CHANNEL_ACCESS_TOKEN: {masked_token}")
    else:
        print("警告: CHANNEL_ACCESS_TOKEN 未設置")
        print("請檢查您的 .env 檔案是否存在且包含 CHANNEL_ACCESS_TOKEN=您的LINE令牌")
        print("或者直接在終端機中設置環境變數:")
        if sys.platform.startswith('win'):
            print("  set CHANNEL_ACCESS_TOKEN=您的LINE令牌")
        else:
            print("  export CHANNEL_ACCESS_TOKEN=您的LINE令牌")
        
    if channel_secret:
        masked_secret = channel_secret[:3] + "..." + channel_secret[-3:] if len(channel_secret) > 6 else "已設置但太短"
        print(f"已找到 CHANNEL_SECRET: {masked_secret}")
    else:
        print("警告: CHANNEL_SECRET 未設置")
        print("請檢查您的 .env 檔案是否存在且包含 CHANNEL_SECRET=您的LINE密鑰")
        print("或者直接在終端機中設置環境變數:")
        if sys.platform.startswith('win'):
            print("  set CHANNEL_SECRET=您的LINE密鑰")
        else:
            print("  export CHANNEL_SECRET=您的LINE密鑰")
        
except ImportError:
    print("錯誤: 找不到 dotenv 模組。請運行 'pip install python-dotenv' 安裝它。")
    
# 檢查 Flask
print("\n檢查 Flask...")
try:
    from flask import Flask
    print("成功: 找到 Flask 模組")
except ImportError:
    print("錯誤: 找不到 Flask 模組。請運行 'pip install flask' 安裝它。")

# 檢查 LINE Bot SDK
print("\n檢查 LINE Bot SDK...")
try:
    import linebot
    print(f"成功: 找到 LINE Bot SDK 模組，版本 {linebot.__version__}")
except ImportError:
    print("錯誤: 找不到 LINE Bot SDK。請運行 'pip install line-bot-sdk' 安裝它。")
except AttributeError:
    print("成功: 找到 LINE Bot SDK 模組，但無法確定版本")

# 嘗試導入主程式
print("\n嘗試導入 Lambda 函數...")
try:
    import lambda_function
    print("成功: 導入 lambda_function.py")
    
    # 檢查必要的函數和變數是否存在
    if hasattr(lambda_function, 'lambda_handler'):
        print("成功: 找到 lambda_handler 函數")
    else:
        print("錯誤: lambda_function.py 中缺少 lambda_handler 函數")
        
except Exception as e:
    print(f"錯誤: 導入 lambda_function.py 時出錯: {str(e)}")
    import traceback
    print(traceback.format_exc())

# 嘗試運行本地測試伺服器
print("\n嘗試運行本地測試伺服器...")
try:
    # 啟動本地伺服器的代碼
    from flask import Flask, request, abort
    import logging
    from lambda_function import lambda_handler, CHANNEL_ACCESS_TOKEN, CHANNEL_SECRET

    # 設置日誌
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    # 檢查環境變量
    if not CHANNEL_ACCESS_TOKEN or not CHANNEL_SECRET:
        print("錯誤: 請設置 LINE Bot 的環境變量")
        print("您可以透過以下方式設置環境變量：")
        print("1. 創建 .env 文件並填入以下內容:")
        print("   CHANNEL_ACCESS_TOKEN=您的訪問令牌")
        print("   CHANNEL_SECRET=您的頻道密碼")
        print("2. 或在命令行中運行:")
        if sys.platform.startswith('win'):
            print("   在 Windows 上執行：")
            print("   set CHANNEL_ACCESS_TOKEN=您的訪問令牌")
            print("   set CHANNEL_SECRET=您的頻道密碼")
        else:
            print("   在 Linux/Mac 上執行：")
            print("   export CHANNEL_ACCESS_TOKEN=您的訪問令牌")
            print("   export CHANNEL_SECRET=您的頻道密碼")
        sys.exit(1)

    # 創建 Flask 應用
    app = Flask(__name__)
    
    @app.route("/callback", methods=['POST'])
    def callback():
        # 獲取 X-Line-Signature 標頭值
        signature = request.headers['X-Line-Signature']
        
        # 獲取請求體
        body = request.get_data(as_text=True)
        logger.info("Request body: " + body)
        
        # 創建類似 Lambda 事件的對象
        lambda_event = {
            'body': body,
            'headers': {
                'X-Line-Signature': signature
            }
        }
        
        # 調用 Lambda 處理函數
        response = lambda_handler(lambda_event, None)
        
        # 處理響應
        status_code = response.get('statusCode', 200)
        if status_code != 200:
            logger.error(f"處理失敗: {response.get('body')}")
            abort(status_code)
        
        return 'OK'
    
    @app.route("/", methods=['GET'])
    def home():
        return """
        <html>
            <head>
                <title>LINE Bot 本地測試服務器</title>
                <style>
                    body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                    h1 { color: #4CAF50; }
                    code { background-color: #f0f0f0; padding: 2px 5px; border-radius: 3px; }
                    .container { border: 1px solid #ddd; padding: 20px; border-radius: 5px; }
                </style>
            </head>
            <body>
                <h1>LINE Bot 本地測試服務器</h1>
                <div class="container">
                    <p>您的 LINE Bot 本地測試服務器已啟動！</p>
                    <p>Webhook URL: <code>https://您的ngrok網址/callback</code></p>
                    <p>使用 ngrok 將此本地服務暴露到互聯網，以便 LINE 平台可以訪問它：</p>
                    <p><code>ngrok http 5000</code></p>
                </div>
            </body>
        </html>
        """

    # 啟動服務器
    print("一切就緒！正在啟動本地 LINE Bot 測試服務器...")
    print("請在另一個命令視窗執行 'ngrok http 5000' 創建公共 URL")
    print("然後將 https://您的ngrok網址/callback 設置為 LINE 的 Webhook URL")
    app.run(host='0.0.0.0', port=5000, debug=True)
    
except Exception as e:
    print(f"錯誤: 啟動本地測試伺服器時出錯: {str(e)}")
    import traceback
    print(traceback.format_exc())

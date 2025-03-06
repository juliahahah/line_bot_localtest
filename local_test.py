# import json
# import os
# import sys
# from flask import Flask, request, abort
# import logging

# # 導入 Lambda 函數 (修改：使用新版 linebot.V3)
# from lambda_function_v3 import handler, line_bot_api, CHANNEL_ACCESS_TOKEN, CHANNEL_SECRET

# # 設置日誌
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(__name__)

# # 檢查環境變量
# if not CHANNEL_ACCESS_TOKEN or not CHANNEL_SECRET:
#     logger.error("請設置 LINE Bot 的環境變量")
#     logger.error("您可以透過以下命令設置環境變量：")
#     if sys.platform.startswith('win'):
#         logger.error("在 Windows 上執行：")
#         logger.error("set CHANNEL_ACCESS_TOKEN=你的訪問令牌")
#         logger.error("set CHANNEL_SECRET=你的頻道密碼")
#     else:
#         logger.error("在 Linux/Mac 上執行：")
#         logger.error("export CHANNEL_ACCESS_TOKEN=你的訪問令牌")
#         logger.error("export CHANNEL_SECRET=你的頻道密碼")
#     sys.exit(1)

# # 創建 Flask 應用
# app = Flask(__name__)

# @app.route("/callback", methods=['POST'])
# def callback():
#     """處理 LINE Webhook 回調"""
#     # 獲取 X-Line-Signature 標頭值
#     signature = request.headers['X-Line-Signature']
    
#     # 獲取請求體
#     body = request.get_data(as_text=True)
#     logger.info("Request body: " + body)
    
#     # 創建類似 Lambda 事件的對象
#     lambda_event = {
#         'body': body,
#         'headers': {
#             'X-Line-Signature': signature
#         }
#     }
    
#     # 調用新版 Lambda 處理函數 (修改：使用 handler)
#     response = handler(lambda_event, None)
    
#     # 處理響應
#     status_code = response.get('statusCode', 200)
#     if status_code != 200:
#         logger.error(f"處理失敗: {response.get('body')}")
#         abort(status_code)
    
#     return 'OK'

# @app.route("/", methods=['GET'])
# def home():
#     """提供簡單的首頁"""
#     return """
#     <html>
#         <head>
#             <title>LINE Bot 本地測試服務器</title>
#             <style>
#                 body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
#                 h1 { color: #4CAF50; }
#                 code { background-color: #f0f0f0; padding: 2px 5px; border-radius: 3px; }
#                 .container { border: 1px solid #ddd; padding: 20px; border-radius: 5px; }
#             </style>
#         </head>
#         <body>
#             <h1>LINE Bot 本地測試服務器</h1>
#             <div class="container">
#                 <p>您的 LINE Bot 本地測試服務器已啟動！</p>
#                 <p>Webhook URL: <code>https://您的ngrok網址/callback</code></p>
#                 <p>使用 ngrok 將此本地服務暴露到互聯網，以便 LINE 平台可以訪問它：</p>
#                 <p><code>ngrok http 5000</code></p>
#             </div>
#         </body>
#     </html>
#     """

# if __name__ == "__main__":
#     logger.info("啟動本地 LINE Bot 測試服務器...")
#     logger.info("請使用 ngrok http 5000 創建公共 URL")
#     logger.info("然後將 https://您的ngrok網址/callback 設置為 LINE 的 Webhook URL")
#     app.run(host='0.0.0.0', port=5000, debug=True)

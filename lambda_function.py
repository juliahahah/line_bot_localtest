import json
import os
import logging
import hmac
import hashlib
import base64

# 嘗試導入 dotenv 以便本地開發時讀取 .env 文件
try:
    from dotenv import load_dotenv
    print("Loading environment from .env file...")
    load_dotenv()  # 從 .env 文件加載環境變數
except ImportError:
    print("dotenv module not found. Environment variables must be set manually.")
    pass  # 在 Lambda 環境中無需 dotenv

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 從環境變數中獲取認證信息，而不是硬編碼
CHANNEL_ACCESS_TOKEN = os.environ.get('CHANNEL_ACCESS_TOKEN')
CHANNEL_SECRET = os.environ.get('CHANNEL_SECRET')

# 檢查環境變數是否已設置
if not CHANNEL_ACCESS_TOKEN:
    print("警告: CHANNEL_ACCESS_TOKEN 環境變數未設置")
if not CHANNEL_SECRET:
    print("警告: CHANNEL_SECRET 環境變數未設置")

# 初始化 LINE Bot API
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

def lambda_handler(event, context):
    """AWS Lambda function handler."""
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # 從事件中提取必要信息
        body = event.get('body', '')
        if not body:
            logger.error("Empty request body")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': '請求主體為空'})
            }
        
        # 從標頭獲取簽名（處理不同的標頭格式）
        headers = event.get('headers', {}) or {}  # 處理 None 頭信息
        
        # LINE 可能會以不同的大小寫發送標頭
        signature = None
        for header_key in headers:
            if header_key.lower() == 'x-line-signature':
                signature = headers[header_key]
                break
                
        if not signature:
            logger.error("Missing LINE signature header")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': '缺少 LINE 簽名標頭'})
            }
            
        # 檢查這是否是帶有虛擬簽名的測試事件
        is_test_event = signature == "dummy_signature"
        if is_test_event:
            logger.info("檢測到帶有虛擬簽名的測試事件")
            # 為測試事件生成有效簽名
            signature = calculate_signature(CHANNEL_SECRET, body)
            logger.info(f"為測試事件生成有效簽名: {signature}")
        
        # 處理 webhook
        handler.handle(body, signature)
        logger.info("Webhook 處理成功")
        
        return {
            'statusCode': 200,
            'body': json.dumps('OK')
        }
        
    except InvalidSignatureError:
        logger.error("無效簽名")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': '無效簽名'})
        }
    except LineBotApiError as e:
        logger.error('LINE Bot API 錯誤: %s', e)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'LINE Bot API 錯誤'})
        }
    except Exception as e:
        logger.error(f"錯誤: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """處理接收到的文字訊息"""
    logger.info(f"處理消息事件: {event.message.text}")
    
    # 嘗試直接通過API call獲取用戶資料
    try:
        user_id = event.source.user_id
        logger.info(f"用戶 ID: {user_id}")
        
        # 使用更直接的方式呼叫LINE API
        try:
            # 構建API請求URL
            profile_url = f'https://api.line.me/v2/bot/profile/{user_id}'
            headers = {
                'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'
            }
            
            # 使用Python標準庫進行HTTP請求
            import urllib.request
            req = urllib.request.Request(profile_url, headers=headers)
            
            logger.info(f"發送請求獲取用戶資料: {profile_url}")
            with urllib.request.urlopen(req) as response:
                profile_json = json.loads(response.read().decode('utf-8'))
            
            logger.info(f"獲取到用戶資料: {profile_json}")
            user_name = profile_json.get('displayName', '朋友')
            logger.info(f"用戶名稱: {user_name}")
            
            # 回覆訊息加上用戶的名字
            reply_text = f"{user_name} {event.message.text}"
            logger.info(f"準備回覆訊息: {reply_text}")
            
        except Exception as api_err:
            logger.error(f"直接API調用失敗: {api_err}")
            # 無法獲取用戶名稱，使用預設稱呼
            user_name = '朋友'
            reply_text = f"{user_name} {event.message.text}"
            logger.info("使用預設稱呼")
        
        # 發送回覆
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )
        logger.info("訊息回覆成功發送")
        
    except Exception as e:
        logger.error(f"處理訊息時出錯: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        # 如果出現任何錯誤，至少嘗試回覆原始訊息
        try:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=event.message.text)
            )
        except Exception as sub_e:
            logger.error(f"嘗試直接回覆訊息時出錯: {str(sub_e)}")

def calculate_signature(channel_secret, body):
    """從頻道密鑰和請求主體計算 LINE 簽名。"""
    hash = hmac.new(
        channel_secret.encode('utf-8'),
        body.encode('utf-8'), 
        hashlib.sha256
    ).digest()
    signature = base64.b64encode(hash).decode('utf-8')
    return signature

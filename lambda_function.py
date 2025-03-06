import json
import os
import logging
import hmac
import hashlib
import base64
import boto3

# 嘗試導入 dotenv 以便本地開發時讀取 .env 文件
try:
    from dotenv import load_dotenv
    print("Loading environment from .env file...")
    load_dotenv()  # 從 .env 文件加載環境變數
except ImportError:
    print("dotenv module not found. Environment variables must be set manually.")
    pass  # 在 Lambda 環境中無需 dotenv

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)
# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 從環境變數中獲取認證信息，而不是硬編碼
CHANNEL_ACCESS_TOKEN = os.environ.get('CHANNEL_ACCESS_TOKEN')
CHANNEL_SECRET = os.environ.get('CHANNEL_SECRET')
# AWS Bedrock 設定
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
BEDROCK_AGENT_ID = os.environ.get('BEDROCK_AGENT_ID')
BEDROCK_AGENT_ALIAS_ID = os.environ.get('BEDROCK_AGENT_ALIAS_ID', 'TSTALIASID')

# 檢查環境變數是否已設置
if not CHANNEL_ACCESS_TOKEN:
    print("警告: CHANNEL_ACCESS_TOKEN 環境變數未設置")
if not CHANNEL_SECRET:
    print("警告: CHANNEL_SECRET 環境變數未設置")
if not BEDROCK_AGENT_ID:
    print("警告: BEDROCK_AGENT_ID 環境變數未設置")

# 初始化 LINE Bot API
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
api_client = ApiClient(configuration)
line_bot_api = MessagingApi(api_client)
handler = WebhookHandler(CHANNEL_SECRET)

# 初始化 AWS Bedrock client
try:
    bedrock_agent_runtime = boto3.client(
        service_name='bedrock-agent-runtime',
        region_name=AWS_REGION
    )
    print(f"成功初始化 AWS Bedrock Agent Runtime")
except Exception as e:
    print(f"初始化 AWS Bedrock 時出錯: {str(e)}")
    bedrock_agent_runtime = None

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

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    """處理接收到的文字訊息"""
    logger.info(f"處理消息事件: {event.message.text}")
    
    try:
        user_id = event.source.user_id
        logger.info(f"用戶 ID: {user_id}")
        
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
            
            # 修改回覆文本格式
            initial_reply_text = f"{user_name} ({user_id}) 呀哈~等等唷!我在幫你分析, {event.message.text}"
            logger.info(f"準備初始回覆訊息: {initial_reply_text}")
            
        except Exception as api_err:
            logger.error(f"直接API調用失敗: {api_err}")
            user_name = '朋友'
            initial_reply_text = f"{user_name} ({user_id}) 呀哈~等等唷!我在幫你分析, {event.message.text}"
            logger.info("使用預設稱呼")
        
        # 發送初始回覆
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=initial_reply_text)]
            )
        )
        logger.info("初始訊息回覆成功發送")
        
        # 呼叫 AWS Bedrock Agent 取得分析回覆
        ai_reply = get_bedrock_agent_response(event.message.text, user_id)
        
        # 使用 push message 發送 AI 回覆 (因為 reply_token 只能用一次)
        send_push_message(user_id, ai_reply)
        logger.info("AI 分析回覆成功發送")
        
    except Exception as e:
        logger.error(f"處理訊息時出錯: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        try:
            # fallback using default values if variables are missing
            fallback_name = locals().get('user_name', '朋友')
            fallback_id = locals().get('user_id', '未知ID')
            fallback_text = f"{fallback_name} ({fallback_id}) 呀哈~等等唷!我在幫你分析, {event.message.text}"
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=fallback_text)]
                )
            )
        except Exception as sub_e:
            logger.error(f"嘗試直接回覆訊息時出錯: {str(sub_e)}")

def get_bedrock_agent_response(user_message, user_id):
    """呼叫 AWS Bedrock Agent 獲取回覆"""
    try:
        if not bedrock_agent_runtime or not BEDROCK_AGENT_ID:
            return "目前無法使用 AI 分析功能，請稍後再試。"
        
        logger.info(f"呼叫 AWS Bedrock Agent，使用者訊息: {user_message}")
        
        response = bedrock_agent_runtime.invoke_agent(
            agentId=BEDROCK_AGENT_ID,
            agentAliasId=BEDROCK_AGENT_ALIAS_ID,
            sessionId=f"line-session-{user_id}",
            inputText=user_message
        )
        
        # 解析回覆
        completion = ""
        for event in response.get('completion', []):
            chunk = event.get('chunk', {})
            if 'bytes' in chunk:
                completion += chunk['bytes'].decode('utf-8')
        
        if not completion:
            completion = "很抱歉，我無法理解您的問題。請再試一次。"
            
        logger.info(f"從 Bedrock Agent 獲得的回覆: {completion}")
        return completion
        
    except Exception as e:
        logger.error(f"呼叫 AWS Bedrock 時出錯: {str(e)}")
        return f"分析過程中發生錯誤，請稍後再試。錯誤: {str(e)[:100]}..."

def send_push_message(user_id, message):
    """發送推送訊息給用戶"""
    try:
        from linebot.v3.messaging import PushMessageRequest
        
        line_bot_api.push_message(
            PushMessageRequest(
                to=user_id,
                messages=[TextMessage(text=message)]
            )
        )
        return True
    except Exception as e:
        logger.error(f"發送推送訊息時出錯: {str(e)}")
        return False

def calculate_signature(channel_secret, body):
    """從頻道密鑰和請求主體計算 LINE 簽名。"""
    hash = hmac.new(
        channel_secret.encode('utf-8'),
        body.encode('utf-8'), 
        hashlib.sha256
    ).digest()
    signature = base64.b64encode(hash).decode('utf-8')
    return signature


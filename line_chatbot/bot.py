from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('DustSensorTable')

app = Flask(__name__)

line_bot_api = LineBotApi('YOUR_CHANNEL_ACCESS_TOKEN')
handler = WebhookHandler('YOUR_CHANNEL_SECRET')

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print(event)
    if event.message.text == "อยากรู้ค่า PM2.5 ล่าสุด":
        sensor_id = 'DustSensor001'
        pm2_5 = get_latest_data_from_dynamodb(sensor_id)
        if pm2_5:
            status = get_status(pm2_5)
            reply_msg = f'ค่า PM2.5 ล่าสุดในกรุงเทพอยู่ที่ {pm2_5} มคก./ลบ.ม ({status})'
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_msg))

def get_status(pm2_5):
    status = ""
    if 0 <= pm2_5 <= 25:
        status = "ดีมาก"
    elif 26 <= pm2_5 <= 37:
        status = "ดี"
    elif 38 <= pm2_5 <= 50:
        status = "ปานกลาง"
    elif 51 <= pm2_5 <= 90:
        status = "เริ่มมีผลกระทบสุขภาพ"
    elif pm2_5 > 91:
        status = "มีผลกระทบสุขภาพ"
    return status

def get_latest_data_from_dynamodb(sensor_id):
    response = table.query(
        ScanIndexForward=False,
        Limit=1,
        KeyConditionExpression=Key('DustSensorID').eq(sensor_id)
    )

    items = response['Items']
    print('found:', len(items))
    output = None
    if len(items) > 0:
        output = int(items[0]['payload']['PM2.5'])
    return output

if __name__ == "__main__":
    app.run()
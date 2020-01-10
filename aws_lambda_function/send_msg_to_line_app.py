import json
import boto3
from boto3.dynamodb.conditions import Key
from botocore.vendored import requests

def lambda_handler(event, context):
    if 'user_ids_dict' not in event:
        return 'User ids are not speci'
    user_ids_dict = event['user_ids_dict']
    
    dust_sensor_id = "DustSensor001"
    pm2_5_dict = get_data_from_dynamodb(dust_sensor_id)
    responses = []
    for name, user_id in user_ids_dict.items():
        response = send_msg(name, user_id, pm2_5_dict['avg'])
        responses.append(response.status_code)
    
    return {
        'statusCode': response.status_code,
        'body': json.dumps(f'Sending successful {len(responses)} people')
    }

def get_data_from_dynamodb(dust_sensor_id):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('DustSensorTable')
    response = table.query(
        KeyConditionExpression=Key('DustSensorID').eq(dust_sensor_id)
    )

    items = response['Items']
    print('found:', len(items))

    result = {}
    if len(items) > 0:
        pm2_5_list = []
        for item in items:
            print(item)
            pm2_5_list.append(int(item['payload']['PM2.5']))

        avg = sum(pm2_5_list) / len(pm2_5_list)
        result['avg'] = round(avg, 3)
        result['latest'] = items[-1]['payload']['PM2.5']
        print('avg=', result['avg'])
        print('latest=', result['latest'])
    return result

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

def send_msg(name, user_id, pm2_5):
    status = get_status(pm2_5)
    text = f"สวัสดีคุณ {name}\nชั่วโมงนี้ค่าเฉลี่ย PM2.5 ในกรุงเทพอยู่ที่ {pm2_5} มคก./ลบ.ม ({status})"
    data = {
        "to": user_id,
        "messages": [
            {
                "type": "text",
                "text": text
            }
        ]
    }

    URL = 'https://api.line.me/v2/bot/message/push'
    channel_access_token = 'xxxxx'

    headers = {
        "Authorization": f"Bearer {channel_access_token}",
        "Content-Type": "application/json"
    }

    r = requests.post(URL, json = data, headers = headers)
    print('response:', r)
    return r
import os
import requests
import json
import logging

def chat(userId, requestContent):
    openaiChatUrl = 'https://api.openai.com/v1/chat/completions'
    api_key = os.getenv('OPENAI_API_KEY')
    headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_key}',
    }
    data = {
        'model': 'gpt-3.5-turbo',
        'messages': [
            {'role': 'system', 'content': '你是一個只會說中文和說話極簡的戀人.'},
            {'role': 'user', 'content': requestContent}
        ],
        'temperature': 0.5
    }
    response = requests.post(openaiChatUrl, headers=headers, json=data)

    if response.status_code == 200:
        data = response.json()
        print("API Response:", data['choices'][0]['message']['content'])
        content = data['choices'][0]['message']['content']
        LineChatRequest(userId, content)
    else:
        print("API Request Failed with Status Code:", response.status_code)


def LineChatRequest(userId, content):
    api_url = 'https://api.line.me/v2/bot/message/push'
    access_token = os.getenv('LINE_ACCESS_TOKEN')
    messages = {
        "to": userId,
        "messages": [
            {
                "type": "text",
                "text": content
            }
        ]
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.post(api_url, data= json.dumps(messages), headers = headers)


def lambda_handler(event, context):
    # TODO implement
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    jsonStr = event['body']
    jsonData = json.loads(jsonStr)
    print(jsonData['events'])
    logger.info(jsonData['events'][0]['message']['text'])
    text = jsonData['events'][0]['message']['text']
    userId = jsonData['events'][0]['source']['userId']
    
    chat(userId, text)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }


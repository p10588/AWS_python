import hashlib
import hmac
import datetime
import os 
import requests

access_key = os.getenv('AWS_ACCESS_KEY')
secret_key = os.getenv('AWS_SECRET_KEY')
region = 'ap-northeast-1'
service = 's3'
bucket_name = 'chi-public-bucket'  
object_key = '123123.png'  
host = f'{bucket_name}.s3.amazonaws.com'
request_date = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')

with open('/Users/chain-mac/Downloads/AAAA.png', 'rb') as file:
    file_data = file.read()
    payload_hash = hashlib.sha256(file_data).hexdigest() # 進行sha256資料加密

# 設定 Content-type
content_type = 'image/png'

# 建立請求規範
canonical_headers = f'host:{host}\nx-amz-date:{request_date}\n' 
signed_headers = 'host;x-amz-date'
canonical_request = f'PUT\n/{object_key}\n\n{canonical_headers}\n{signed_headers}\n{payload_hash}'

# 字串簽名
algorithm = 'AWS4-HMAC-SHA256'
credential_scope = f'{request_date[0:8]}/{region}/{service}/aws4_request'
string_to_sign = f'{algorithm}\n{request_date}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode()).hexdigest()}'

# 產生加密簽名
def sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

date_key = sign(('AWS4' + secret_key).encode('utf-8'), request_date[0:8])
region_key = sign(date_key, region)
service_key = sign(region_key, service)
signing_key = sign(service_key, 'aws4_request')
signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

# auth header
authorization_header = f'{algorithm} Credential={access_key}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}'

# HTTP header 
headers = {
    'Authorization': authorization_header,
    'x-amz-date': request_date,
    'Host': host,
    'x-amz-content-sha256': payload_hash,
}

print(headers)

url = f'https://{host}/{object_key}'
response = requests.put(url, headers=headers ,data=file_data)

# handle response
if response.status_code == 200:
    print('Upload success')
else:
    print('Upload fail, status code:', response.status_code, ' error message:', response.content)
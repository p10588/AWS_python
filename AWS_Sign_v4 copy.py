import hashlib
import hmac
import datetime
import requests
import os

access_key = os.getenv('AWS_ACCESS_KEY')
secret_key = os.getenv('AWS_SECRET_KEY')
region = 'ap-northeast-1'
service = 's3'
bucket_name = 'chi-public-bucket'  # 替换为实际的存储桶名称
object_key = '1231235555.png'  # 替换为实际的对象路径
host = f'{bucket_name}.s3.amazonaws.com'
request_date = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')

# 读取要上传的文件
with open('/Users/chain-mac/Downloads/AAAA.png', 'rb') as file:
    file_data = file.read()
    payload_hash = hashlib.sha256(file_data).hexdigest()

# 设置 ACL 权限和 Content-Type
acl = 'public-read'
content_type = 'image/png'

# 构建规范请求
canonical_headers = f'host:{host}\nx-amz-date:{request_date}\n'
signed_headers = 'host;x-amz-date'
canonical_request = f'PUT\n/{object_key}\n\n{canonical_headers}\n{signed_headers}\n{payload_hash}'

# 构建字符串签名
algorithm = 'AWS4-HMAC-SHA256'
credential_scope = f'{request_date[0:8]}/{region}/{service}/aws4_request'
string_to_sign = f'{algorithm}\n{request_date}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode()).hexdigest()}'

# 生成签名
def sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

date_key = sign(('AWS4' + secret_key).encode('utf-8'), request_date[0:8])
region_key = sign(date_key, region)
service_key = sign(region_key, service)
signing_key = sign(service_key, 'aws4_request')
signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

# 包括签名在 Authorization 头部
authorization_header = f'{algorithm} Credential={access_key}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}'

# 构建 HTTP 请求头部
headers = {
    'Authorization': authorization_header,
    'x-amz-date': request_date,
    'Host': host,
    'x-amz-content-sha256': payload_hash,
    'Content-Type': content_type,
}

# 发送 PUT 请求以上传文件
url = f'https://{host}/{object_key}'
response = requests.put(url, headers=headers, data=file_data)

# 处理响应
if response.status_code == 200:
    print('文件上传成功')
else:
    print('文件上传失败，状态码:', response.status_code, response.content)

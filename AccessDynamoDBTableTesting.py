import boto3


def lambda_handler(event, context) :
    dynamodb = boto3.client('dynamodb')
    table_name = ""
    key = ""
    try:
        response = dynamodb.get_item(
            TableName = table_name,
            Key = key
        )

        #item = response.

        return {

        }
    except Exception as e:
        return {
            'statusCode' : 500,
            'body' : str(e)
        }


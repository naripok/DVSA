import boto3
import json
import decimal
import os
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    # Helper class to convert a DynamoDB item to JSON.
    class DecimalEncoder(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, decimal.Decimal):
                if o % 1 > 0:
                    return float(o)
                else:
                    return int(o)
            return super(DecimalEncoder, self).default(o)

    keys = []
    total = 0
    cart = json.loads(event['body'])

    for item in cart:
        key = {
            'itemId': item,
            "category": "A"
        }
        keys.append(key)
    try:
        table = os.environ["INVENTORY_TABLE"]
        dynamodb = boto3.resource('dynamodb')
        response = dynamodb.meta.client.batch_get_item(
            RequestItems={
                table: {
                    'Keys': keys,
                    'AttributesToGet': ["itemId", "price"]
                }
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
        res = {"status": "err", "msg": "could not calculate cart"}
    else:
        items = response['Responses']
        for item in items[table]:
            total = total + (item["price"] * cart[item["itemId"]])
        res = {"status": "ok", "total": float(total)}

    return {
        'statusCode': 200,
        'body': json.dumps(res)
    }

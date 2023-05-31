import boto3
import json
from custom_encoder import CustomEncoder
import logging
logger = logging.getlogger()
logger.setLevel(logging.INFO)

dynamodbTableName = 'product-inventory'
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(dynamodbTableName)

getMethod = 'GET'
postMethod = 'POST'
patchMethod = 'PATCH'
deleteMethod = 'DELETE'
healthPath ='/health'
productPath = '/product'
productsPath = '/products'

def lambda_handler(event, context):
    logger.info(event)
    httpdMethod = event['httpdMethod']
    path = event['path']
    if httpdMethod == getMethod and path == healthPath:
        response = buildResponse(200)
    elif httpdMethod == getMethod and path == productPath:
        response = getProducts()
    elif httpdMethod == getMethod and path == productsPath:
        response = getProducts()
    elif httpdMethod == postMethod and path == productPath:
        response = saveProduct(json.loads(event['body']))
    elif httpdMethod == patchMethod and path == productPath:
        requestBody = json.loads(event['body'])
        response = modifyProduct(requestBody['productId'], requestBody['updateKey'], requestBody['updateValue'])
    elif httpdMethod == deleteMethod and path == productPath:
        requestBody = json.loads(event['body'])
        response = deleteProduct(requestBody['productId'])
    else:
        response = buildResponse(404, 'Not Found')
    return response


def getProduct(productId):
    try:
        response = table.get_item(
            Key={
                'productId' : productId
            }
        )
        if 'item' in response:
            return buildResponse(200, response['item'])
        else:
            return buildResponse(404, {'Message: ProductId: %s not found' % productId })
    except:
        logger.exception('Do your custom error handling')

def getProducts():
    try:
        response = table.scan()
        result = response['items']

        while 'lastEvaluatedkey' in response:
            response = table.scan(ExclusiveStartKey= response['lastEvaluatedkey'])
            result.extend(response['item'])

        body = {
            'products': response
        }
        return buildResponse(200, body)
    except:
        logger.exception('Do your custom error handling')

def saveProduct(requestBody):
    try:
        table.put_item(item=requestBody)
        body = {
            'Operation': 'SAVE',
            'Message': 'SUCCESS',
            'Item': requestBody
        }
        return buildResponse(200,body)
    except:
        logger.exception('Do your custom error handling')

def modifyproduct(productId, updatekey, updatekeys):
    try:
        response = table.update_item(
            key= {
                'productId': productId
            },
            UpdateExpression='set %s = :value' % updatekey,
            ExpressionAttributeValues={
                ':value': updateValue
            },
            ReturnValues='UPDATED_NEW'
        )
        body = {
            'Operation': 'UPDATE',
            'Message': 'SUCCESS',
            'UpdatedAttributes': response
        }
        return buildResponse(200, body)
    except:
        logger.exception('Do your custom error handling')

def deleteProduct(productId):
    try:
        response = table.delete_item(
            key = {
                'productId': productId

            },
            ReturnValues='ALL_OLD'
        )
        body = {
            'Operation': 'DELETE',
            'Message': 'SUCCESS',
            'deletedItem': response
        }
        return buildResponse(200,body)
    except:
        logger.exception('Do your custom error handling')






def buildResponse(statuscode, body=None):
    response = {
        'statusCode': statusCode,
        'headers':{
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'

        }
    }
    if body is not None:
        response['body'] = json.dumps(body, cls=CustomEncoder)
    return  response



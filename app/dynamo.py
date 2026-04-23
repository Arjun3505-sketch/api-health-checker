import boto3
import os
from dotenv import load_dotenv
from datetime import datetime, timezone
from boto3.dynamodb.conditions import Key

load_dotenv()

def get_dynamodb():
    return boto3.resource(
        'dynamodb',
        region_name=os.getenv('AWS_REGION'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )

def get_checks_table():
    return get_dynamodb().Table('api_health_checks')

def get_endpoints_table():
    return get_dynamodb().Table('api_endpoints')

def save_result(endpoint_url, status_code, response_time, status):
    table = get_checks_table()
    table.put_item(Item={
        'endpoint_url': endpoint_url,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'status_code': str(status_code) if status_code else 'N/A',
        'response_time': str(round(response_time, 2)),
        'status': status
    })

def get_history(endpoint_url, limit=20):
    table = get_checks_table()
    response = table.query(
        KeyConditionExpression=Key('endpoint_url').eq(endpoint_url),
        ScanIndexForward=False,
        Limit=limit
    )
    return response.get('Items', [])

def get_all_endpoints():
    table = get_endpoints_table()
    response = table.scan()
    return response.get('Items', [])

def add_endpoint(name, url):
    table = get_endpoints_table()
    table.put_item(Item={
        'endpoint_url': url,
        'name': name,
        'added_at': datetime.now(timezone.utc).isoformat()
    })

def delete_endpoint(url):
    table = get_endpoints_table()
    table.delete_item(Key={'endpoint_url': url})

def get_uptime_percentage(endpoint_url):
    records = get_history(endpoint_url, limit=20)
    if not records:
        return None
    up_count = sum(1 for r in records if r.get('status') == 'up')
    return round((up_count / len(records)) * 100, 1)
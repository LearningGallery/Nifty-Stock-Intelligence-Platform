"""
DynamoDB Repository
Generic CRUD operations for DynamoDB tables
"""
from typing import Dict, Any, List, Optional
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

from app.config import settings
from app.core.logging import logger
from app.core.exceptions import DynamoDBException


class DynamoDBRepository:
    """
    Base repository for DynamoDB operations
    """
    
    def __init__(self, table_name: str):
        self.dynamodb = boto3.resource('dynamodb', region_name=settings.AWS_REGION)
        self.table = self.dynamodb.Table(table_name)
        self.table_name = table_name
    
    async def get_item(self, key: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get single item by key"""
        try:
            response = self.table.get_item(Key=key)
            return response.get('Item')
        except ClientError as e:
            logger.error(f"DynamoDB get_item error: {e}")
            raise DynamoDBException(f"Failed to get item from {self.table_name}")
    
    async def put_item(self, item: Dict[str, Any]) -> None:
        """Insert or update item"""
        try:
            self.table.put_item(Item=item)
        except ClientError as e:
            logger.error(f"DynamoDB put_item error: {e}")
            raise DynamoDBException(f"Failed to put item to {self.table_name}")
    
    async def update_item(
        self,
        key: Dict[str, Any],
        update_expression: str,
        expression_values: Dict[str, Any],
        expression_names: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Update item with expression"""
        try:
            params = {
                'Key': key,
                'UpdateExpression': update_expression,
                'ExpressionAttributeValues': expression_values,
                'ReturnValues': 'ALL_NEW'
            }
            
            if expression_names:
                params['ExpressionAttributeNames'] = expression_names
            
            response = self.table.update_item(**params)
            return response.get('Attributes')
        except ClientError as e:
            logger.error(f"DynamoDB update_item error: {e}")
            raise DynamoDBException(f"Failed to update item in {self.table_name}")
    
    async def delete_item(self, key: Dict[str, Any]) -> None:
        """Delete item by key"""
        try:
            self.table.delete_item(Key=key)
        except ClientError as e:
            logger.error(f"DynamoDB delete_item error: {e}")
            raise DynamoDBException(f"Failed to delete item from {self.table_name}")
    
    async def query(
        self,
        key_condition_expression: Any,
        filter_expression: Optional[Any] = None,
        limit: Optional[int] = None,
        scan_forward: bool = True
    ) -> List[Dict[str, Any]]:
        """Query items with conditions"""
        try:
            params = {
                'KeyConditionExpression': key_condition_expression,
                'ScanIndexForward': scan_forward
            }
            
            if filter_expression:
                params['FilterExpression'] = filter_expression
            
            if limit:
                params['Limit'] = limit
            
            response = self.table.query(**params)
            return response.get('Items', [])
        except ClientError as e:
            logger.error(f"DynamoDB query error: {e}")
            raise DynamoDBException(f"Failed to query {self.table_name}")
    
    async def scan(
        self,
        filter_expression: Optional[Any] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Scan table (use sparingly)"""
        try:
            params = {}
            
            if filter_expression:
                params['FilterExpression'] = filter_expression
            
            if limit:
                params['Limit'] = limit
            
            response = self.table.scan(**params)
            return response.get('Items', [])
        except ClientError as e:
            logger.error(f"DynamoDB scan error: {e}")
            raise DynamoDBException(f"Failed to scan {self.table_name}")

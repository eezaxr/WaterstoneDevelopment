"""
Firebase Handler Module
Handles all Firebase Realtime Database operations using REST API
"""

import requests
import json
from typing import Optional, Dict, Any
import config


class FirebaseHandler:
    """Handles all Firebase Realtime Database interactions via REST API"""
    
    def __init__(self):
        """Initialize Firebase handler"""
        self.database_url = config.FIREBASE_DATABASE_URL.rstrip('/')
        self.secret = config.FIREBASE_SECRET
        self.initialized = True
    
    def _build_url(self, path: str) -> str:
        """
        Build a complete Firebase URL with authentication
        
        Args:
            path: Database path (e.g., 'users/123')
            
        Returns:
            Complete URL with auth parameter
        """
        path = path.strip('/')
        return f"{self.database_url}/{path}.json?auth={self.secret}"
    
    def get(self, path: str) -> Optional[Any]:
        """
        Get data from Firebase at specified path
        
        Args:
            path: Database path (e.g., 'users/123')
            
        Returns:
            Data at path or None if not found/error
        """
        if not self.initialized:
            return None
            
        try:
            url = self._build_url(path)
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None
    
    def set(self, path: str, data: Any) -> bool:
        """
        Set/overwrite data at specified path
        
        Args:
            path: Database path
            data: Data to write
            
        Returns:
            True if successful, False otherwise
        """
        if not self.initialized:
            return False
            
        try:
            url = self._build_url(path)
            response = requests.put(
                url,
                data=json.dumps(data),
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception:
            return False
    
    def update(self, path: str, data: Dict[str, Any]) -> bool:
        """
        Update specific fields at path (merges with existing data)
        
        Args:
            path: Database path
            data: Dictionary of fields to update
            
        Returns:
            True if successful, False otherwise
        """
        if not self.initialized:
            return False
            
        try:
            url = self._build_url(path)
            response = requests.patch(
                url,
                data=json.dumps(data),
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception:
            return False
    
    def delete(self, path: str) -> bool:
        """
        Delete data at specified path
        
        Args:
            path: Database path
            
        Returns:
            True if successful, False otherwise
        """
        if not self.initialized:
            return False
            
        try:
            url = self._build_url(url, timeout=10)
            response = requests.delete(url, timeout=10)
            response.raise_for_status()
            return True
        except Exception:
            return False
    
    def push(self, path: str, data: Any) -> Optional[str]:
        """
        Push data to a list (creates unique key)
        
        Args:
            path: Database path
            data: Data to push
            
        Returns:
            Generated key if successful, None otherwise
        """
        if not self.initialized:
            return None
            
        try:
            url = self._build_url(path)
            response = requests.post(
                url,
                data=json.dumps(data),
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            return result.get('name')
        except Exception:
            return None
    
    def query(self, path: str, order_by: str = "$key",
              limit_to_first: Optional[int] = None,
              limit_to_last: Optional[int] = None,
              start_at: Optional[str] = None,
              end_at: Optional[str] = None,
              equal_to: Optional[str] = None) -> Optional[Any]:
        """
        Query Firebase with filters
        
        Args:
            path: Database path
            order_by: Field to order by (use "$key" for keys, "$value" for values)
            limit_to_first: Limit to first N results
            limit_to_last: Limit to last N results
            start_at: Start at this value
            end_at: End at this value
            equal_to: Equal to this value
            
        Returns:
            Query results or None if error
        """
        if not self.initialized:
            return None
            
        try:
            url = self._build_url(path)
            params = []
            
            if order_by:
                params.append(f'orderBy="{order_by}"')
            if limit_to_first:
                params.append(f'limitToFirst={limit_to_first}')
            if limit_to_last:
                params.append(f'limitToLast={limit_to_last}')
            if start_at is not None:
                params.append(f'startAt="{start_at}"')
            if end_at is not None:
                params.append(f'endAt="{end_at}"')
            if equal_to is not None:
                params.append(f'equalTo="{equal_to}"')
            
            if params:
                url += '&' + '&'.join(params)
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None
    
    def exists(self, path: str) -> bool:
        """
        Check if data exists at path
        
        Args:
            path: Database path
            
        Returns:
            True if data exists, False otherwise
        """
        data = self.get(path)
        return data is not None
    
    def increment(self, path: str, amount: int = 1) -> bool:
        """
        Increment a numeric value at path
        
        Args:
            path: Database path
            amount: Amount to increment by (default: 1)
            
        Returns:
            True if successful, False otherwise
        """
        current = self.get(path)
        if current is None:
            current = 0
        elif not isinstance(current, (int, float)):
            return False
        
        return self.set(path, current + amount)
    
    def test_connection(self) -> bool:
        """
        Test Firebase connection
        
        Returns:
            True if connection successful, False otherwise
        """
        if not self.initialized:
            return False
            
        try:
            import datetime
            test_path = 'connection_test'
            test_data = {'test': 'connection', 'timestamp': str(datetime.datetime.now())}
            
            # Try to set data
            if not self.set(test_path, test_data):
                return False
            
            # Try to read it back
            result = self.get(test_path)
            
            # Clean up
            self.delete(test_path)
            
            return result and result.get('test') == 'connection'
                
        except Exception:
            return False


# Global singleton instance
firebase = FirebaseHandler()
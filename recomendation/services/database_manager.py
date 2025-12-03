"""
Database connection manager supporting both SQLite and MySQL
"""
import os
import logging
from typing import Any, Optional
from urllib.parse import urlparse

class DatabaseManager:
    """
    Universal database connection manager that supports SQLite and MySQL
    """
    
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.db_type = self._detect_db_type(db_url)
        self.logger = logging.getLogger(__name__)
        
    def _detect_db_type(self, db_url: str) -> str:
        """Detect database type from URL"""
        if db_url.startswith('mysql://') or db_url.startswith('mysql+pymysql://'):
            return 'mysql'
        elif db_url.startswith('sqlite://') or '.' in db_url:
            return 'sqlite'
        else:
            # Default to SQLite for simple paths
            return 'sqlite'
    
    def get_connection(self, timeout: float = 30.0):
        """Get database connection based on type"""
        if self.db_type == 'mysql':
            return self._get_mysql_connection(timeout)
        else:
            return self._get_sqlite_connection(timeout)
    
    def _get_sqlite_connection(self, timeout: float = 30.0):
        """Get SQLite connection"""
        import sqlite3
        
        # Handle both file paths and sqlite:// URLs
        if self.db_url.startswith('sqlite://'):
            db_path = self.db_url.replace('sqlite:///', '').replace('sqlite://', '')
        else:
            db_path = self.db_url
            
        conn = sqlite3.connect(db_path, timeout=timeout)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _get_mysql_connection(self, timeout: float = 30.0):
        """Get MySQL connection"""
        try:
            import pymysql
            
            # Parse MySQL URL: mysql://user:password@host:port/database
            parsed = urlparse(self.db_url)
            
            connection_params = {
                'host': parsed.hostname,
                'port': parsed.port or 3306,
                'user': parsed.username,
                'password': parsed.password,
                'database': parsed.path.lstrip('/'),
                'charset': 'utf8mb4',
                'autocommit': False,
                'connect_timeout': int(timeout),
                'cursorclass': pymysql.cursors.DictCursor
            }
            
            conn = pymysql.connect(**connection_params)
            return conn
            
        except ImportError:
            raise ImportError("pymysql is required for MySQL connections. Install with: pip install pymysql")
        except Exception as e:
            self.logger.error(f"MySQL connection failed: {str(e)}")
            raise
    
    def execute_query(self, query: str, params: tuple = None, timeout: float = 30.0):
        """Execute a query and return results"""
        conn = self.get_connection(timeout)
        try:
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Handle different return types
            if query.strip().upper().startswith(('SELECT', 'SHOW', 'DESCRIBE')):
                results = cursor.fetchall()
                return results
            else:
                conn.commit()
                return cursor.rowcount
                
        finally:
            conn.close()
    
    def execute_script(self, script: str, timeout: float = 30.0):
        """Execute multiple SQL statements"""
        conn = self.get_connection(timeout)
        try:
            if self.db_type == 'mysql':
                # Split script into individual statements for MySQL
                statements = [stmt.strip() for stmt in script.split(';') if stmt.strip()]
                cursor = conn.cursor()
                for statement in statements:
                    if statement:
                        cursor.execute(statement)
                conn.commit()
            else:
                # SQLite can handle executescript
                conn.executescript(script)
        finally:
            conn.close()
    
    def get_sql_dialect(self) -> dict:
        """Get SQL dialect-specific syntax"""
        if self.db_type == 'mysql':
            return {
                'autoincrement': 'AUTO_INCREMENT',
                'primary_key': 'INT AUTO_INCREMENT PRIMARY KEY',
                'text_type': 'TEXT',
                'real_type': 'DECIMAL(10,2)',
                'timestamp': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
                'limit_syntax': 'LIMIT'
            }
        else:  # SQLite
            return {
                'autoincrement': 'AUTOINCREMENT',
                'primary_key': 'INTEGER PRIMARY KEY AUTOINCREMENT',
                'text_type': 'TEXT',
                'real_type': 'REAL',
                'timestamp': 'TEXT DEFAULT CURRENT_TIMESTAMP',
                'limit_syntax': 'LIMIT'
            }
"""Database service for SQL operations."""
from typing import Optional, List, Dict, Any
import sqlalchemy
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.pool import NullPool
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for database operations."""
    
    def __init__(self):
        self.engine: Optional[sqlalchemy.Engine] = None
        self._initialize()
    
    def _initialize(self):
        """Initialize database connection."""
        try:
            if settings.DATABASE_URL:
                db_url = settings.DATABASE_URL
            elif all([settings.DB_HOST, settings.DB_NAME, settings.DB_USER]):
                db_url = (
                    f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@"
                    f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
                )
            else:
                logger.warning("Database credentials not set. SQL agent will have limited functionality.")
                return
            
            # Use NullPool for serverless/containerized deployments
            self.engine = create_engine(
                db_url,
                poolclass=NullPool,
                pool_pre_ping=True,
                echo=False
            )
            logger.info("Database connection initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            self.engine = None
    
    def is_available(self) -> bool:
        """Check if database is available."""
        return self.engine is not None
    
    def get_schema(self) -> Dict[str, Any]:
        """Get database schema information."""
        if not self.is_available():
            return {}
        
        try:
            inspector = inspect(self.engine)
            schema = {}
            
            for table_name in inspector.get_table_names():
                columns = []
                for column in inspector.get_columns(table_name):
                    columns.append({
                        "name": column["name"],
                        "type": str(column["type"]),
                        "nullable": column["nullable"],
                        "default": str(column.get("default", ""))
                    })
                
                foreign_keys = []
                for fk in inspector.get_foreign_keys(table_name):
                    foreign_keys.append({
                        "constrained_columns": fk["constrained_columns"],
                        "referred_table": fk["referred_table"],
                        "referred_columns": fk["referred_columns"]
                    })
                
                schema[table_name] = {
                    "columns": columns,
                    "foreign_keys": foreign_keys
                }
            
            return schema
        except Exception as e:
            logger.error(f"Error getting schema: {e}")
            return {}
    
    def execute_query(self, query: str, limit: int = 100) -> Dict[str, Any]:
        """Execute a SQL query safely."""
        if not self.is_available():
            raise RuntimeError("Database is not initialized")
        
        # Basic safety check - prevent dangerous operations
        query_lower = query.lower().strip()
        dangerous_keywords = ["drop", "delete", "truncate", "alter", "create", "insert", "update"]
        
        for keyword in dangerous_keywords:
            if query_lower.startswith(keyword):
                raise ValueError(f"Operation '{keyword}' is not allowed for safety")
        
        # Add LIMIT if SELECT query and no limit exists
        if query_lower.startswith("select") and "limit" not in query_lower:
            query = f"{query.rstrip(';')} LIMIT {limit}"
        
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query))
                
                if result.returns_rows:
                    rows = result.fetchall()
                    columns = result.keys()
                    return {
                        "columns": list(columns),
                        "rows": [dict(row._mapping) for row in rows],
                        "row_count": len(rows)
                    }
                else:
                    return {
                        "message": "Query executed successfully",
                        "row_count": result.rowcount
                    }
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise


# Global instance
database_service = DatabaseService()


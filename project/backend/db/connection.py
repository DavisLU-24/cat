"""
数据库连接管理模块
负责 SQLite 连接和初始化
"""
import sqlite3
import os
from pathlib import Path


class DatabaseConnection:
    """数据库连接单例"""

    _instance = None
    _connection = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._connection is None:
            self._initialize_database()

    def _initialize_database(self):
        """初始化数据库连接和表结构"""
        # 确定数据库路径
        project_root = Path(__file__).parent.parent.parent
        db_path = project_root / "data" / "travel_cat.db"
        schema_path = project_root / "database" / "schema.sql"

        # 确保 data 目录存在
        db_path.parent.mkdir(parents=True, exist_ok=True)

        # 数据库是否需要初始化
        db_exists = db_path.exists()

        # 连接数据库
        self._connection = sqlite3.connect(
            str(db_path),
            check_same_thread=False  # 允许多线程访问
        )
        self._connection.row_factory = sqlite3.Row  # 返回字典式行

        # 启用外键约束
        self._connection.execute("PRAGMA foreign_keys = ON")

        # 如果数据库不存在或为空，执行初始化
        if not db_exists or self._is_empty_database():
            self._create_schema(schema_path)

    def _is_empty_database(self) -> bool:
        """检查数据库是否为空（无表）"""
        cursor = self._connection.execute(
            "SELECT count(*) FROM sqlite_master WHERE type='table'"
        )
        count = cursor.fetchone()[0]
        return count == 0

    def _create_schema(self, schema_path: Path):
        """执行 schema.sql 创建表结构"""
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")

        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        # 执行建表脚本
        self._connection.executescript(schema_sql)
        self._connection.commit()

    def get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        if self._connection is None:
            self._initialize_database()
        return self._connection

    def close(self):
        """关闭数据库连接"""
        if self._connection:
            self._connection.close()
            self._connection = None


def get_db_connection() -> sqlite3.Connection:
    """全局获取数据库连接的便捷函数"""
    db = DatabaseConnection()
    return db.get_connection()

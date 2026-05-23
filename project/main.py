"""
旅行小猫 - 上海海事大学版
项目入口文件
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from frontend import main

if __name__ == "__main__":
    main()

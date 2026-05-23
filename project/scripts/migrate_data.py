"""
数据迁移脚本
在 JSON 和 SQLite 之间迁移存档数据
"""
import sys
import argparse
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.db import GameRepository
from backend.save_system import SaveManager


def migrate_json_to_db(slot_id: int = None):
    """从 JSON 导入到 SQLite"""
    repository = GameRepository()
    manager = SaveManager(repository)

    if slot_id:
        # 迁移指定槽位
        result = manager.import_from_json(slot_id)
        if result["success"]:
            print(f"✓ 槽位 {slot_id} 导入成功")
        else:
            print(f"✗ 槽位 {slot_id} 导入失败: {result['message']}")
    else:
        # 迁移所有槽位
        for i in range(1, 11):
            result = manager.import_from_json(i)
            if result["success"]:
                print(f"✓ 槽位 {i} 导入成功")


def migrate_db_to_json(slot_id: int = None):
    """从 SQLite 导出到 JSON"""
    repository = GameRepository()
    manager = SaveManager(repository)

    if slot_id:
        # 导出指定槽位
        result = manager.export_to_json(slot_id)
        if result["success"]:
            print(f"✓ 槽位 {slot_id} 导出成功: {result['json_path']}")
        else:
            print(f"✗ 槽位 {slot_id} 导出失败: {result['message']}")
    else:
        # 导出所有槽位
        slots = repository.get_save_slots_info()
        for slot in slots:
            if slot["is_occupied"]:
                result = manager.export_to_json(slot["slot_id"])
                if result["success"]:
                    print(f"✓ 槽位 {slot['slot_id']} 导出成功")


def main():
    parser = argparse.ArgumentParser(description="旅行小猫存档迁移工具")

    parser.add_argument(
        "command",
        choices=["json2db", "db2json"],
        help="迁移方向: json2db (JSON→SQLite) 或 db2json (SQLite→JSON)"
    )

    parser.add_argument(
        "--slot",
        type=int,
        choices=range(1, 11),
        help="指定槽位 (1-10)，不指定则迁移所有槽位"
    )

    args = parser.parse_args()

    print(f"\n{'='*50}")
    print(f"  旅行小猫 - 存档迁移工具")
    print(f"{'='*50}\n")

    if args.command == "json2db":
        print(f"从 JSON 导入到 SQLite...")
        migrate_json_to_db(args.slot)

    elif args.command == "db2json":
        print(f"从 SQLite 导出到 JSON...")
        migrate_db_to_json(args.slot)

    print(f"\n{'='*50}")
    print(f"  迁移完成")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()

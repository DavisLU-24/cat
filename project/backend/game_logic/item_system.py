"""
物品系统模块
处理背包管理和收集进度统计
"""
from typing import Dict, List, Any


class ItemSystem:
    """物品系统"""

    def __init__(self, repository):
        self.repository = repository

    def add_items(self, inventory: Dict[str, int], item_ids: List[str]) -> Dict[str, int]:
        """
        向背包添加物品

        参数:
            inventory: 当前背包 {item_id: quantity}
            item_ids: 要添加的物品 ID 列表

        返回:
            更新后的背包
        """
        new_inventory = inventory.copy()

        for item_id in item_ids:
            if item_id in new_inventory:
                new_inventory[item_id] += 1
            else:
                new_inventory[item_id] = 1

        return new_inventory

    def get_inventory_by_type(
        self,
        inventory: Dict[str, int]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        按类型分组获取背包物品

        返回:
            {
                "postcards": [item_with_quantity],
                "badges": [item_with_quantity],
                "treasures": [item_with_quantity]
            }
        """
        all_items = self.repository.get_all_items()

        # 按类型分组
        result = {
            "postcards": [],
            "badges": [],
            "treasures": []
        }

        for item in all_items:
            item_id = item["id"]
            quantity = inventory.get(item_id, 0)

            if quantity > 0:
                item_with_quantity = item.copy()
                item_with_quantity["quantity"] = quantity

                item_type = item["type"]
                if item_type == "postcard":
                    result["postcards"].append(item_with_quantity)
                elif item_type == "badge":
                    result["badges"].append(item_with_quantity)
                elif item_type == "treasure":
                    result["treasures"].append(item_with_quantity)

        return result

    def calculate_collection_progress(
        self,
        inventory: Dict[str, int]
    ) -> Dict[str, Any]:
        """
        计算收集进度

        返回:
            {
                "total_items": int,
                "collected_items": int,
                "progress_percentage": float,
                "by_type": {
                    "postcard": {"collected": int, "total": int, "percentage": float},
                    "badge": {...},
                    "treasure": {...}
                },
                "by_landmark": {
                    "landmark_id": {"collected": int, "total": int, "percentage": float}
                }
            }
        """
        all_items = self.repository.get_all_items()
        all_landmarks = self.repository.get_all_landmarks()

        # 总体进度
        total_items = len(all_items)
        collected_items = sum(1 for item in all_items if inventory.get(item["id"], 0) > 0)
        progress_percentage = (collected_items / total_items * 100) if total_items > 0 else 0

        # 按类型统计
        by_type = {}
        for item_type in ["postcard", "badge", "treasure"]:
            type_items = [item for item in all_items if item["type"] == item_type]
            type_total = len(type_items)
            type_collected = sum(1 for item in type_items if inventory.get(item["id"], 0) > 0)
            type_percentage = (type_collected / type_total * 100) if type_total > 0 else 0

            by_type[item_type] = {
                "collected": type_collected,
                "total": type_total,
                "percentage": round(type_percentage, 1)
            }

        # 按地标统计
        by_landmark = {}
        for landmark in all_landmarks:
            landmark_id = landmark["id"]
            landmark_items = [item for item in all_items if item["landmark_id"] == landmark_id]
            landmark_total = len(landmark_items)
            landmark_collected = sum(1 for item in landmark_items if inventory.get(item["id"], 0) > 0)
            landmark_percentage = (landmark_collected / landmark_total * 100) if landmark_total > 0 else 0

            by_landmark[landmark_id] = {
                "name": landmark["name"],
                "collected": landmark_collected,
                "total": landmark_total,
                "percentage": round(landmark_percentage, 1)
            }

        return {
            "total_items": total_items,
            "collected_items": collected_items,
            "progress_percentage": round(progress_percentage, 1),
            "by_type": by_type,
            "by_landmark": by_landmark
        }

    def get_item_rarity_color(self, rarity: str) -> str:
        """获取稀有度对应的颜色"""
        colors = {
            "common": "gray",
            "rare": "blue",
            "legendary": "gold"
        }
        return colors.get(rarity, "gray")

    def has_item(self, inventory: Dict[str, int], item_id: str) -> bool:
        """检查是否拥有某个物品"""
        return inventory.get(item_id, 0) > 0

    def get_item_count(self, inventory: Dict[str, int], item_id: str) -> int:
        """获取物品数量"""
        return inventory.get(item_id, 0)

"""
数据访问层 Repository
负责所有数据库的 CRUD 操作
"""
import sqlite3
from typing import Dict, List, Optional, Any
from datetime import datetime
from .connection import get_db_connection


class GameRepository:
    """游戏数据仓库"""

    def __init__(self):
        self.conn = get_db_connection()

    # ==================== 食物相关 ====================

    def get_all_foods(self) -> List[Dict[str, Any]]:
        """获取所有食物"""
        cursor = self.conn.execute("SELECT * FROM Foods")
        return [dict(row) for row in cursor.fetchall()]

    def get_food_by_id(self, food_id: str) -> Optional[Dict[str, Any]]:
        """根据 ID 获取食物"""
        cursor = self.conn.execute("SELECT * FROM Foods WHERE id = ?", (food_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    # ==================== 地标相关 ====================

    def get_all_landmarks(self) -> List[Dict[str, Any]]:
        """获取所有地标"""
        cursor = self.conn.execute("SELECT * FROM Landmarks ORDER BY min_energy")
        return [dict(row) for row in cursor.fetchall()]

    def get_landmark_by_id(self, landmark_id: str) -> Optional[Dict[str, Any]]:
        """根据 ID 获取地标"""
        cursor = self.conn.execute("SELECT * FROM Landmarks WHERE id = ?", (landmark_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_available_landmarks(self, current_energy: int) -> List[Dict[str, Any]]:
        """获取当前能量可访问的地标"""
        cursor = self.conn.execute(
            "SELECT * FROM Landmarks WHERE min_energy <= ? ORDER BY min_energy",
            (current_energy,)
        )
        return [dict(row) for row in cursor.fetchall()]

    # ==================== 收集品相关 ====================

    def get_all_items(self) -> List[Dict[str, Any]]:
        """获取所有收集品"""
        cursor = self.conn.execute("SELECT * FROM Items")
        return [dict(row) for row in cursor.fetchall()]

    def get_item_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        """根据 ID 获取收集品"""
        cursor = self.conn.execute("SELECT * FROM Items WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_items_by_landmark(self, landmark_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """获取指定地标的所有收集品，按类型分组"""
        cursor = self.conn.execute(
            "SELECT * FROM Items WHERE landmark_id = ? ORDER BY type, id",
            (landmark_id,)
        )
        items = [dict(row) for row in cursor.fetchall()]

        return {
            "postcards": [item for item in items if item["type"] == "postcard"],
            "badges": [item for item in items if item["type"] == "badge"],
            "treasures": [item for item in items if item["type"] == "treasure"]
        }

    # ==================== 存档槽位相关 ====================

    def get_save_slots_info(self) -> List[Dict[str, Any]]:
        """获取所有存档槽位信息"""
        # 确保所有槽位都存在
        for slot_id in range(1, 11):
            self.conn.execute("""
                INSERT OR IGNORE INTO SaveSlots (slot_id, game_time, is_occupied)
                VALUES (?, 0, 0)
            """, (slot_id,))
        self.conn.commit()

        cursor = self.conn.execute("""
            SELECT slot_id, game_time, save_time, is_occupied
            FROM SaveSlots
            ORDER BY slot_id
        """)
        return [dict(row) for row in cursor.fetchall()]

    def is_slot_occupied(self, slot_id: int) -> bool:
        """检查槽位是否已占用"""
        cursor = self.conn.execute(
            "SELECT is_occupied FROM SaveSlots WHERE slot_id = ?",
            (slot_id,)
        )
        row = cursor.fetchone()
        return bool(row["is_occupied"]) if row else False

    # ==================== 小猫状态相关 ====================

    def save_cat_state(self, slot_id: int, cat_state: Dict[str, Any]):
        """保存小猫状态"""
        self.conn.execute("""
            INSERT OR REPLACE INTO CatState
            (slot_id, current_energy, status, mood, last_fed_time, total_travels)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            slot_id,
            cat_state.get("current_energy", 100),
            cat_state.get("status", "idle"),
            cat_state.get("mood", "happy"),
            cat_state.get("last_fed_time"),
            cat_state.get("total_travels", 0)
        ))
        self.conn.commit()

    def load_cat_state(self, slot_id: int) -> Optional[Dict[str, Any]]:
        """加载小猫状态"""
        cursor = self.conn.execute(
            "SELECT * FROM CatState WHERE slot_id = ?",
            (slot_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    # ==================== 背包相关 ====================

    def save_inventory(self, slot_id: int, inventory: Dict[str, int]):
        """保存背包（完全覆盖）"""
        # 删除旧数据
        self.conn.execute("DELETE FROM PlayerInventory WHERE slot_id = ?", (slot_id,))

        # 插入新数据
        for item_id, quantity in inventory.items():
            if quantity > 0:
                self.conn.execute("""
                    INSERT INTO PlayerInventory (slot_id, item_id, quantity)
                    VALUES (?, ?, ?)
                """, (slot_id, item_id, quantity))

        self.conn.commit()

    def load_inventory(self, slot_id: int) -> Dict[str, int]:
        """加载背包"""
        cursor = self.conn.execute(
            "SELECT item_id, quantity FROM PlayerInventory WHERE slot_id = ?",
            (slot_id,)
        )
        return {row["item_id"]: row["quantity"] for row in cursor.fetchall()}

    def add_item_to_inventory(self, slot_id: int, item_id: str, quantity: int = 1):
        """向背包添加物品"""
        cursor = self.conn.execute("""
            SELECT quantity FROM PlayerInventory
            WHERE slot_id = ? AND item_id = ?
        """, (slot_id, item_id))
        row = cursor.fetchone()

        if row:
            # 更新数量
            new_quantity = row["quantity"] + quantity
            self.conn.execute("""
                UPDATE PlayerInventory SET quantity = ?
                WHERE slot_id = ? AND item_id = ?
            """, (new_quantity, slot_id, item_id))
        else:
            # 插入新物品
            self.conn.execute("""
                INSERT INTO PlayerInventory (slot_id, item_id, quantity)
                VALUES (?, ?, ?)
            """, (slot_id, item_id, quantity))

        self.conn.commit()

    # ==================== 旅行历史相关 ====================

    def save_travel_history(self, slot_id: int, travel_data: Dict[str, Any]) -> int:
        """保存旅行历史记录，返回 travel_id"""
        cursor = self.conn.execute("""
            INSERT INTO TravelHistory
            (slot_id, landmark_id, start_time, end_time, energy_before, energy_after, duration)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            slot_id,
            travel_data["landmark_id"],
            travel_data.get("start_time"),
            travel_data.get("end_time"),
            travel_data["energy_before"],
            travel_data["energy_after"],
            travel_data["duration"]
        ))
        self.conn.commit()
        return cursor.lastrowid

    def save_travel_rewards(self, travel_id: int, rewards: List[str]):
        """保存旅行奖励"""
        for item_id in rewards:
            self.conn.execute("""
                INSERT INTO TravelRewards (travel_id, item_id)
                VALUES (?, ?)
            """, (travel_id, item_id))
        self.conn.commit()

    def get_travel_history(self, slot_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """获取旅行历史"""
        cursor = self.conn.execute("""
            SELECT th.*, l.name as landmark_name
            FROM TravelHistory th
            JOIN Landmarks l ON th.landmark_id = l.id
            WHERE th.slot_id = ?
            ORDER BY th.id DESC
            LIMIT ?
        """, (slot_id, limit))
        return [dict(row) for row in cursor.fetchall()]

    # ==================== 已解锁地标相关 ====================

    def save_unlocked_landmarks(self, slot_id: int, landmark_ids: List[str]):
        """保存已解锁地标"""
        # 删除旧数据
        self.conn.execute("DELETE FROM UnlockedLandmarks WHERE slot_id = ?", (slot_id,))

        # 插入新数据
        for landmark_id in landmark_ids:
            self.conn.execute("""
                INSERT INTO UnlockedLandmarks (slot_id, landmark_id)
                VALUES (?, ?)
            """, (slot_id, landmark_id))

        self.conn.commit()

    def load_unlocked_landmarks(self, slot_id: int) -> List[str]:
        """加载已解锁地标"""
        cursor = self.conn.execute(
            "SELECT landmark_id FROM UnlockedLandmarks WHERE slot_id = ?",
            (slot_id,)
        )
        return [row["landmark_id"] for row in cursor.fetchall()]

    def unlock_landmark(self, slot_id: int, landmark_id: str):
        """解锁地标"""
        self.conn.execute("""
            INSERT OR IGNORE INTO UnlockedLandmarks (slot_id, landmark_id)
            VALUES (?, ?)
        """, (slot_id, landmark_id))
        self.conn.commit()

    # ==================== 当前旅行状态相关 ====================

    def save_current_travel(self, slot_id: int, travel_data: Dict[str, Any]):
        """保存当前旅行状态"""
        self.conn.execute("""
            INSERT OR REPLACE INTO CurrentTravel
            (slot_id, landmark_id, start_time, duration, energy_before)
            VALUES (?, ?, ?, ?, ?)
        """, (
            slot_id,
            travel_data["landmark_id"],
            travel_data["start_time"],
            travel_data["duration"],
            travel_data["energy_before"]
        ))
        self.conn.commit()

    def load_current_travel(self, slot_id: int) -> Optional[Dict[str, Any]]:
        """加载当前旅行状态"""
        cursor = self.conn.execute(
            "SELECT * FROM CurrentTravel WHERE slot_id = ?",
            (slot_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def clear_current_travel(self, slot_id: int):
        """清除当前旅行状态"""
        self.conn.execute("DELETE FROM CurrentTravel WHERE slot_id = ?", (slot_id,))
        self.conn.commit()

    # ==================== 完整存档相关 ====================

    def save_game_state(self, slot_id: int, game_state: Dict[str, Any]):
        """保存完整游戏状态（事务）"""
        try:
            self.conn.execute("BEGIN TRANSACTION")

            # 更新或创建存档槽位
            self.conn.execute("""
                INSERT OR REPLACE INTO SaveSlots (slot_id, game_time, is_occupied)
                VALUES (?, ?, 1)
            """, (slot_id, game_state.get("game_time", 0)))

            # 保存小猫状态
            self.save_cat_state(slot_id, game_state.get("cat", {}))

            # 保存背包
            self.save_inventory(slot_id, game_state.get("inventory", {}))

            # 保存已解锁地标
            self.save_unlocked_landmarks(slot_id, game_state.get("unlocked_landmarks", []))

            # 保存当前旅行状态（如果有）
            if game_state.get("current_travel"):
                self.save_current_travel(slot_id, game_state["current_travel"])
            else:
                self.clear_current_travel(slot_id)

            self.conn.commit()
            return True

        except Exception as e:
            self.conn.rollback()
            print(f"Save game error: {e}")
            return False

    def load_game_state(self, slot_id: int) -> Optional[Dict[str, Any]]:
        """加载完整游戏状态"""
        # 检查槽位是否存在
        if not self.is_slot_occupied(slot_id):
            return None

        # 加载各部分数据
        cat_state = self.load_cat_state(slot_id)
        inventory = self.load_inventory(slot_id)
        unlocked_landmarks = self.load_unlocked_landmarks(slot_id)
        current_travel = self.load_current_travel(slot_id)

        # 获取游戏时间
        cursor = self.conn.execute(
            "SELECT game_time FROM SaveSlots WHERE slot_id = ?",
            (slot_id,)
        )
        row = cursor.fetchone()
        game_time = row["game_time"] if row else 0

        return {
            "game_time": game_time,
            "cat": cat_state or {},
            "inventory": inventory,
            "unlocked_landmarks": unlocked_landmarks,
            "current_travel": current_travel
        }

    def delete_save(self, slot_id: int):
        """删除存档"""
        try:
            self.conn.execute("BEGIN TRANSACTION")

            # 标记槽位为未占用
            self.conn.execute("""
                UPDATE SaveSlots SET is_occupied = 0, game_time = 0
                WHERE slot_id = ?
            """, (slot_id,))

            # 删除相关数据会被外键约束自动级联删除
            self.conn.execute("DELETE FROM CatState WHERE slot_id = ?", (slot_id,))
            self.conn.execute("DELETE FROM PlayerInventory WHERE slot_id = ?", (slot_id,))
            self.conn.execute("DELETE FROM UnlockedLandmarks WHERE slot_id = ?", (slot_id,))
            self.conn.execute("DELETE FROM CurrentTravel WHERE slot_id = ?", (slot_id,))
            self.conn.execute("DELETE FROM TravelHistory WHERE slot_id = ?", (slot_id,))

            self.conn.commit()
            return True

        except Exception as e:
            self.conn.rollback()
            print(f"Delete save error: {e}")
            return False

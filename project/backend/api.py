"""
游戏 API
前后端通信的统一门面接口
"""
import time
from typing import Dict, Any, List
from .db import GameRepository, seed_all, is_database_seeded
from .game_logic import Cat, EnergySystem, TravelSystem, ItemSystem
from .save_system import GameState, SaveManager


class GameAPI:
    """游戏 API 门面"""

    def __init__(self):
        # 初始化仓库和管理器
        self.repository = GameRepository()
        self.save_manager = SaveManager(self.repository)
        self.travel_system = TravelSystem(self.repository)
        self.item_system = ItemSystem(self.repository)

        # 游戏状态
        self.cat = Cat()
        self.game_state = GameState()
        self.game_start_time = time.time()

        # 当前槽位
        self.current_slot = None

        # 确保数据库已灌入种子数据
        if not is_database_seeded():
            seed_all()

    # ==================== 游戏初始化 ====================

    def init_game(self) -> Dict[str, Any]:
        """
        初始化游戏（重置状态）

        返回:
            {
                "success": bool,
                "message": str
            }
        """
        self.cat = Cat()
        self.game_state = GameState()
        self.game_state.cat = self.cat.to_dict()
        self.game_start_time = time.time()
        self.current_slot = None

        # 默认解锁第一个地标
        landmarks = self.repository.get_all_landmarks()
        if landmarks:
            self.game_state.unlocked_landmarks = [landmarks[0]["id"]]

        return {
            "success": True,
            "message": "游戏已初始化"
        }

    # ==================== 小猫状态相关 ====================

    def get_cat_status(self) -> Dict[str, Any]:
        """
        获取小猫状态

        返回:
            {
                "success": bool,
                "cat": {
                    "current_energy": int,
                    "status": str,
                    "mood": str,
                    "total_travels": int,
                    "energy_level": str,
                    "energy_description": str,
                    "energy_suggestion": str
                }
            }
        """
        energy_level = self.cat.get_energy_level()
        energy_description = EnergySystem.get_energy_level_description(self.cat.current_energy)
        energy_suggestion = EnergySystem.get_energy_suggestion(self.cat.current_energy)

        return {
            "success": True,
            "cat": {
                **self.cat.to_dict(),
                "energy_level": energy_level,
                "energy_description": energy_description,
                "energy_suggestion": energy_suggestion
            }
        }

    # ==================== 食物相关 ====================

    def get_available_foods(self) -> Dict[str, Any]:
        """
        获取所有可用食物

        返回:
            {
                "success": bool,
                "foods": List[Dict]
            }
        """
        foods = self.repository.get_all_foods()

        return {
            "success": True,
            "foods": foods
        }

    def feed_cat(self, food_id: str) -> Dict[str, Any]:
        """
        喂食小猫

        返回:
            {
                "success": bool,
                "message": str,
                "new_energy": int,
                "energy_gained": int
            }
        """
        # 获取食物信息
        food = self.repository.get_food_by_id(food_id)
        if not food:
            return {
                "success": False,
                "message": "食物不存在",
                "new_energy": self.cat.current_energy,
                "energy_gained": 0
            }

        # 验证喂食
        validation = EnergySystem.validate_feed(
            self.cat.current_energy,
            food["energy_value"]
        )

        if not validation["success"]:
            return validation

        # 执行喂食
        success = self.cat.feed(food["energy_value"])

        if not success:
            return {
                "success": False,
                "message": "喂食失败",
                "new_energy": self.cat.current_energy,
                "energy_gained": 0
            }

        # 更新游戏状态
        self.game_state.cat = self.cat.to_dict()
        self.cat.last_fed_time = time.time()

        # 喂食后重置为空闲状态
        if self.cat.status == "eating":
            self.cat.reset_to_idle()

        return {
            "success": True,
            "message": f"{food['name']} 能量 +{validation['energy_gained']}",
            "new_energy": self.cat.current_energy,
            "energy_gained": validation["energy_gained"]
        }

    # ==================== 地标相关 ====================

    def get_available_landmarks(self) -> Dict[str, Any]:
        """
        获取所有地标（包括可访问状态）

        返回:
            {
                "success": bool,
                "landmarks": List[Dict]  # 包含 can_visit 字段
            }
        """
        all_landmarks = self.repository.get_all_landmarks()

        # 添加可访问状态
        for landmark in all_landmarks:
            landmark["can_visit"] = self.cat.current_energy >= landmark["min_energy"]
            landmark["is_unlocked"] = landmark["id"] in self.game_state.unlocked_landmarks

        return {
            "success": True,
            "landmarks": all_landmarks
        }

    # ==================== 旅行相关 ====================

    def start_travel(self, landmark_id: str) -> Dict[str, Any]:
        """
        开始旅行

        返回:
            {
                "success": bool,
                "message": str,
                "travel_info": {
                    "landmark_name": str,
                    "duration": float,
                    "start_time": float
                }
            }
        """
        # 获取地标信息
        landmark = self.repository.get_landmark_by_id(landmark_id)
        if not landmark:
            return {
                "success": False,
                "message": "地标不存在",
                "travel_info": None
            }

        # 检查是否已在旅行中
        if self.cat.status == "traveling":
            return {
                "success": False,
                "message": "小猫已经在旅行中了",
                "travel_info": None
            }

        # 开始旅行
        result = self.travel_system.start_travel(self.cat, landmark)

        if not result["success"]:
            return {
                "success": False,
                "message": result["message"],
                "travel_info": None
            }

        # 保存旅行数据
        self.game_state.current_travel = result["travel_data"]
        self.game_state.cat = self.cat.to_dict()

        # 解锁该地标
        if landmark_id not in self.game_state.unlocked_landmarks:
            self.game_state.unlocked_landmarks.append(landmark_id)

        return {
            "success": True,
            "message": result["message"],
            "travel_info": {
                "landmark_name": landmark["name"],
                "duration": result["travel_data"]["duration"],
                "start_time": result["travel_data"]["start_time"]
            }
        }

    def start_random_travel(self) -> Dict[str, Any]:
        """
        随机旅行（选择一个可访问的地标）

        返回: 同 start_travel
        """
        available = self.repository.get_available_landmarks(self.cat.current_energy)

        if not available:
            return {
                "success": False,
                "message": "没有可访问的地标",
                "travel_info": None
            }

        import random
        landmark = random.choice(available)

        return self.start_travel(landmark["id"])

    def check_travel_status(self) -> Dict[str, Any]:
        """
        检查旅行进度

        返回:
            {
                "success": bool,
                "is_traveling": bool,
                "is_completed": bool,
                "progress": float,
                "remaining_time": float,
                "landmark_name": str
            }
        """
        if not self.game_state.current_travel:
            return {
                "success": True,
                "is_traveling": False,
                "is_completed": False,
                "progress": 0.0,
                "remaining_time": 0.0,
                "landmark_name": None
            }

        # 检查进度
        progress_info = self.travel_system.check_travel_progress(self.game_state.current_travel)

        # 获取地标名称
        landmark = self.repository.get_landmark_by_id(self.game_state.current_travel["landmark_id"])
        landmark_name = landmark["name"] if landmark else "未知地点"

        return {
            "success": True,
            "is_traveling": True,
            "is_completed": progress_info["is_completed"],
            "progress": progress_info["progress"],
            "remaining_time": progress_info["remaining_time"],
            "landmark_name": landmark_name
        }

    def end_travel(self, save_progress: bool = True) -> Dict[str, Any]:
        """
        结束旅行（自动或手动）

        参数:
            save_progress: 是否保存进度到历史记录

        返回:
            {
                "success": bool,
                "message": str,
                "rewards": List[Dict],  # 奖励物品完整信息
                "new_items": List[str]  # 新获得的物品 ID
            }
        """
        if not self.game_state.current_travel:
            return {
                "success": False,
                "message": "没有进行中的旅行",
                "rewards": [],
                "new_items": []
            }

        # 完成旅行并生成奖励
        result = self.travel_system.complete_travel(self.cat, self.game_state.current_travel)

        if not result["success"]:
            return {
                "success": False,
                "message": result["message"],
                "rewards": [],
                "new_items": []
            }

        # 更新背包
        self.game_state.inventory = self.item_system.add_items(
            self.game_state.inventory,
            result["rewards"]
        )

        # 更新小猫状态
        self.game_state.cat = self.cat.to_dict()

        # 清除当前旅行
        travel_data = self.game_state.current_travel
        self.game_state.current_travel = None

        # 小猫回到空闲状态
        self.cat.reset_to_idle()

        return {
            "success": True,
            "message": result["message"],
            "rewards": result["reward_items"],
            "new_items": result["rewards"]
        }

    def cancel_travel(self) -> Dict[str, Any]:
        """
        取消旅行

        返回:
            {
                "success": bool,
                "message": str
            }
        """
        result = self.travel_system.cancel_travel(self.cat)

        if result["success"]:
            self.game_state.current_travel = None
            self.game_state.cat = self.cat.to_dict()

        return result

    # ==================== 背包相关 ====================

    def get_inventory(self) -> Dict[str, Any]:
        """
        获取背包

        返回:
            {
                "success": bool,
                "inventory": {
                    "postcards": List[Dict],
                    "badges": List[Dict],
                    "treasures": List[Dict]
                },
                "total_count": int
            }
        """
        inventory_by_type = self.item_system.get_inventory_by_type(self.game_state.inventory)

        total_count = (
            len(inventory_by_type["postcards"]) +
            len(inventory_by_type["badges"]) +
            len(inventory_by_type["treasures"])
        )

        return {
            "success": True,
            "inventory": inventory_by_type,
            "total_count": total_count
        }

    def get_collection_progress(self) -> Dict[str, Any]:
        """
        获取收集进度

        返回:
            {
                "success": bool,
                "progress": Dict  # 收集进度详情
            }
        """
        progress = self.item_system.calculate_collection_progress(self.game_state.inventory)

        return {
            "success": True,
            "progress": progress
        }

    # ==================== 存档相关 ====================

    def save_game(self, slot_id: int) -> Dict[str, Any]:
        """
        保存游戏

        返回:
            {
                "success": bool,
                "message": str,
                "slot_id": int
            }
        """
        # 更新游戏时间
        self.game_state.game_time = time.time() - self.game_start_time

        # 更新小猫状态
        self.game_state.cat = self.cat.to_dict()

        # 保存
        result = self.save_manager.save_game(slot_id, self.game_state)

        if result["success"]:
            self.current_slot = slot_id

        return result

    def load_game(self, slot_id: int) -> Dict[str, Any]:
        """
        加载游戏

        返回:
            {
                "success": bool,
                "message": str,
                "slot_id": int
            }
        """
        result = self.save_manager.load_game(slot_id)

        if not result["success"]:
            return result

        # 恢复游戏状态
        self.game_state = result["game_state"]
        self.cat.from_dict(self.game_state.cat)
        self.current_slot = slot_id

        # 重置游戏开始时间
        self.game_start_time = time.time() - self.game_state.game_time

        return {
            "success": True,
            "message": result["message"],
            "slot_id": slot_id
        }

    def get_save_slots_info(self) -> Dict[str, Any]:
        """
        获取存档槽位信息

        返回:
            {
                "success": bool,
                "slots": List[Dict]
            }
        """
        return self.save_manager.get_save_slots_info()

    def delete_save(self, slot_id: int) -> Dict[str, Any]:
        """
        删除存档

        返回:
            {
                "success": bool,
                "message": str
            }
        """
        return self.save_manager.delete_save(slot_id)

    # ==================== 自动保存 ====================

    def auto_check_travel_and_save(self):
        """
        自动检查旅行完成并保存（由游戏主循环调用）
        """
        if not self.game_state.current_travel:
            return

        # 检查是否完成
        status = self.check_travel_status()

        if status["is_completed"] and self.cat.status == "traveling":
            # 自动结束旅行
            self.end_travel(save_progress=True)

    # ==================== 辅助方法 ====================

    def get_game_time(self) -> float:
        """获取当前游戏时间（秒）"""
        return time.time() - self.game_start_time

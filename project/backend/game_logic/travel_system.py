"""
旅行系统模块
处理旅行流程、时间计算、奖励生成
"""
import random
import time
from typing import Dict, Any, List, Optional


class TravelSystem:
    """旅行系统"""

    def __init__(self, repository):
        self.repository = repository

    def calculate_travel_duration(self, base_time: int, min_energy: int) -> float:
        """
        计算旅行时间（秒）
        基础时间 + min_energy 加成 ± 20% 随机
        """
        # 加成：min_energy 越高，时间越长
        bonus_time = min_energy * 0.1

        # 总时间
        total_time = base_time + bonus_time

        # ±20% 随机
        random_factor = random.uniform(0.8, 1.2)
        final_time = total_time * random_factor

        return round(final_time, 2)

    def generate_rewards(
        self,
        landmark_id: str,
        energy_before_travel: int
    ) -> List[str]:
        """
        生成旅行奖励

        规则:
        - 必得 1 张明信片
        - 能量 ≥50：30%~80% 概率得徽章
        - 能量 >100：10%~60% 概率得宝物
        """
        rewards = []

        # 获取该地标的所有收集品
        items = self.repository.get_items_by_landmark(landmark_id)

        # 1. 必得一张明信片
        postcards = items.get("postcards", [])
        if postcards:
            postcard = random.choice(postcards)
            rewards.append(postcard["id"])

        # 2. 徽章概率
        if energy_before_travel >= 50:
            badges = items.get("badges", [])
            if badges:
                # 能量越高，概率越高：30% ~ 80%
                badge_probability = 0.3 + (min(energy_before_travel, 200) - 50) / 150 * 0.5
                if random.random() < badge_probability:
                    badge = random.choice(badges)
                    rewards.append(badge["id"])

        # 3. 宝物概率
        if energy_before_travel > 100:
            treasures = items.get("treasures", [])
            if treasures:
                # 能量越高，概率越高：10% ~ 60%
                treasure_probability = 0.1 + (min(energy_before_travel, 200) - 100) / 100 * 0.5
                if random.random() < treasure_probability:
                    treasure = treasures[0]
                    rewards.append(treasure["id"])

        return rewards

    def start_travel(
        self,
        cat,
        landmark: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        开始旅行

        返回:
            {
                "success": bool,
                "message": str,
                "travel_data": {
                    "landmark_id": str,
                    "start_time": float,
                    "duration": float,
                    "energy_before": int
                }
            }
        """
        landmark_id = landmark["id"]
        min_energy = landmark["min_energy"]
        energy_cost = landmark["energy_cost"]
        base_time = landmark["base_travel_time"]

        # 检查能量是否足够
        if not cat.can_travel(min_energy):
            return {
                "success": False,
                "message": f"能量不足或状态不对！需要至少 {min_energy} 能量且小猫处于空闲状态",
                "travel_data": None
            }

        # 记录出发前的能量
        energy_before = cat.current_energy

        # 消耗能量
        if not cat.consume_energy(energy_cost):
            return {
                "success": False,
                "message": "能量消耗失败",
                "travel_data": None
            }

        # 计算旅行时间
        duration = self.calculate_travel_duration(base_time, min_energy)

        # 更新小猫状态
        cat.start_travel()

        # 返回旅行数据
        travel_data = {
            "landmark_id": landmark_id,
            "start_time": time.time(),
            "duration": duration,
            "energy_before": energy_before
        }

        return {
            "success": True,
            "message": f"开始旅行到 {landmark['name']}！预计 {int(duration)} 秒",
            "travel_data": travel_data
        }

    def check_travel_progress(self, travel_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        检查旅行进度

        返回:
            {
                "is_completed": bool,
                "progress": float (0.0 ~ 1.0),
                "remaining_time": float (秒)
            }
        """
        if not travel_data:
            return {
                "is_completed": False,
                "progress": 0.0,
                "remaining_time": 0.0
            }

        current_time = time.time()
        start_time = travel_data["start_time"]
        duration = travel_data["duration"]

        elapsed_time = current_time - start_time
        progress = min(1.0, elapsed_time / duration)
        remaining_time = max(0.0, duration - elapsed_time)

        is_completed = progress >= 1.0

        return {
            "is_completed": is_completed,
            "progress": progress,
            "remaining_time": remaining_time
        }

    def complete_travel(
        self,
        cat,
        travel_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        完成旅行，生成奖励

        返回:
            {
                "success": bool,
                "message": str,
                "rewards": List[str],
                "reward_items": List[Dict]  # 完整的物品信息
            }
        """
        if not travel_data:
            return {
                "success": False,
                "message": "没有进行中的旅行",
                "rewards": [],
                "reward_items": []
            }

        landmark_id = travel_data["landmark_id"]
        energy_before = travel_data["energy_before"]

        # 生成奖励
        reward_ids = self.generate_rewards(landmark_id, energy_before)

        # 获取奖励的完整信息
        reward_items = []
        for item_id in reward_ids:
            item = self.repository.get_item_by_id(item_id)
            if item:
                reward_items.append(item)

        # 更新小猫状态
        cat.finish_travel()

        # 获取地标名称
        landmark = self.repository.get_landmark_by_id(landmark_id)
        landmark_name = landmark["name"] if landmark else "未知地点"

        return {
            "success": True,
            "message": f"从 {landmark_name} 旅行归来！",
            "rewards": reward_ids,
            "reward_items": reward_items
        }

    def cancel_travel(self, cat) -> Dict[str, Any]:
        """
        取消旅行（不返还能量）

        返回:
            {
                "success": bool,
                "message": str
            }
        """
        if cat.status != "traveling":
            return {
                "success": False,
                "message": "小猫没有在旅行中"
            }

        # 重置为空闲状态
        cat.reset_to_idle()

        return {
            "success": True,
            "message": "已取消旅行"
        }

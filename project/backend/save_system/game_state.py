"""
游戏状态类
可序列化的游戏状态对象
"""
from typing import Dict, Any, List, Optional
import json


class GameState:
    """游戏状态"""

    def __init__(self):
        self.game_time = 0.0  # 游戏时间（秒）
        self.cat = {}  # 小猫状态
        self.inventory = {}  # 背包 {item_id: quantity}
        self.unlocked_landmarks = []  # 已解锁地标
        self.current_travel = None  # 当前旅行状态

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "game_time": self.game_time,
            "cat": self.cat,
            "inventory": self.inventory,
            "unlocked_landmarks": self.unlocked_landmarks,
            "current_travel": self.current_travel
        }

    def from_dict(self, data: Dict[str, Any]):
        """从字典加载"""
        self.game_time = data.get("game_time", 0.0)
        self.cat = data.get("cat", {})
        self.inventory = data.get("inventory", {})
        self.unlocked_landmarks = data.get("unlocked_landmarks", [])
        self.current_travel = data.get("current_travel")

    def to_json(self) -> str:
        """转换为 JSON 字符串"""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    def from_json(self, json_str: str):
        """从 JSON 字符串加载"""
        data = json.loads(json_str)
        self.from_dict(data)

    def __repr__(self):
        return f"GameState(time={self.game_time}, energy={self.cat.get('current_energy', 0)})"

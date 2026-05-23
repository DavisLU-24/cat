"""
小猫状态管理模块
"""
from typing import Dict, Any


class Cat:
    """小猫类"""

    def __init__(self, initial_energy: int = 100):
        self.current_energy = initial_energy
        self.status = "idle"  # idle, eating, traveling, returning
        self.mood = "happy"  # happy, normal, tired, exhausted
        self.last_fed_time = None
        self.total_travels = 0

    def feed(self, energy_value: int) -> bool:
        """喂食，返回是否成功"""
        if self.current_energy >= 200:
            return False  # 已经吃饱了

        self.current_energy = min(200, self.current_energy + energy_value)
        self.status = "eating"
        self.update_mood()
        return True

    def consume_energy(self, amount: int) -> bool:
        """消耗能量，返回是否成功"""
        if self.current_energy < amount:
            return False

        self.current_energy = max(0, self.current_energy - amount)
        self.update_mood()
        return True

    def update_mood(self):
        """根据能量更新心情"""
        if self.current_energy == 0:
            self.mood = "exhausted"
        elif self.current_energy < 50:
            self.mood = "tired"
        elif self.current_energy < 100:
            self.mood = "normal"
        else:
            self.mood = "happy"

    def start_travel(self):
        """开始旅行"""
        self.status = "traveling"
        self.total_travels += 1

    def finish_travel(self):
        """完成旅行"""
        self.status = "returning"

    def reset_to_idle(self):
        """重置为空闲状态"""
        self.status = "idle"

    def get_energy_level(self) -> str:
        """获取能量等级描述"""
        if self.current_energy == 0:
            return "empty"
        elif self.current_energy < 30:
            return "very_low"
        elif self.current_energy < 70:
            return "low"
        elif self.current_energy < 120:
            return "medium"
        elif self.current_energy < 180:
            return "high"
        else:
            return "full"

    def can_travel(self, min_energy: int) -> bool:
        """检查是否有足够能量旅行"""
        return self.current_energy >= min_energy and self.status == "idle"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "current_energy": self.current_energy,
            "status": self.status,
            "mood": self.mood,
            "last_fed_time": self.last_fed_time,
            "total_travels": self.total_travels
        }

    def from_dict(self, data: Dict[str, Any]):
        """从字典加载"""
        self.current_energy = data.get("current_energy", 100)
        self.status = data.get("status", "idle")
        self.mood = data.get("mood", "happy")
        self.last_fed_time = data.get("last_fed_time")
        self.total_travels = data.get("total_travels", 0)

    def __repr__(self):
        return f"Cat(energy={self.current_energy}, status={self.status}, mood={self.mood})"

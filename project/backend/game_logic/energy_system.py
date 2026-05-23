"""
能量系统模块
处理能量相关的计算和验证
"""
from typing import Dict, Any


class EnergySystem:
    """能量系统"""

    MAX_ENERGY = 200
    MIN_ENERGY = 0

    @staticmethod
    def validate_feed(current_energy: int, food_energy: int) -> Dict[str, Any]:
        """验证喂食操作

        返回:
            {
                "success": bool,
                "message": str,
                "new_energy": int,
                "energy_gained": int
            }
        """
        if current_energy >= EnergySystem.MAX_ENERGY:
            return {
                "success": False,
                "message": "小猫已经吃饱了！",
                "new_energy": current_energy,
                "energy_gained": 0
            }

        new_energy = min(EnergySystem.MAX_ENERGY, current_energy + food_energy)
        energy_gained = new_energy - current_energy

        return {
            "success": True,
            "message": f"能量 +{energy_gained}",
            "new_energy": new_energy,
            "energy_gained": energy_gained
        }

    @staticmethod
    def validate_travel(current_energy: int, min_energy: int, energy_cost: int) -> Dict[str, Any]:
        """验证旅行操作

        返回:
            {
                "success": bool,
                "message": str,
                "energy_after": int
            }
        """
        if current_energy < min_energy:
            return {
                "success": False,
                "message": f"能量不足！需要至少 {min_energy} 能量",
                "energy_after": current_energy
            }

        energy_after = max(EnergySystem.MIN_ENERGY, current_energy - energy_cost)

        return {
            "success": True,
            "message": f"消耗了 {energy_cost} 能量",
            "energy_after": energy_after
        }

    @staticmethod
    def get_energy_level_description(energy: int) -> str:
        """获取能量等级的描述文本"""
        if energy == 0:
            return "能量耗尽"
        elif energy < 30:
            return "能量极低"
        elif energy < 70:
            return "能量偏低"
        elif energy < 120:
            return "能量适中"
        elif energy < 180:
            return "能量充沛"
        else:
            return "能量满满"

    @staticmethod
    def get_energy_suggestion(energy: int) -> str:
        """根据能量给出建议"""
        if energy == 0:
            return "赶快喂食吧！"
        elif energy < 30:
            return "建议先喂食再旅行"
        elif energy < 50:
            return "可以吃点东西补充能量"
        elif energy < 100:
            return "能量还可以，可以去近处旅行"
        elif energy < 150:
            return "能量充足，可以去远一点的地方"
        else:
            return "能量满满，可以探索任何地方！"

    @staticmethod
    def calculate_energy_percentage(energy: int) -> float:
        """计算能量百分比（0.0 ~ 1.0）"""
        return min(1.0, max(0.0, energy / EnergySystem.MAX_ENERGY))

    @staticmethod
    def get_energy_color(energy: int) -> str:
        """根据能量获取颜色建议（用于 UI）"""
        percentage = EnergySystem.calculate_energy_percentage(energy)

        if percentage >= 0.8:
            return "green"
        elif percentage >= 0.5:
            return "blue"
        elif percentage >= 0.3:
            return "yellow"
        else:
            return "red"

"""
旅行奖励系统测试和演示
展示不同能量下的奖励概率
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend import GameAPI

def test_reward_probabilities():
    """测试不同能量下的奖励概率"""

    print("="*60)
    print("旅行奖励系统 - 概率计算示例")
    print("="*60)

    # 测试不同能量等级
    energy_levels = [
        (30, "低能量"),
        (50, "中等能量（徽章阈值）"),
        (100, "高能量"),
        (150, "很高能量（宝物阈值）"),
        (200, "满能量")
    ]

    print("\n奖励概率说明：")
    print("-" * 60)

    for energy, label in energy_levels:
        print(f"\n【{label}：{energy} 能量】")

        # 明信片（必得）
        print("  - 明信片：100% （必得 1 张）")

        # 徽章概率
        if energy >= 50:
            badge_prob = 0.3 + (min(energy, 200) - 50) / 150 * 0.5
            print(f"  - 徽章：{badge_prob*100:.1f}% （能量≥50）")
        else:
            print(f"  - 徽章：0% （需要能量≥50）")

        # 宝物概率
        if energy > 100:
            treasure_prob = 0.1 + (min(energy, 200) - 100) / 100 * 0.5
            print(f"  - 宝物：{treasure_prob*100:.1f}% （能量>100）")
        else:
            print(f"  - 宝物：0% （需要能量>100）")

    print("\n" + "="*60)
    print("策略建议：")
    print("="*60)
    print("1. 能量 20-49：只能得明信片")
    print("2. 能量 50-100：可能得徽章（30%-70%）")
    print("3. 能量 101-200：同时有机会得徽章和宝物！")
    print("4. 满能量出发：徽章 80% + 宝物 60% 最大化收集")


def test_actual_travel():
    """测试实际旅行流程"""
    print("\n" + "="*60)
    print("实际旅行测试")
    print("="*60)

    # 初始化 API
    api = GameAPI()
    api.init_game()

    # 喂食到满能量
    print("\n步骤 1：喂食小猫到满能量...")
    foods_result = api.get_available_foods()
    if foods_result["success"]:
        # 喂金枪鱼罐头（+60）多次
        tuna_food = next((f for f in foods_result["foods"] if f["id"] == "tuna"), None)
        if tuna_food:
            for i in range(4):
                result = api.feed_cat("tuna")
                print(f"  喂食 {tuna_food['name']}: 能量 {result.get('new_energy', 0)}")

    # 获取可用地标
    print("\n步骤 2：选择地标...")
    landmarks_result = api.get_available_landmarks()
    if landmarks_result["success"] and landmarks_result["landmarks"]:
        landmark = landmarks_result["landmarks"][0]  # 选第一个地标
        print(f"  选择：{landmark['name']}")
        print(f"  需要能量：{landmark['min_energy']}")
        print(f"  消耗能量：{landmark['energy_cost']}")

    # 开始旅行
    print("\n步骤 3：开始旅行...")
    cat_status = api.get_cat_status()
    energy_before = cat_status["cat"]["current_energy"]
    print(f"  出发前能量：{energy_before}")

    travel_result = api.start_travel(landmark["id"])
    if travel_result["success"]:
        print(f"  ✓ {travel_result['message']}")
        print(f"  旅行时间：{travel_result['travel_info']['duration']:.1f} 秒")

    # 模拟旅行完成（直接调用 end_travel，不等待）
    print("\n步骤 4：旅行完成，获得奖励...")

    # 直接结束旅行获取奖励
    end_result = api.end_travel()
    if end_result["success"]:
        print(f"  ✓ {end_result['message']}")
        print(f"\n  获得奖励：")

        if end_result["rewards"]:
            for item in end_result["rewards"]:
                type_names = {
                    "postcard": "明信片",
                    "badge": "徽章",
                    "treasure": "宝物"
                }
                type_name = type_names.get(item["type"], item["type"])
                print(f"    - [{type_name}] {item['name']}")
        else:
            print("    (无奖励)")

    # 检查背包
    print("\n步骤 5：检查背包...")
    inventory_result = api.get_inventory()
    if inventory_result["success"]:
        total = inventory_result["total_count"]
        print(f"  背包中共有 {total} 种物品")

    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)


if __name__ == "__main__":
    # 测试概率计算
    test_reward_probabilities()

    # 测试实际旅行
    test_actual_travel()

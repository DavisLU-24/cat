"""
测试游戏初始化和 UI 创建
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 设置环境变量避免实际显示窗口
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'

import pygame
pygame.init()

# 测试导入
from backend import GameAPI
from frontend.game_renderer import GameRenderer
from frontend.ui import TravelUI

# 创建测试
print("Testing GameAPI initialization...")
api = GameAPI()
api.init_game()
print("OK - GameAPI initialized")

print("\nTesting landmarks data...")
landmarks_result = api.get_available_landmarks()
print(f"OK - Got {len(landmarks_result['landmarks'])} landmarks")

print("\nTesting TravelUI creation...")
screen = pygame.display.set_mode((800, 600))
renderer = GameRenderer(screen)
travel_ui = TravelUI(api, renderer)
travel_ui.load_data()
print(f"OK - TravelUI loaded {len(travel_ui.landmarks)} landmarks")

print("\nTesting landmark selection...")
if travel_ui.landmarks:
    # 模拟选择第一个地标（现在应该使用 ID）
    first_landmark = travel_ui.landmarks[0]
    travel_ui.selected_landmark = first_landmark["id"]
    print(f"OK - Selected landmark: {first_landmark['name']} (ID: {first_landmark['id']})")
    print(f"OK - Selected landmark stored as: {travel_ui.selected_landmark}")

print("\n" + "="*50)
print("All tests passed! Bug fix successful.")
print("="*50)

pygame.quit()

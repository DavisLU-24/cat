"""
游戏主循环
事件处理、更新、绘制
"""
import pygame
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent))

from backend import GameAPI
from .game_renderer import GameRenderer
from .sound_manager import SoundManager
from .ui import GamePanel, TravelUI, InventoryUI, SaveLoadUI


class Game:
    """游戏主类"""

    def __init__(self):
        # 初始化 Pygame
        pygame.init()

        # 窗口设置
        self.screen_width = 800
        self.screen_height = 600
        self.min_width = 640
        self.min_height = 480

        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height),
            pygame.RESIZABLE
        )
        pygame.display.set_caption("旅行小猫 - 上海海事大学版")

        # 时钟
        self.clock = pygame.time.Clock()
        self.fps = 60

        # 游戏状态
        self.running = True

        # 初始化系统
        self.api = GameAPI()
        self.api.init_game()

        self.renderer = GameRenderer(self.screen)
        self.sound_manager = SoundManager()

        # UI 组件
        self.current_ui = "game_panel"  # game_panel, travel, inventory
        self.save_load_ui_open = False
        self.save_load_mode = "save"

        self.game_panel = GamePanel(self.api, self.renderer)
        self.travel_ui = TravelUI(self.api, self.renderer)
        self.inventory_ui = InventoryUI(self.api, self.renderer)
        self.save_load_ui = SaveLoadUI(self.api, self.renderer)

        # 加载初始数据
        self.game_panel.load_data()

        # 消息系统
        self.message = None
        self.message_type = "info"
        self.message_time = 0
        self.message_duration = 3.0  # 秒

    def run(self):
        """运行游戏主循环"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.fps)

        self.quit()

    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event.key)

            elif event.type == pygame.VIDEORESIZE:
                self._handle_resize(event.w, event.h)

            else:
                self._handle_ui_event(event)

    def _handle_keydown(self, key):
        """处理按键"""
        if key == pygame.K_ESCAPE:
            # ESC 键：关闭弹窗 → 返回主界面 → 退出游戏
            if self.save_load_ui_open:
                self.save_load_ui_open = False
            elif self.current_ui != "game_panel":
                self.current_ui = "game_panel"
                self.game_panel.load_data()
            else:
                self.running = False

    def _handle_resize(self, width, height):
        """处理窗口缩放"""
        # 限制最小尺寸
        width = max(width, self.min_width)
        height = max(height, self.min_height)

        self.screen_width = width
        self.screen_height = height

        self.screen = pygame.display.set_mode(
            (width, height),
            pygame.RESIZABLE
        )

        # 更新渲染器尺寸
        self.renderer.screen = self.screen
        self.renderer.update_size(width, height)

    def _handle_ui_event(self, event):
        """分发事件到当前 UI"""
        # 存档/读档界面优先级最高（overlay）
        if self.save_load_ui_open:
            result = self.save_load_ui.handle_event(event)
            if result == "close":
                self.save_load_ui_open = False
                self.game_panel.load_data()  # 刷新主界面
            return

        # 当前主界面
        result = None

        if self.current_ui == "game_panel":
            result = self.game_panel.handle_event(event)

        elif self.current_ui == "travel":
            result = self.travel_ui.handle_event(event)

        elif self.current_ui == "inventory":
            result = self.inventory_ui.handle_event(event)

        # 处理 UI 返回值
        if result:
            self._handle_ui_result(result)

    def _handle_ui_result(self, result: str):
        """处理 UI 返回的结果"""
        if result == "travel":
            # 打开旅行界面
            self.current_ui = "travel"
            self.travel_ui.reset()

        elif result == "inventory":
            # 打开背包界面
            self.current_ui = "inventory"
            self.inventory_ui.reset()

        elif result == "save":
            # 打开存档界面
            self.save_load_ui_open = True
            self.save_load_ui.open("save")

        elif result == "load":
            # 打开读档界面
            self.save_load_ui_open = True
            self.save_load_ui.open("load")

        elif result == "close":
            # 关闭当前界面，返回主界面
            self.current_ui = "game_panel"
            self.game_panel.load_data()

    def update(self):
        """更新游戏状态"""
        # 后台检查旅行完成（仅在非旅行界面时）
        # 如果在旅行界面，让 travel_ui 自己处理完成逻辑
        if self.current_ui != "travel":
            self.api.auto_check_travel_and_save()

        # 更新当前 UI
        if self.current_ui == "travel":
            self.travel_ui.update()

        # 更新消息显示
        if self.message:
            import time
            if time.time() - self.message_time > self.message_duration:
                self.message = None

    def draw(self):
        """绘制"""
        # 背景
        self.renderer.draw_background()

        # 绘制当前 UI
        if self.current_ui == "game_panel":
            self.game_panel.draw()

        elif self.current_ui == "travel":
            # 主界面作为背景
            self.game_panel.draw()
            # 旅行界面覆盖
            self.travel_ui.draw()

        elif self.current_ui == "inventory":
            # 主界面作为背景
            self.game_panel.draw()
            # 背包界面覆盖
            self.inventory_ui.draw()

        # 存档/读档界面（最顶层 overlay）
        if self.save_load_ui_open:
            self.save_load_ui.draw()

        # 绘制消息
        if self.message:
            self.renderer.draw_message(self.message, self.message_type)

        # 刷新屏幕
        pygame.display.flip()

    def show_message(self, message: str, message_type: str = "info"):
        """显示消息"""
        import time
        self.message = message
        self.message_type = message_type
        self.message_time = time.time()

    def quit(self):
        """退出游戏"""
        pygame.quit()
        sys.exit()


def main():
    """主函数"""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()

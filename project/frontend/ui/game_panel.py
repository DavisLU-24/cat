"""
游戏主界面
包含食物区、小猫、能量条、功能按钮
"""
import pygame
from typing import Tuple, Optional


class GamePanel:
    """游戏主界面"""

    def __init__(self, api, renderer):
        self.api = api
        self.renderer = renderer

        # 布局参数（百分比）
        self.food_area_left = 0.06  # 食物区左边距
        self.food_area_width = 0.20  # 食物区宽度
        self.button_area_right = 0.22  # 按钮区右边距
        self.button_area_width = 0.16  # 按钮宽度

        # UI 状态
        self.foods = []
        self.hovered_food = None
        self.hovered_button = None
        self.cat_status = {}

        # 按钮区域
        self.buttons = {}

    def load_data(self):
        """加载数据"""
        result = self.api.get_available_foods()
        if result["success"]:
            self.foods = result["foods"]

        self.update_cat_status()

    def update_cat_status(self):
        """更新小猫状态"""
        result = self.api.get_cat_status()
        if result["success"]:
            self.cat_status = result["cat"]

    def handle_event(self, event) -> Optional[str]:
        """
        处理事件

        返回:
            None: 无操作
            "travel": 切换到旅行界面
            "inventory": 切换到背包界面
            "save": 打开存档界面
            "load": 打开读档界面
        """
        if event.type == pygame.MOUSEMOTION:
            self._handle_mouse_motion(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self._handle_click(event.pos)

        return None

    def _handle_mouse_motion(self, pos: Tuple[int, int]):
        """处理鼠标移动"""
        x, y = pos
        width = self.renderer.width
        height = self.renderer.height

        # 检查食物区
        self.hovered_food = None
        food_grid = self._calculate_food_grid()

        for i, food in enumerate(self.foods):
            if i < len(food_grid):
                rect = food_grid[i]
                if rect.collidepoint(x, y):
                    self.hovered_food = food
                    break

        # 检查按钮区
        self.hovered_button = None
        for button_name, rect in self.buttons.items():
            if rect.collidepoint(x, y):
                self.hovered_button = button_name
                break

    def _handle_click(self, pos: Tuple[int, int]) -> Optional[str]:
        """处理点击"""
        x, y = pos

        # 点击食物
        food_grid = self._calculate_food_grid()
        for i, food in enumerate(self.foods):
            if i < len(food_grid):
                rect = food_grid[i]
                if rect.collidepoint(x, y):
                    self._feed_cat(food)
                    return None

        # 点击按钮
        for button_name, rect in self.buttons.items():
            if rect.collidepoint(x, y):
                return button_name

        return None

    def _feed_cat(self, food: dict):
        """喂食小猫"""
        result = self.api.feed_cat(food["id"])
        # 刷新小猫状态
        self.update_cat_status()

    def _calculate_food_grid(self) -> list:
        """计算食物网格位置"""
        width = self.renderer.width
        height = self.renderer.height

        # 食物区域 - 扩大区域宽度
        area_x = int(width * self.food_area_left)
        area_width = int(width * 0.25)  # 从20%增加到25%
        area_y = int(height * 0.25)  # 从 25% 高度开始
        area_height = int(height * 0.60)  # 占 60% 高度

        # 网格：2 列 × 多行（从3列改为2列，避免格子太小）
        cols = 2
        cell_width = area_width // cols
        cell_height = int(height * 0.16)  # 进一步增加每格高度

        # 水平和垂直间距
        h_padding = int(width * 0.012)
        v_padding = int(height * 0.012)

        grid = []
        for i, food in enumerate(self.foods):
            row = i // cols
            col = i % cols

            x = area_x + col * cell_width + h_padding
            y = area_y + row * cell_height + v_padding
            w = cell_width - 2 * h_padding
            h = cell_height - 2 * v_padding

            grid.append(pygame.Rect(x, y, w, h))

        return grid

    def draw(self):
        """绘制主界面"""
        width = self.renderer.width
        height = self.renderer.height

        # 标题
        self.renderer.draw_text(
            "旅行小猫 - 上海海事大学版",
            width // 2,
            int(height * 0.08),
            "xlarge",
            self.renderer.colors["accent_color"]
        )

        # 绘制食物区
        self._draw_food_area()

        # 绘制小猫和能量条
        self._draw_cat_area()

        # 绘制功能按钮
        self._draw_button_area()

        # 绘制提示信息
        self._draw_info_area()

    def _draw_food_area(self):
        """绘制食物区"""
        width = self.renderer.width
        height = self.renderer.height

        # 区域标题
        title_x = int(width * (self.food_area_left + self.food_area_width / 2))
        title_y = int(height * 0.20)

        self.renderer.draw_text(
            "食物",
            title_x, title_y,
            "large",
            self.renderer.colors["text_color"]
        )

        # 绘制食物格子
        food_grid = self._calculate_food_grid()

        for i, food in enumerate(self.foods):
            if i < len(food_grid):
                rect = food_grid[i]
                is_hovered = (self.hovered_food == food)

                self.renderer.draw_food_item(
                    food,
                    rect.x, rect.y,
                    rect.width, rect.height,
                    is_hovered
                )

    def _draw_cat_area(self):
        """绘制小猫和能量条"""
        width = self.renderer.width
        height = self.renderer.height

        # 小猫位置：水平居中
        cat_x = width // 2
        cat_y = int(height * 0.40)
        cat_size = int(min(width, height) * 0.25)

        status = self.cat_status.get("status", "idle")
        self.renderer.draw_cat(status, cat_x, cat_y, cat_size)

        # 能量条 - 减小宽度避免与右侧按钮重叠
        bar_width = int(width * 0.38)  # 从50%减小到38%
        bar_height = int(height * 0.045)
        bar_x = (width - bar_width) // 2
        bar_y = int(height * 0.60)

        current_energy = self.cat_status.get("current_energy", 100)
        self.renderer.draw_energy_bar(bar_x, bar_y, bar_width, bar_height, current_energy)

        # 能量描述
        energy_desc = self.cat_status.get("energy_description", "")
        self.renderer.draw_text(
            energy_desc,
            width // 2,
            bar_y + bar_height + int(height * 0.04),
            "medium",
            self.renderer.colors["text_color"]
        )

    def _draw_button_area(self):
        """绘制功能按钮区"""
        width = self.renderer.width
        height = self.renderer.height

        # 按钮区域
        button_x = int(width * (1 - self.button_area_right))
        button_width = int(width * self.button_area_width)
        button_height = int(height * 0.08)
        button_spacing = int(height * 0.11)  # 按钮间距

        # 起始 Y 位置
        start_y = int(height * 0.25)

        buttons_config = [
            ("travel", "开始旅行"),
            ("inventory", "背包"),
            ("save", "存档"),
            ("load", "读档")
        ]

        self.buttons = {}

        for i, (button_name, button_text) in enumerate(buttons_config):
            y = start_y + i * button_spacing

            is_hovered = (self.hovered_button == button_name)

            rect = self.renderer.draw_button(
                button_text,
                button_x, y,
                button_width, button_height,
                is_hovered=is_hovered
            )

            self.buttons[button_name] = rect

    def _draw_info_area(self):
        """绘制底部信息"""
        width = self.renderer.width
        height = self.renderer.height

        # 建议文字
        suggestion = self.cat_status.get("energy_suggestion", "")
        self.renderer.draw_text(
            suggestion,
            width // 2,
            int(height * 0.92),
            "small",
            self.renderer.colors["text_color"]
        )

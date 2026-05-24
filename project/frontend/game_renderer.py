"""
游戏渲染器
提供配色方案和所有 UI 原语
"""
import pygame
import os
from pathlib import Path
from typing import Tuple, Optional


class GameRenderer:
    """游戏渲染器"""

    # 配色方案
    colors = {
        # 基础配色
        "bg_color": (240, 248, 255),  # 爱丽丝蓝
        "panel_color": (255, 255, 255),  # 白色卡片
        "text_color": (51, 51, 51),  # 深灰
        "accent_color": (70, 130, 180),  # 钢蓝
        "energy_color": (70, 130, 180),  # 同强调色

        # 状态配色
        "success_color": (60, 179, 113),  # 海洋绿
        "error_color": (220, 20, 60),  # 猩红

        # 物品配色
        "postcard_color": (255, 182, 193),  # 浅粉
        "badge_color": (255, 215, 0),  # 金色
        "treasure_color": (138, 43, 226),  # 紫罗兰

        # 辅助配色
        "hover_color": (50, 100, 150),  # 按钮 hover
        "disabled_color": (180, 180, 180),  # 禁用
        "border_color": (200, 200, 200),  # 边框
        "overlay_color": (0, 0, 0, 180),  # 半透明遮罩
        "shadow_color": (0, 0, 0, 50),  # 阴影
    }

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.width, self.height = screen.get_size()

        # 字体
        self.fonts = {}
        self._init_fonts()

        # 背景图
        self.background_image = None
        self._load_background()

    def _init_fonts(self):
        """初始化字体"""
        # 四级字号：small, medium, large, xlarge
        # 字号根据屏幕高度缩放
        base_height = 600
        scale = self.height / base_height

        sizes = {
            "small": int(20 * scale),
            "medium": int(24 * scale),
            "large": int(32 * scale),
            "xlarge": int(48 * scale)
        }

        # 尝试加载中文字体
        font_name = None
        try:
            # Windows
            if os.name == 'nt':
                font_name = "SimHei"  # 黑体
            # 其他系统
            else:
                font_name = None  # 使用默认字体
        except:
            font_name = None

        for size_name, size_value in sizes.items():
            try:
                if font_name:
                    self.fonts[size_name] = pygame.font.SysFont(font_name, size_value)
                else:
                    self.fonts[size_name] = pygame.font.Font(None, size_value)
            except:
                self.fonts[size_name] = pygame.font.Font(None, size_value)

    def _load_background(self):
        """加载背景图"""
        try:
            project_root = Path(__file__).parent.parent
            bg_path = project_root / "assets" / "images" / "background.png"

            if bg_path.exists():
                self.background_image = pygame.image.load(str(bg_path))
                self.background_image = pygame.transform.scale(
                    self.background_image,
                    (self.width, self.height)
                )
        except:
            self.background_image = None

    def update_size(self, width: int, height: int):
        """更新窗口尺寸（响应窗口缩放）"""
        self.width = width
        self.height = height
        self._init_fonts()

        # 重新缩放背景
        if self.background_image:
            try:
                project_root = Path(__file__).parent.parent
                bg_path = project_root / "assets" / "images" / "background.png"
                if bg_path.exists():
                    original_bg = pygame.image.load(str(bg_path))
                    self.background_image = pygame.transform.scale(
                        original_bg,
                        (width, height)
                    )
            except:
                pass

    # ==================== 基础绘制 ====================

    def draw_background(self):
        """绘制背景"""
        if self.background_image:
            self.screen.blit(self.background_image, (0, 0))
        else:
            self.screen.fill(self.colors["bg_color"])

    def draw_panel(
        self,
        x: int, y: int,
        width: int, height: int,
        color: Optional[Tuple[int, int, int]] = None,
        border_radius: int = 15,
        alpha: int = 255
    ):
        """绘制圆角面板"""
        if color is None:
            color = self.colors["panel_color"]

        # 创建带透明度的表面
        panel_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(
            panel_surface,
            (*color, alpha),
            (0, 0, width, height),
            border_radius=border_radius
        )
        self.screen.blit(panel_surface, (x, y))

    def draw_button(
        self,
        text: str,
        x: int, y: int,
        width: int, height: int,
        is_hovered: bool = False,
        is_disabled: bool = False,
        font_size: str = "medium"
    ) -> pygame.Rect:
        """
        绘制按钮

        返回按钮的 Rect，用于碰撞检测
        """
        # 按钮颜色
        if is_disabled:
            color = self.colors["disabled_color"]
        elif is_hovered:
            color = self.colors["hover_color"]
        else:
            color = self.colors["accent_color"]

        # 绘制圆角矩形
        pygame.draw.rect(
            self.screen,
            color,
            (x, y, width, height),
            border_radius=10
        )

        # 绘制文本
        self.draw_text(
            text,
            x + width // 2,
            y + height // 2,
            font_size,
            (255, 255, 255),
            align="center"
        )

        return pygame.Rect(x, y, width, height)

    def draw_text(
        self,
        text: str,
        x: int, y: int,
        font_size: str = "medium",
        color: Optional[Tuple[int, int, int]] = None,
        align: str = "center"
    ):
        """
        绘制文本

        align: "left", "center", "right"
        """
        if color is None:
            color = self.colors["text_color"]

        font = self.fonts.get(font_size, self.fonts["medium"])
        text_surface = font.render(str(text), True, color)
        text_rect = text_surface.get_rect()

        # 对齐
        if align == "center":
            text_rect.center = (x, y)
        elif align == "left":
            text_rect.midleft = (x, y)
        elif align == "right":
            text_rect.midright = (x, y)

        self.screen.blit(text_surface, text_rect)

    # ==================== 特殊组件 ====================

    def draw_energy_bar(
        self,
        x: int, y: int,
        width: int, height: int,
        energy: int,
        max_energy: int = 200
    ):
        """绘制能量条"""
        # 背景
        pygame.draw.rect(
            self.screen,
            self.colors["border_color"],
            (x, y, width, height),
            border_radius=int(height * 0.5)
        )

        # 能量值
        if energy > 0:
            fill_width = int(width * (energy / max_energy))
            pygame.draw.rect(
                self.screen,
                self.colors["energy_color"],
                (x, y, fill_width, height),
                border_radius=int(height * 0.5)
            )

        # 文本
        self.draw_text(
            f"{energy}/{max_energy}",
            x + width // 2,
            y + height // 2,
            "small",
            (255, 255, 255)
        )

    def draw_progress_bar(
        self,
        x: int, y: int,
        width: int, height: int,
        progress: float,
        color: Optional[Tuple[int, int, int]] = None
    ):
        """
        绘制进度条

        progress: 0.0 ~ 1.0
        """
        if color is None:
            color = self.colors["success_color"]

        # 背景
        pygame.draw.rect(
            self.screen,
            self.colors["border_color"],
            (x, y, width, height),
            border_radius=int(height * 0.5)
        )

        # 进度
        progress = max(0.0, min(1.0, progress))
        if progress > 0:
            fill_width = int(width * progress)
            pygame.draw.rect(
                self.screen,
                color,
                (x, y, fill_width, height),
                border_radius=int(height * 0.5)
            )

    def draw_cat(
        self,
        status: str,
        x: int, y: int,
        size: int = 200
    ):
        """
        绘制小猫

        status: idle, eating, traveling, returning
        """
        # 尝试加载图片
        try:
            project_root = Path(__file__).parent.parent
            img_path = project_root / "assets" / "images" / f"cat_{status}.png"

            if img_path.exists():
                image = pygame.image.load(str(img_path))
                image = pygame.transform.scale(image, (size, size))
                image_rect = image.get_rect(center=(x, y))
                self.screen.blit(image, image_rect)
                return
        except:
            pass

        # 占位图：灰色圆形
        pygame.draw.circle(
            self.screen,
            self.colors["disabled_color"],
            (x, y),
            size // 2
        )

    def draw_item_icon(
        self,
        item_type: str,
        x: int, y: int,
        size: int = 50,
        quantity: int = 1
    ):
        """
        绘制物品图标

        item_type: postcard, badge, treasure
        """
        # 根据类型选择颜色
        type_colors = {
            "postcard": self.colors["postcard_color"],
            "badge": self.colors["badge_color"],
            "treasure": self.colors["treasure_color"]
        }
        color = type_colors.get(item_type, self.colors["disabled_color"])

        # 绘制圆角方块
        pygame.draw.rect(
            self.screen,
            color,
            (x, y, size, size),
            border_radius=10
        )

        # 如果数量 > 1，显示数字
        if quantity > 1:
            self.draw_text(
                f"×{quantity}",
                x + size - 5,
                y + size - 5,
                "small",
                (255, 255, 255),
                align="right"
            )

    def draw_food_item(
        self,
        food: dict,
        x: int, y: int,
        width: int, height: int,
        is_hovered: bool = False
    ) -> pygame.Rect:
        """绘制食物格子"""
        # 背景
        color = self.colors["hover_color"] if is_hovered else self.colors["panel_color"]
        pygame.draw.rect(
            self.screen,
            color,
            (x, y, width, height),
            border_radius=10
        )

        # 边框
        pygame.draw.rect(
            self.screen,
            self.colors["border_color"],
            (x, y, width, height),
            width=2,
            border_radius=10
        )

        # 食物名称 - 上部显示，留足边距
        name_y = y + int(height * 0.30)
        self.draw_text(
            food["name"],
            x + width // 2,
            name_y,
            "small",
            self.colors["text_color"]
        )

        # 能量值 - 下部显示，与名称保持足够间距
        energy_y = y + int(height * 0.70)
        self.draw_text(
            f"+{food['energy_value']}",
            x + width // 2,
            energy_y,
            "small",
            self.colors["success_color"]
        )

        return pygame.Rect(x, y, width, height)

    # ==================== 消息提示 ====================

    def draw_message(
        self,
        message: str,
        message_type: str = "info"
    ):
        """
        绘制顶部消息提示

        message_type: info, success, error
        """
        # 颜色
        type_colors = {
            "info": self.colors["text_color"],
            "success": self.colors["success_color"],
            "error": self.colors["error_color"]
        }
        bg_color = type_colors.get(message_type, self.colors["text_color"])

        # 消息框尺寸
        padding = 20
        msg_height = 60
        msg_width = self.width * 0.6

        # 位置：顶部居中
        x = (self.width - msg_width) // 2
        y = 20

        # 绘制背景
        self.draw_panel(x, y, msg_width, msg_height, bg_color, alpha=230)

        # 绘制文本
        self.draw_text(
            message,
            x + msg_width // 2,
            y + msg_height // 2,
            "medium",
            (255, 255, 255)
        )

    def draw_overlay(self, alpha: int = 180):
        """绘制半透明遮罩"""
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        self.screen.blit(overlay, (0, 0))

    def draw_close_button(self, x: int, y: int, size: int = 40) -> pygame.Rect:
        """绘制关闭按钮"""
        # 圆形背景
        pygame.draw.circle(
            self.screen,
            self.colors["error_color"],
            (x, y),
            size // 2
        )

        # X 符号
        self.draw_text(
            "×",
            x, y,
            "large",
            (255, 255, 255)
        )

        return pygame.Rect(x - size // 2, y - size // 2, size, size)

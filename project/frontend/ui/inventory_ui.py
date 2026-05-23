"""
背包界面
四个 Tab：明信片 / 徽章 / 宝物 / 收集进度
"""
import pygame
from typing import Optional


class InventoryUI:
    """背包界面"""

    def __init__(self, api, renderer):
        self.api = api
        self.renderer = renderer

        # 当前 Tab：postcards, badges, treasures, progress
        self.current_tab = "postcards"

        # 数据
        self.inventory = {}
        self.progress = {}

        # UI 元素
        self.tab_rects = {}
        self.close_button_rect = None

    def load_data(self):
        """加载数据"""
        # 加载背包
        result = self.api.get_inventory()
        if result["success"]:
            self.inventory = result["inventory"]

        # 加载进度
        progress_result = self.api.get_collection_progress()
        if progress_result["success"]:
            self.progress = progress_result["progress"]

    def reset(self):
        """重置"""
        self.current_tab = "postcards"
        self.load_data()

    def handle_event(self, event) -> Optional[str]:
        """
        处理事件

        返回:
            "close": 关闭界面
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self._handle_click(event.pos)

        return None

    def _handle_click(self, pos) -> Optional[str]:
        """处理点击"""
        # 关闭按钮
        if self.close_button_rect and self.close_button_rect.collidepoint(pos):
            return "close"

        # Tab 切换
        for tab_name, rect in self.tab_rects.items():
            if rect.collidepoint(pos):
                self.current_tab = tab_name
                return None

        return None

    def draw(self):
        """绘制"""
        # 遮罩
        self.renderer.draw_overlay()

        # 主面板
        width = self.renderer.width
        height = self.renderer.height

        panel_width = int(width * 0.90)
        panel_height = int(height * 0.90)
        panel_x = (width - panel_width) // 2
        panel_y = (height - panel_height) // 2

        self.renderer.draw_panel(panel_x, panel_y, panel_width, panel_height)

        # 关闭按钮
        close_x = panel_x + panel_width - 30
        close_y = panel_y + 30
        self.close_button_rect = self.renderer.draw_close_button(close_x, close_y)

        # 标题
        self.renderer.draw_text(
            "背包",
            panel_x + panel_width // 2,
            panel_y + int(panel_height * 0.08),
            "xlarge",
            self.renderer.colors["accent_color"]
        )

        # Tab 栏
        self._draw_tabs(panel_x, panel_y, panel_width, panel_height)

        # 内容区
        self._draw_content(panel_x, panel_y, panel_width, panel_height)

    def _draw_tabs(self, px, py, pw, ph):
        """绘制 Tab 栏"""
        tabs = [
            ("postcards", "明信片"),
            ("badges", "徽章"),
            ("treasures", "宝物"),
            ("progress", "收集进度")
        ]

        tab_width = int(pw * 0.20)
        tab_height = int(ph * 0.06)
        tab_spacing = int(pw * 0.02)
        tab_y = py + int(ph * 0.16)

        total_width = len(tabs) * tab_width + (len(tabs) - 1) * tab_spacing
        start_x = px + (pw - total_width) // 2

        self.tab_rects = {}

        for i, (tab_name, tab_text) in enumerate(tabs):
            x = start_x + i * (tab_width + tab_spacing)

            # 背景色
            if self.current_tab == tab_name:
                color = self.renderer.colors["accent_color"]
                text_color = (255, 255, 255)
            else:
                color = (220, 220, 220)
                text_color = self.renderer.colors["text_color"]

            rect = pygame.Rect(x, tab_y, tab_width, tab_height)
            pygame.draw.rect(self.renderer.screen, color, rect, border_radius=10)

            self.renderer.draw_text(
                tab_text,
                x + tab_width // 2,
                tab_y + tab_height // 2,
                "medium",
                text_color
            )

            self.tab_rects[tab_name] = rect

    def _draw_content(self, px, py, pw, ph):
        """绘制内容区"""
        if self.current_tab == "progress":
            self._draw_progress(px, py, pw, ph)
        else:
            self._draw_items(px, py, pw, ph)

    def _draw_items(self, px, py, pw, ph):
        """绘制物品列表"""
        # 获取当前 Tab 的物品
        items = self.inventory.get(self.current_tab, [])

        if not items:
            # 无物品
            self.renderer.draw_text(
                "还没有收集到任何物品",
                px + pw // 2,
                py + ph // 2,
                "large",
                self.renderer.colors["text_color"]
            )
            return

        # 物品网格
        content_y = py + int(ph * 0.26)
        content_height = int(ph * 0.64)

        cols = 5
        rows = (len(items) + cols - 1) // cols

        item_size = int(min(pw / cols * 0.85, content_height / max(rows, 3) * 0.85))
        padding_x = (pw - cols * item_size) // (cols + 1)
        padding_y = int(ph * 0.02)

        for i, item in enumerate(items):
            row = i // cols
            col = i % cols

            x = px + padding_x + col * (item_size + padding_x)
            y = content_y + row * (item_size + padding_y * 2)

            # 绘制物品图标
            quantity = item.get("quantity", 1)
            self.renderer.draw_item_icon(
                item["type"],
                x, y,
                item_size,
                quantity
            )

            # 物品名称
            self.renderer.draw_text(
                item["name"],
                x + item_size // 2,
                y + item_size + int(ph * 0.02),
                "small",
                self.renderer.colors["text_color"]
            )

    def _draw_progress(self, px, py, pw, ph):
        """绘制收集进度"""
        content_y = py + int(ph * 0.26)

        # 总体进度
        total = self.progress.get("total_items", 0)
        collected = self.progress.get("collected_items", 0)
        percentage = self.progress.get("progress_percentage", 0.0)

        self.renderer.draw_text(
            f"总进度：{collected}/{total} ({percentage}%)",
            px + pw // 2,
            content_y + int(ph * 0.05),
            "large",
            self.renderer.colors["accent_color"]
        )

        # 按类型统计
        by_type = self.progress.get("by_type", {})

        type_names = {
            "postcard": "明信片",
            "badge": "徽章",
            "treasure": "宝物"
        }

        type_y = content_y + int(ph * 0.15)
        type_spacing = int(ph * 0.08)

        for i, (item_type, type_name) in enumerate(type_names.items()):
            type_data = by_type.get(item_type, {})
            type_collected = type_data.get("collected", 0)
            type_total = type_data.get("total", 0)
            type_percentage = type_data.get("percentage", 0.0)

            y = type_y + i * type_spacing

            # 文本
            self.renderer.draw_text(
                f"{type_name}：{type_collected}/{type_total} ({type_percentage}%)",
                px + int(pw * 0.25),
                y,
                "medium",
                self.renderer.colors["text_color"],
                align="left"
            )

            # 进度条
            bar_width = int(pw * 0.50)
            bar_height = int(ph * 0.03)
            bar_x = px + int(pw * 0.25)
            bar_y = y + int(ph * 0.03)

            self.renderer.draw_progress_bar(
                bar_x, bar_y,
                bar_width, bar_height,
                type_percentage / 100.0
            )

        # 按地标统计
        by_landmark = self.progress.get("by_landmark", {})

        landmark_y = type_y + int(ph * 0.35)

        self.renderer.draw_text(
            "地标收集进度",
            px + pw // 2,
            landmark_y,
            "large",
            self.renderer.colors["accent_color"]
        )

        landmark_list_y = landmark_y + int(ph * 0.06)
        landmark_spacing = int(ph * 0.06)

        for i, (landmark_id, landmark_data) in enumerate(by_landmark.items()):
            landmark_name = landmark_data.get("name", landmark_id)
            landmark_collected = landmark_data.get("collected", 0)
            landmark_total = landmark_data.get("total", 0)
            landmark_percentage = landmark_data.get("percentage", 0.0)

            y = landmark_list_y + i * landmark_spacing

            # 文本
            text = f"{landmark_name}：{landmark_collected}/{landmark_total} ({landmark_percentage}%)"

            self.renderer.draw_text(
                text,
                px + int(pw * 0.15),
                y,
                "small",
                self.renderer.colors["text_color"],
                align="left"
            )

            # 小进度条
            bar_width = int(pw * 0.30)
            bar_height = int(ph * 0.02)
            bar_x = px + int(pw * 0.55)
            bar_y = y - bar_height // 2

            self.renderer.draw_progress_bar(
                bar_x, bar_y,
                bar_width, bar_height,
                landmark_percentage / 100.0
            )

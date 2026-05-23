"""
存档/读档界面
10 个槽位列表
"""
import pygame
from typing import Optional


class SaveLoadUI:
    """存档/读档界面"""

    def __init__(self, api, renderer):
        self.api = api
        self.renderer = renderer

        # 模式：save 或 load
        self.mode = "save"

        # 数据
        self.slots = []

        # UI 元素
        self.slot_rects = {}
        self.close_button_rect = None
        self.hovered_slot = None

    def open(self, mode: str):
        """
        打开界面

        mode: "save" 或 "load"
        """
        self.mode = mode
        self.load_data()

    def load_data(self):
        """加载存档槽位信息"""
        result = self.api.get_save_slots_info()
        if result["success"]:
            self.slots = result["slots"]

    def handle_event(self, event) -> Optional[str]:
        """
        处理事件

        返回:
            "close": 关闭界面
        """
        if event.type == pygame.MOUSEMOTION:
            self._handle_mouse_motion(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self._handle_click(event.pos)

        return None

    def _handle_mouse_motion(self, pos):
        """处理鼠标移动"""
        self.hovered_slot = None
        for slot_id, rect in self.slot_rects.items():
            if rect.collidepoint(pos):
                self.hovered_slot = slot_id
                break

    def _handle_click(self, pos) -> Optional[str]:
        """处理点击"""
        # 关闭按钮
        if self.close_button_rect and self.close_button_rect.collidepoint(pos):
            return "close"

        # 点击槽位
        for slot_id, rect in self.slot_rects.items():
            if rect.collidepoint(pos):
                self._handle_slot_click(slot_id)
                return None

        return None

    def _handle_slot_click(self, slot_id: int):
        """处理槽位点击"""
        if self.mode == "save":
            # 存档
            result = self.api.save_game(slot_id)
            if result["success"]:
                self.load_data()  # 刷新列表

        elif self.mode == "load":
            # 读档
            slot = self._get_slot_by_id(slot_id)
            if slot and slot["is_occupied"]:
                result = self.api.load_game(slot_id)
                if result["success"]:
                    # 加载成功后刷新数据
                    pass

    def _get_slot_by_id(self, slot_id: int):
        """根据 ID 获取槽位"""
        for slot in self.slots:
            if slot["slot_id"] == slot_id:
                return slot
        return None

    def draw(self):
        """绘制"""
        # 遮罩
        self.renderer.draw_overlay()

        # 主面板
        width = self.renderer.width
        height = self.renderer.height

        panel_width = int(width * 0.70)
        panel_height = int(height * 0.85)
        panel_x = (width - panel_width) // 2
        panel_y = (height - panel_height) // 2

        self.renderer.draw_panel(panel_x, panel_y, panel_width, panel_height)

        # 关闭按钮
        close_x = panel_x + panel_width - 30
        close_y = panel_y + 30
        self.close_button_rect = self.renderer.draw_close_button(close_x, close_y)

        # 标题
        title = "保存游戏" if self.mode == "save" else "加载游戏"
        self.renderer.draw_text(
            title,
            panel_x + panel_width // 2,
            panel_y + int(panel_height * 0.08),
            "xlarge",
            self.renderer.colors["accent_color"]
        )

        # 槽位列表
        self._draw_slots(panel_x, panel_y, panel_width, panel_height)

    def _draw_slots(self, px, py, pw, ph):
        """绘制槽位列表"""
        list_y = py + int(ph * 0.18)
        slot_height = int(ph * 0.07)
        slot_spacing = int(ph * 0.01)

        self.slot_rects = {}

        for i, slot in enumerate(self.slots):
            slot_id = slot["slot_id"]
            is_occupied = slot["is_occupied"]

            y = list_y + i * (slot_height + slot_spacing)

            # 背景色
            if self.hovered_slot == slot_id:
                if self.mode == "load" and not is_occupied:
                    bg_color = self.renderer.colors["disabled_color"]
                else:
                    bg_color = self.renderer.colors["hover_color"]
            else:
                if self.mode == "load" and not is_occupied:
                    bg_color = (240, 240, 240)
                else:
                    bg_color = (250, 250, 250)

            rect = pygame.Rect(px + int(pw * 0.08), y, int(pw * 0.84), slot_height)
            pygame.draw.rect(self.renderer.screen, bg_color, rect, border_radius=10)

            # 边框
            border_color = self.renderer.colors["border_color"]
            pygame.draw.rect(self.renderer.screen, border_color, rect, width=2, border_radius=10)

            # 槽位信息
            text_color = (255, 255, 255) if self.hovered_slot == slot_id else self.renderer.colors["text_color"]

            # 槽位编号
            self.renderer.draw_text(
                f"槽位 {slot_id}",
                rect.x + int(rect.width * 0.12),
                rect.centery,
                "medium",
                text_color,
                align="left"
            )

            # 存档信息
            if is_occupied:
                game_time = slot.get("game_time", 0)
                save_time = slot.get("save_time", "")

                # 游戏时间
                hours = int(game_time // 3600)
                minutes = int((game_time % 3600) // 60)
                time_text = f"游戏时间：{hours}h {minutes}m"

                self.renderer.draw_text(
                    time_text,
                    rect.x + int(rect.width * 0.45),
                    rect.centery,
                    "small",
                    text_color,
                    align="left"
                )

                # 保存时间
                if save_time:
                    # 提取日期时间（去掉毫秒）
                    save_time_str = save_time.split('.')[0] if '.' in save_time else save_time

                    self.renderer.draw_text(
                        save_time_str,
                        rect.x + int(rect.width * 0.88),
                        rect.centery,
                        "small",
                        text_color,
                        align="right"
                    )
            else:
                self.renderer.draw_text(
                    "空槽位",
                    rect.x + int(rect.width * 0.50),
                    rect.centery,
                    "medium",
                    self.renderer.colors["disabled_color"],
                    align="left"
                )

            self.slot_rects[slot_id] = rect

        # 提示文字
        hint_y = py + ph - int(ph * 0.08)
        if self.mode == "save":
            hint_text = "点击槽位保存游戏"
        else:
            hint_text = "点击已有存档的槽位加载游戏"

        self.renderer.draw_text(
            hint_text,
            px + pw // 2,
            hint_y,
            "small",
            self.renderer.colors["text_color"]
        )

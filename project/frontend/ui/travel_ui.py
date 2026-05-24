"""
旅行界面
三态状态机：selecting → traveling → completed
"""
import pygame
import time
from typing import Optional


class TravelUI:
    """旅行界面"""

    def __init__(self, api, renderer):
        self.api = api
        self.renderer = renderer

        # 状态：selecting, traveling, completed
        self.state = "selecting"

        # 数据
        self.landmarks = []
        self.selected_landmark = None
        self.travel_info = {}
        self.rewards = []

        # UI 元素
        self.landmark_rects = {}
        self.hovered_landmark = None
        self.start_button_rect = None
        self.cancel_button_rect = None
        self.return_button_rect = None
        self.random_button_rect = None
        self.close_button_rect = None

    def load_data(self):
        """加载数据"""
        result = self.api.get_available_landmarks()
        if result["success"]:
            self.landmarks = result["landmarks"]

    def reset(self):
        """重置状态"""
        self.state = "selecting"
        self.selected_landmark = None
        self.travel_info = {}
        self.rewards = []
        self.load_data()

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
        # 检查地标列表
        self.hovered_landmark = None
        for landmark_id, rect in self.landmark_rects.items():
            if rect.collidepoint(pos):
                self.hovered_landmark = landmark_id
                break

    def _handle_click(self, pos) -> Optional[str]:
        """处理点击"""
        # 关闭按钮
        if self.close_button_rect and self.close_button_rect.collidepoint(pos):
            return "close"

        if self.state == "selecting":
            return self._handle_selecting_click(pos)
        elif self.state == "traveling":
            return self._handle_traveling_click(pos)
        elif self.state == "completed":
            return self._handle_completed_click(pos)

        return None

    def _handle_selecting_click(self, pos) -> Optional[str]:
        """选择地标阶段的点击"""
        # 点击地标
        for landmark_id, rect in self.landmark_rects.items():
            if rect.collidepoint(pos):
                self.selected_landmark = landmark_id
                return None

        # 开始旅行按钮
        if self.start_button_rect and self.start_button_rect.collidepoint(pos):
            if self.selected_landmark:
                self._start_travel()
            return None

        # 随机旅行按钮
        if self.random_button_rect and self.random_button_rect.collidepoint(pos):
            self._start_random_travel()
            return None

        return None

    def _handle_traveling_click(self, pos) -> Optional[str]:
        """旅行中阶段的点击"""
        # 取消旅行按钮
        if self.cancel_button_rect and self.cancel_button_rect.collidepoint(pos):
            self._cancel_travel()
            return None

        return None

    def _handle_completed_click(self, pos) -> Optional[str]:
        """完成阶段的点击"""
        # 返回按钮
        if self.return_button_rect and self.return_button_rect.collidepoint(pos):
            self.reset()
            return None

        return None

    def _start_travel(self):
        """开始旅行"""
        if not self.selected_landmark:
            return

        result = self.api.start_travel(self.selected_landmark)

        if result["success"]:
            self.state = "traveling"
            self.travel_info = result["travel_info"]

    def _start_random_travel(self):
        """随机旅行"""
        result = self.api.start_random_travel()

        if result["success"]:
            self.state = "traveling"
            self.travel_info = result["travel_info"]
            # 找到对应的地标
            for landmark in self.landmarks:
                if landmark["name"] == result["travel_info"]["landmark_name"]:
                    self.selected_landmark = landmark["id"]
                    break

    def _cancel_travel(self):
        """取消旅行"""
        result = self.api.cancel_travel()

        if result["success"]:
            self.reset()

    def update(self):
        """更新（在 traveling 状态检查进度）"""
        if self.state == "traveling":
            result = self.api.check_travel_status()

            if result["is_completed"]:
                # 自动完成旅行
                end_result = self.api.end_travel()

                if end_result["success"]:
                    self.rewards = end_result["rewards"]
                    self.state = "completed"

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

        # 根据状态绘制
        if self.state == "selecting":
            self._draw_selecting(panel_x, panel_y, panel_width, panel_height)
        elif self.state == "traveling":
            self._draw_traveling(panel_x, panel_y, panel_width, panel_height)
        elif self.state == "completed":
            self._draw_completed(panel_x, panel_y, panel_width, panel_height)

    def _draw_selecting(self, px, py, pw, ph):
        """绘制选择地标阶段"""
        # 标题
        self.renderer.draw_text(
            "选择旅行地点",
            px + pw // 2,
            py + int(ph * 0.08),
            "xlarge",
            self.renderer.colors["accent_color"]
        )

        # 地标列表
        list_y = py + int(ph * 0.18)
        item_height = int(ph * 0.10)
        item_spacing = int(ph * 0.02)

        self.landmark_rects = {}

        for i, landmark in enumerate(self.landmarks):
            y = list_y + i * (item_height + item_spacing)

            # 检查是否可访问
            can_visit = landmark.get("can_visit", False)
            is_selected = (self.selected_landmark == landmark["id"])

            # 背景色
            if not can_visit:
                bg_color = self.renderer.colors["disabled_color"]
            elif is_selected:
                bg_color = self.renderer.colors["accent_color"]
            elif self.hovered_landmark == landmark["id"]:
                bg_color = self.renderer.colors["hover_color"]
            else:
                bg_color = (230, 230, 230)

            rect = pygame.Rect(px + int(pw * 0.10), y, int(pw * 0.80), item_height)
            pygame.draw.rect(self.renderer.screen, bg_color, rect, border_radius=10)

            # 文本
            text_color = (255, 255, 255) if (is_selected or not can_visit) else self.renderer.colors["text_color"]

            self.renderer.draw_text(
                landmark["name"],
                rect.x + int(rect.width * 0.20),
                rect.centery,
                "large",
                text_color,
                align="left"
            )

            # 能量需求
            energy_text = f"需要 {landmark['min_energy']} 能量"
            self.renderer.draw_text(
                energy_text,
                rect.x + int(rect.width * 0.70),
                rect.centery,
                "medium",
                text_color,
                align="left"
            )

            self.landmark_rects[landmark["id"]] = rect

        # 按钮区
        button_y = py + ph - int(ph * 0.15)
        button_width = int(pw * 0.30)
        button_height = int(ph * 0.08)
        button_spacing = int(pw * 0.05)

        # 开始旅行按钮
        start_x = px + pw // 2 - button_width - button_spacing // 2
        self.start_button_rect = self.renderer.draw_button(
            "开始旅行",
            start_x, button_y,
            button_width, button_height,
            is_disabled=(not self.selected_landmark)
        )

        # 随机旅行按钮
        random_x = px + pw // 2 + button_spacing // 2
        self.random_button_rect = self.renderer.draw_button(
            "随机旅行",
            random_x, button_y,
            button_width, button_height
        )

    def _draw_traveling(self, px, py, pw, ph):
        """绘制旅行中阶段"""
        # 标题
        landmark_name = self.travel_info.get("landmark_name", "未知地点")
        self.renderer.draw_text(
            f"正在旅行：{landmark_name}",
            px + pw // 2,
            py + int(ph * 0.15),
            "xlarge",
            self.renderer.colors["accent_color"]
        )

        # 小猫图（旅行状态）
        cat_size = int(min(pw, ph) * 0.30)
        self.renderer.draw_cat(
            "traveling",
            px + pw // 2,
            py + int(ph * 0.40),
            cat_size
        )

        # 进度条
        result = self.api.check_travel_status()
        progress = result.get("progress", 0.0)
        remaining_time = result.get("remaining_time", 0.0)

        bar_width = int(pw * 0.60)
        bar_height = int(ph * 0.05)
        bar_x = px + (pw - bar_width) // 2
        bar_y = py + int(ph * 0.60)

        self.renderer.draw_progress_bar(bar_x, bar_y, bar_width, bar_height, progress)

        # 剩余时间
        self.renderer.draw_text(
            f"剩余时间：{int(remaining_time)} 秒",
            px + pw // 2,
            bar_y + bar_height + int(ph * 0.05),
            "large",
            self.renderer.colors["text_color"]
        )

        # 取消按钮
        button_width = int(pw * 0.25)
        button_height = int(ph * 0.08)
        cancel_x = px + (pw - button_width) // 2
        cancel_y = py + ph - int(ph * 0.15)

        self.cancel_button_rect = self.renderer.draw_button(
            "取消旅行",
            cancel_x, cancel_y,
            button_width, button_height
        )

    def _draw_completed(self, px, py, pw, ph):
        """绘制完成阶段"""
        # 标题
        self.renderer.draw_text(
            "旅行归来！",
            px + pw // 2,
            py + int(ph * 0.10),
            "xlarge",
            self.renderer.colors["success_color"]
        )

        # 小猫图（返回状态）
        cat_size = int(min(pw, ph) * 0.25)
        self.renderer.draw_cat(
            "returning",
            px + pw // 2,
            py + int(ph * 0.30),
            cat_size
        )

        # 奖励展示
        reward_title_y = py + int(ph * 0.50)

        self.renderer.draw_text(
            "获得奖励：",
            px + pw // 2,
            reward_title_y,
            "large",
            self.renderer.colors["text_color"]
        )

        # 计算奖励区域的实际高度，用于动态调整返回按钮位置
        reward_bottom_y = reward_title_y + int(ph * 0.10)  # 默认值

        # 奖励物品
        if self.rewards:
            item_size = int(min(pw, ph) * 0.12)
            items_per_row = 2  # 每行2个物品

            # 间距
            h_spacing = int(pw * 0.15)
            v_spacing = int(ph * 0.16)  # 稍微减小垂直间距，避免超出边界

            reward_start_y = reward_title_y + int(ph * 0.10)

            # 计算总行数
            total_rows = (len(self.rewards) + items_per_row - 1) // items_per_row

            for i, item in enumerate(self.rewards):
                # 计算当前是第几行第几列
                row = i // items_per_row
                col = i % items_per_row

                # 计算当前行有多少个物品
                items_in_current_row = min(items_per_row, len(self.rewards) - row * items_per_row)

                # 计算当前行的总宽度
                row_total_width = items_in_current_row * item_size + (items_in_current_row - 1) * h_spacing

                # 当前行的起始X坐标（居中）
                row_start_x = px + (pw - row_total_width) // 2

                # 当前物品的X坐标
                item_x = row_start_x + col * (item_size + h_spacing)

                # 当前物品的Y坐标
                item_y = reward_start_y + row * v_spacing

                # 绘制物品图标
                self.renderer.draw_item_icon(
                    item["type"],
                    item_x, item_y,
                    item_size
                )

                # 物品名称
                name_y = item_y + item_size + int(ph * 0.04)

                self.renderer.draw_text(
                    item["name"],
                    item_x + item_size // 2,
                    name_y,
                    "small",
                    self.renderer.colors["text_color"]
                )

            # 计算奖励区域的实际底部位置（最后一行的底部）
            last_row = total_rows - 1
            last_item_y = reward_start_y + last_row * v_spacing
            last_name_y = last_item_y + item_size + int(ph * 0.04)
            reward_bottom_y = last_name_y + int(ph * 0.03)  # 加上文字高度和小间距
        else:
            # 无奖励的情况
            no_reward_y = reward_title_y + int(ph * 0.10)
            self.renderer.draw_text(
                "无奖励",
                px + pw // 2,
                no_reward_y,
                "medium",
                self.renderer.colors["text_color"]
            )
            reward_bottom_y = no_reward_y + int(ph * 0.05)

        # 返回按钮 - 动态位置，确保在奖励下方且不超出面板
        button_width = int(pw * 0.20)
        button_height = int(ph * 0.08)

        # 计算按钮位置：奖励底部 + 间距，但不超过面板底部
        min_button_y = reward_bottom_y + int(ph * 0.05)  # 奖励下方留5%间距
        max_button_y = py + ph - button_height - int(ph * 0.08)  # 距离面板底部8%
        return_y = min(min_button_y, max_button_y)

        return_x = px + (pw - button_width) // 2

        self.return_button_rect = self.renderer.draw_button(
            "返回",
            return_x, return_y,
            button_width, button_height
        )

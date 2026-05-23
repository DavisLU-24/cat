"""
音效管理器
"""
import pygame
import os
from pathlib import Path


class SoundManager:
    """音效管理器"""

    def __init__(self):
        # 初始化音效系统
        try:
            pygame.mixer.init()
            self.enabled = True
        except:
            self.enabled = False

        # 音效字典
        self.sounds = {}

        # 加载音效
        if self.enabled:
            self._load_sounds()

    def _load_sounds(self):
        """加载所有音效"""
        project_root = Path(__file__).parent.parent
        sounds_dir = project_root / "assets" / "sounds"

        # 音效文件名映射
        sound_files = {
            "click": "click.wav",
            "feed": "feed.wav",
            "travel_start": "travel_start.wav",
            "travel_return": "travel_return.wav",
            "item_collect": "item_collect.wav",
            "error": "error.wav"
        }

        for sound_name, file_name in sound_files.items():
            sound_path = sounds_dir / file_name

            try:
                if sound_path.exists():
                    self.sounds[sound_name] = pygame.mixer.Sound(str(sound_path))
            except:
                # 加载失败，跳过
                pass

    def play(self, sound_name: str, volume: float = 1.0):
        """
        播放音效

        sound_name: click, feed, travel_start, travel_return, item_collect, error
        volume: 0.0 ~ 1.0
        """
        if not self.enabled:
            return

        sound = self.sounds.get(sound_name)
        if sound:
            try:
                sound.set_volume(volume)
                sound.play()
            except:
                pass

    def stop_all(self):
        """停止所有音效"""
        if self.enabled:
            try:
                pygame.mixer.stop()
            except:
                pass

    def set_volume(self, volume: float):
        """设置全局音量"""
        if not self.enabled:
            return

        volume = max(0.0, min(1.0, volume))

        for sound in self.sounds.values():
            try:
                sound.set_volume(volume)
            except:
                pass

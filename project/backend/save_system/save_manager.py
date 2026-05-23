"""
存档管理器
实现 SQLite + JSON 双存储
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from .game_state import GameState


class SaveManager:
    """存档管理器"""

    def __init__(self, repository):
        self.repository = repository
        self.saves_dir = self._get_saves_directory()

    def _get_saves_directory(self) -> Path:
        """获取存档目录路径"""
        project_root = Path(__file__).parent.parent.parent
        saves_dir = project_root / "saves"
        saves_dir.mkdir(parents=True, exist_ok=True)
        return saves_dir

    def _get_json_path(self, slot_id: int) -> Path:
        """获取 JSON 存档文件路径"""
        return self.saves_dir / f"save_slot_{slot_id}.json"

    def save_game(self, slot_id: int, game_state: GameState) -> Dict[str, Any]:
        """
        保存游戏（SQLite + JSON）

        返回:
            {
                "success": bool,
                "message": str,
                "slot_id": int,
                "json_path": str
            }
        """
        try:
            # 1. 保存到 SQLite
            state_dict = game_state.to_dict()
            success = self.repository.save_game_state(slot_id, state_dict)

            if not success:
                return {
                    "success": False,
                    "message": "SQLite 保存失败",
                    "slot_id": slot_id,
                    "json_path": None
                }

            # 2. 导出到 JSON
            json_path = self._get_json_path(slot_id)
            with open(json_path, 'w', encoding='utf-8') as f:
                f.write(game_state.to_json())

            return {
                "success": True,
                "message": f"游戏已保存到槽位 {slot_id}",
                "slot_id": slot_id,
                "json_path": str(json_path)
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"保存失败: {str(e)}",
                "slot_id": slot_id,
                "json_path": None
            }

    def load_game(self, slot_id: int) -> Dict[str, Any]:
        """
        加载游戏（优先从 SQLite）

        返回:
            {
                "success": bool,
                "message": str,
                "game_state": GameState or None
            }
        """
        try:
            # 1. 从 SQLite 加载
            state_dict = self.repository.load_game_state(slot_id)

            if not state_dict:
                return {
                    "success": False,
                    "message": f"槽位 {slot_id} 没有存档",
                    "game_state": None
                }

            # 2. 转换为 GameState 对象
            game_state = GameState()
            game_state.from_dict(state_dict)

            return {
                "success": True,
                "message": f"成功加载槽位 {slot_id}",
                "game_state": game_state
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"加载失败: {str(e)}",
                "game_state": None
            }

    def load_game_from_json(self, slot_id: int) -> Dict[str, Any]:
        """
        从 JSON 文件加载游戏（备用方案）

        返回:
            {
                "success": bool,
                "message": str,
                "game_state": GameState or None
            }
        """
        try:
            json_path = self._get_json_path(slot_id)

            if not json_path.exists():
                return {
                    "success": False,
                    "message": f"JSON 存档文件不存在: {json_path}",
                    "game_state": None
                }

            with open(json_path, 'r', encoding='utf-8') as f:
                json_str = f.read()

            game_state = GameState()
            game_state.from_json(json_str)

            return {
                "success": True,
                "message": f"成功从 JSON 加载槽位 {slot_id}",
                "game_state": game_state
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"从 JSON 加载失败: {str(e)}",
                "game_state": None
            }

    def delete_save(self, slot_id: int) -> Dict[str, Any]:
        """
        删除存档（SQLite + JSON）

        返回:
            {
                "success": bool,
                "message": str
            }
        """
        try:
            # 1. 删除 SQLite 中的存档
            success = self.repository.delete_save(slot_id)

            if not success:
                return {
                    "success": False,
                    "message": "删除 SQLite 存档失败"
                }

            # 2. 删除 JSON 文件
            json_path = self._get_json_path(slot_id)
            if json_path.exists():
                json_path.unlink()

            return {
                "success": True,
                "message": f"已删除槽位 {slot_id} 的存档"
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"删除失败: {str(e)}"
            }

    def get_save_slots_info(self) -> Dict[str, Any]:
        """
        获取所有存档槽位信息

        返回:
            {
                "success": bool,
                "slots": List[Dict]
            }
        """
        try:
            slots = self.repository.get_save_slots_info()

            return {
                "success": True,
                "slots": slots
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"获取存档信息失败: {str(e)}",
                "slots": []
            }

    def export_to_json(self, slot_id: int) -> Dict[str, Any]:
        """
        手动导出存档到 JSON

        返回:
            {
                "success": bool,
                "message": str,
                "json_path": str
            }
        """
        # 先加载
        result = self.load_game(slot_id)

        if not result["success"]:
            return {
                "success": False,
                "message": result["message"],
                "json_path": None
            }

        # 再导出
        try:
            game_state = result["game_state"]
            json_path = self._get_json_path(slot_id)

            with open(json_path, 'w', encoding='utf-8') as f:
                f.write(game_state.to_json())

            return {
                "success": True,
                "message": f"已导出到 {json_path}",
                "json_path": str(json_path)
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"导出失败: {str(e)}",
                "json_path": None
            }

    def import_from_json(self, slot_id: int) -> Dict[str, Any]:
        """
        从 JSON 导入存档到 SQLite

        返回:
            {
                "success": bool,
                "message": str
            }
        """
        # 从 JSON 加载
        result = self.load_game_from_json(slot_id)

        if not result["success"]:
            return {
                "success": False,
                "message": result["message"]
            }

        # 保存到 SQLite
        game_state = result["game_state"]
        save_result = self.save_game(slot_id, game_state)

        return {
            "success": save_result["success"],
            "message": f"已从 JSON 导入到槽位 {slot_id}"
        }

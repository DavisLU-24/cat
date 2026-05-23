"""
种子数据灌入模块
从 data 模块导入种子数据并插入数据库
"""
from .connection import get_db_connection
from ..data import FOODS_DATA, LANDMARKS_DATA, ITEMS_DATA


def seed_foods():
    """灌入食物数据"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 检查是否已有数据
    cursor.execute("SELECT COUNT(*) FROM Foods")
    if cursor.fetchone()[0] > 0:
        return  # 已有数据，跳过

    # 插入食物数据
    for food in FOODS_DATA:
        cursor.execute("""
            INSERT INTO Foods (id, name, description, energy_value, icon_path)
            VALUES (?, ?, ?, ?, ?)
        """, (food["id"], food["name"], food["description"],
              food["energy_value"], food["icon_path"]))

    conn.commit()


def seed_landmarks():
    """灌入地标数据"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 检查是否已有数据
    cursor.execute("SELECT COUNT(*) FROM Landmarks")
    if cursor.fetchone()[0] > 0:
        return

    # 插入地标数据
    for landmark in LANDMARKS_DATA:
        cursor.execute("""
            INSERT INTO Landmarks (id, name, description, min_energy, energy_cost, base_travel_time, icon_path, image_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (landmark["id"], landmark["name"], landmark["description"],
              landmark["min_energy"], landmark["energy_cost"], landmark["base_travel_time"],
              landmark["icon_path"], landmark["image_path"]))

    conn.commit()


def seed_items():
    """灌入收集品数据"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 检查是否已有数据
    cursor.execute("SELECT COUNT(*) FROM Items")
    if cursor.fetchone()[0] > 0:
        return

    # 插入收集品数据
    for item in ITEMS_DATA:
        cursor.execute("""
            INSERT INTO Items (id, name, description, type, rarity, landmark_id, icon_path)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (item["id"], item["name"], item["description"],
              item["type"], item["rarity"], item["landmark_id"], item["icon_path"]))

    conn.commit()


def seed_all():
    """灌入所有种子数据"""
    seed_foods()
    seed_landmarks()
    seed_items()


def is_database_seeded():
    """检查数据库是否已灌入种子数据"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM Foods")
    foods_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Landmarks")
    landmarks_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Items")
    items_count = cursor.fetchone()[0]

    return foods_count > 0 and landmarks_count > 0 and items_count > 0

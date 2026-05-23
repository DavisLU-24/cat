"""
收集品数据定义
56 个收集品：7 个地标 × (5 明信片 + 2 徽章 + 1 宝物)
"""

# 收集品种子数据
ITEMS_DATA = []

# 为每个地标生成收集品
LANDMARKS = [
    ("playground", "操场"),
    ("badminton_hall", "羽毛球馆"),
    ("wisdom_lake", "智慧湖"),
    ("lighthouse", "灯塔"),
    ("auditorium", "大礼堂"),
    ("library", "中远图书馆"),
    ("wusong_ship", "吴淞号船")
]

for landmark_id, landmark_name in LANDMARKS:
    # 5 张明信片
    for i in range(1, 6):
        ITEMS_DATA.append({
            "id": f"{landmark_id}_postcard_{i}",
            "name": f"{landmark_name}明信片{i}",
            "description": f"来自{landmark_name}的美丽明信片",
            "type": "postcard",
            "rarity": "common",
            "landmark_id": landmark_id,
            "icon_path": f"assets/images/postcard_{landmark_id}_{i}.png"
        })

    # 2 个徽章
    for i in range(1, 3):
        rarity = "rare" if i == 1 else "common"
        ITEMS_DATA.append({
            "id": f"{landmark_id}_badge_{i}",
            "name": f"{landmark_name}徽章{i}",
            "description": f"{landmark_name}的纪念徽章",
            "type": "badge",
            "rarity": rarity,
            "landmark_id": landmark_id,
            "icon_path": f"assets/images/badge_{landmark_id}_{i}.png"
        })

    # 1 个宝物
    ITEMS_DATA.append({
        "id": f"{landmark_id}_treasure",
        "name": f"{landmark_name}宝物",
        "description": f"{landmark_name}的珍贵宝物",
        "type": "treasure",
        "rarity": "legendary",
        "landmark_id": landmark_id,
        "icon_path": f"assets/images/treasure_{landmark_id}.png"
    })


def get_all_items():
    """获取所有收集品数据"""
    return ITEMS_DATA.copy()


def get_item_by_id(item_id: str):
    """根据 ID 获取收集品"""
    for item in ITEMS_DATA:
        if item["id"] == item_id:
            return item.copy()
    return None


def get_items_by_landmark(landmark_id: str):
    """获取指定地标的所有收集品"""
    return [item.copy() for item in ITEMS_DATA if item["landmark_id"] == landmark_id]


def get_items_by_type(item_type: str):
    """按类型获取收集品"""
    return [item.copy() for item in ITEMS_DATA if item["type"] == item_type]


def get_items_grouped_by_landmark(landmark_id: str):
    """获取指定地标的收集品，按类型分组"""
    items = get_items_by_landmark(landmark_id)
    return {
        "postcards": [item for item in items if item["type"] == "postcard"],
        "badges": [item for item in items if item["type"] == "badge"],
        "treasures": [item for item in items if item["type"] == "treasure"]
    }

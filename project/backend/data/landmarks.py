"""
地标数据定义
7 个上海海事大学地标及其属性
"""

# 地标种子数据
LANDMARKS_DATA = [
    {
        "id": "playground",
        "name": "操场",
        "description": "宽阔的操场，适合散步",
        "min_energy": 20,
        "energy_cost": 30,
        "base_travel_time": 5,  # 秒
        "icon_path": "assets/images/landmark_playground.png",
        "image_path": "assets/images/landmark_playground_full.png"
    },
    {
        "id": "badminton_hall",
        "name": "羽毛球馆",
        "description": "室内运动场馆",
        "min_energy": 20,
        "energy_cost": 30,
        "base_travel_time": 5,
        "icon_path": "assets/images/landmark_badminton.png",
        "image_path": "assets/images/landmark_badminton_full.png"
    },
    {
        "id": "wisdom_lake",
        "name": "智慧湖",
        "description": "美丽的校园湖泊",
        "min_energy": 25,
        "energy_cost": 35,
        "base_travel_time": 6,
        "icon_path": "assets/images/landmark_lake.png",
        "image_path": "assets/images/landmark_lake_full.png"
    },
    {
        "id": "lighthouse",
        "name": "灯塔",
        "description": "校园标志性建筑",
        "min_energy": 30,
        "energy_cost": 40,
        "base_travel_time": 7,
        "icon_path": "assets/images/landmark_lighthouse.png",
        "image_path": "assets/images/landmark_lighthouse_full.png"
    },
    {
        "id": "auditorium",
        "name": "大礼堂",
        "description": "举办活动的场所",
        "min_energy": 30,
        "energy_cost": 40,
        "base_travel_time": 7,
        "icon_path": "assets/images/landmark_auditorium.png",
        "image_path": "assets/images/landmark_auditorium_full.png"
    },
    {
        "id": "library",
        "name": "中远图书馆",
        "description": "知识的海洋",
        "min_energy": 35,
        "energy_cost": 45,
        "base_travel_time": 8,
        "icon_path": "assets/images/landmark_library.png",
        "image_path": "assets/images/landmark_library_full.png"
    },
    {
        "id": "wusong_ship",
        "name": "吴淞号船",
        "description": "海事大学的标志",
        "min_energy": 40,
        "energy_cost": 50,
        "base_travel_time": 9,
        "icon_path": "assets/images/landmark_ship.png",
        "image_path": "assets/images/landmark_ship_full.png"
    }
]


def get_all_landmarks():
    """获取所有地标数据"""
    return LANDMARKS_DATA.copy()


def get_landmark_by_id(landmark_id: str):
    """根据 ID 获取地标"""
    for landmark in LANDMARKS_DATA:
        if landmark["id"] == landmark_id:
            return landmark.copy()
    return None


def get_landmarks_sorted_by_energy():
    """按能量需求排序返回地标"""
    return sorted(LANDMARKS_DATA.copy(), key=lambda x: x["min_energy"])

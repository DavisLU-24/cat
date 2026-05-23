"""
食物数据定义
8 种食物及其属性
"""

# 食物种子数据
FOODS_DATA = [
    {
        "id": "fish",
        "name": "鱼",
        "description": "小猫最爱的美食",
        "energy_value": 50,
        "icon_path": "assets/images/food_fish.png"
    },
    {
        "id": "cat_food",
        "name": "猫粮",
        "description": "营养均衡的主食",
        "energy_value": 30,
        "icon_path": "assets/images/food_cat_food.png"
    },
    {
        "id": "milk",
        "name": "牛奶",
        "description": "香浓的牛奶",
        "energy_value": 20,
        "icon_path": "assets/images/food_milk.png"
    },
    {
        "id": "chicken",
        "name": "鸡肉",
        "description": "新鲜的鸡肉",
        "energy_value": 40,
        "icon_path": "assets/images/food_chicken.png"
    },
    {
        "id": "tuna",
        "name": "金枪鱼罐头",
        "description": "高级美味",
        "energy_value": 60,
        "icon_path": "assets/images/food_tuna.png"
    },
    {
        "id": "treats",
        "name": "小零食",
        "description": "猫咪零食",
        "energy_value": 15,
        "icon_path": "assets/images/food_treats.png"
    },
    {
        "id": "dried_fish",
        "name": "小鱼干",
        "description": "香脆可口",
        "energy_value": 25,
        "icon_path": "assets/images/food_dried_fish.png"
    },
    {
        "id": "cat_grass",
        "name": "猫草",
        "description": "健康零食",
        "energy_value": 10,
        "icon_path": "assets/images/food_cat_grass.png"
    }
]


def get_all_foods():
    """获取所有食物数据"""
    return FOODS_DATA.copy()


def get_food_by_id(food_id: str):
    """根据 ID 获取食物"""
    for food in FOODS_DATA:
        if food["id"] == food_id:
            return food.copy()
    return None

-- 旅行小猫数据库 Schema
-- 创建时间: 2026-05-24

-- 版本管理表
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 静态配置表: 食物
CREATE TABLE IF NOT EXISTS Foods (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    energy_value INTEGER NOT NULL,
    icon_path TEXT
);

-- 静态配置表: 地标
CREATE TABLE IF NOT EXISTS Landmarks (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    min_energy INTEGER NOT NULL,
    energy_cost INTEGER NOT NULL,
    base_travel_time INTEGER NOT NULL,
    icon_path TEXT,
    image_path TEXT
);

-- 静态配置表: 收集品
CREATE TABLE IF NOT EXISTS Items (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    type TEXT NOT NULL CHECK(type IN ('postcard', 'badge', 'treasure')),
    rarity TEXT NOT NULL CHECK(rarity IN ('common', 'rare', 'legendary')),
    landmark_id TEXT NOT NULL,
    icon_path TEXT,
    FOREIGN KEY (landmark_id) REFERENCES Landmarks(id)
);

-- 存档槽位表
CREATE TABLE IF NOT EXISTS SaveSlots (
    slot_id INTEGER PRIMARY KEY CHECK(slot_id BETWEEN 1 AND 10),
    game_time REAL NOT NULL DEFAULT 0,
    save_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_occupied INTEGER NOT NULL DEFAULT 0
);

-- 小猫状态表
CREATE TABLE IF NOT EXISTS CatState (
    slot_id INTEGER PRIMARY KEY,
    current_energy INTEGER NOT NULL DEFAULT 100,
    status TEXT NOT NULL DEFAULT 'idle' CHECK(status IN ('idle', 'eating', 'traveling', 'returning')),
    mood TEXT NOT NULL DEFAULT 'happy' CHECK(mood IN ('happy', 'normal', 'tired', 'exhausted')),
    last_fed_time TIMESTAMP,
    total_travels INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (slot_id) REFERENCES SaveSlots(slot_id) ON DELETE CASCADE
);

-- 玩家背包表
CREATE TABLE IF NOT EXISTS PlayerInventory (
    slot_id INTEGER NOT NULL,
    item_id TEXT NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    obtained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (slot_id, item_id),
    FOREIGN KEY (slot_id) REFERENCES SaveSlots(slot_id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES Items(id)
);

-- 旅行历史表
CREATE TABLE IF NOT EXISTS TravelHistory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slot_id INTEGER NOT NULL,
    landmark_id TEXT NOT NULL,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    energy_before INTEGER NOT NULL,
    energy_after INTEGER NOT NULL,
    duration REAL NOT NULL,
    FOREIGN KEY (slot_id) REFERENCES SaveSlots(slot_id) ON DELETE CASCADE,
    FOREIGN KEY (landmark_id) REFERENCES Landmarks(id)
);

-- 旅行奖励表
CREATE TABLE IF NOT EXISTS TravelRewards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    travel_id INTEGER NOT NULL,
    item_id TEXT NOT NULL,
    FOREIGN KEY (travel_id) REFERENCES TravelHistory(id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES Items(id)
);

-- 已解锁地标表
CREATE TABLE IF NOT EXISTS UnlockedLandmarks (
    slot_id INTEGER NOT NULL,
    landmark_id TEXT NOT NULL,
    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (slot_id, landmark_id),
    FOREIGN KEY (slot_id) REFERENCES SaveSlots(slot_id) ON DELETE CASCADE,
    FOREIGN KEY (landmark_id) REFERENCES Landmarks(id)
);

-- 当前旅行状态表
CREATE TABLE IF NOT EXISTS CurrentTravel (
    slot_id INTEGER PRIMARY KEY,
    landmark_id TEXT NOT NULL,
    start_time REAL NOT NULL,
    duration REAL NOT NULL,
    energy_before INTEGER NOT NULL,
    FOREIGN KEY (slot_id) REFERENCES SaveSlots(slot_id) ON DELETE CASCADE,
    FOREIGN KEY (landmark_id) REFERENCES Landmarks(id)
);

-- 初始化版本号
INSERT OR IGNORE INTO schema_version (version) VALUES (1);

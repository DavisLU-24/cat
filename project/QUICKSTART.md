# 快速启动指南

## 1. 安装依赖

```bash
pip install -r requirements.txt
```

或直接安装 Pygame：

```bash
pip install pygame
```

## 2. 运行游戏

```bash
python main.py
```

## 3. 游戏操作

### 主界面
- **点击食物**：喂养小猫，增加能量
- **开始旅行**：打开旅行界面
- **背包**：查看收集的物品
- **存档/读档**：保存或加载游戏进度

### 旅行界面
- **选择地标**：点击地标列表中的地标
- **开始旅行**：点击按钮开始旅行
- **随机旅行**：随机选择一个可访问的地标
- **取消旅行**：旅行中可以取消（不返还能量）

### 背包界面
- **Tab 切换**：明信片/徽章/宝物/收集进度
- **查看进度**：收集进度 Tab 显示总体进度和各地标进度

### 快捷键
- **ESC**：关闭弹窗 → 返回主界面 → 退出游戏
- **鼠标左键**：所有操作

## 4. 游戏提示

### 能量管理
- 能量范围：0-200
- 喂食增加能量，旅行消耗能量
- 能量越高，旅行获得珍贵物品的概率越大

### 地标选择
- 地标有最低能量要求
- 能量不足的地标会显示为灰色
- 先去近处的地标，积累能量后再去远处

### 收集策略
- 必得 1 张明信片
- 能量 ≥50：有概率得徽章（能量越高概率越大）
- 能量 >100：有概率得宝物（能量越高概率越大）

## 5. 数据迁移（高级）

### 导出存档为 JSON

```bash
python scripts/migrate_data.py db2json
```

### 从 JSON 导入存档

```bash
python scripts/migrate_data.py json2db
```

### 指定槽位

```bash
python scripts/migrate_data.py db2json --slot 1
python scripts/migrate_data.py json2db --slot 1
```

## 6. 故障排除

### 无法启动游戏
- 确认已安装 Pygame：`pip install pygame`
- 确认 Python 版本 ≥ 3.7

### 数据库错误
- 删除 `data/travel_cat.db` 文件，重新启动游戏

### 资源缺失
- 游戏会使用占位图（灰色方块），不影响游戏逻辑
- 可以将图片放入 `assets/images/` 目录

## 7. 目录说明

- `data/` - 数据库文件
- `saves/` - JSON 备份存档
- `assets/` - 游戏资源（图片、音效）
- `database/` - 数据库建表脚本
- `backend/` - 后端代码
- `frontend/` - 前端代码

## 8. 开发调试

### 查看数据库内容

```bash
sqlite3 data/travel_cat.db
.tables
SELECT * FROM Foods;
.exit
```

### 重置游戏数据

删除以下文件：
- `data/travel_cat.db`
- `saves/*.json`

重新启动游戏即可。

---

**祝游戏愉快！** 🐱

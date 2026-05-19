# law-school-crawler

法学保研夏令营自动监控系统，用于定时抓取中国 985 + 五院四系法学院官网中的夏令营、推免、优秀大学生计划、招生简章等通知，并自动去重入库。

## 功能

- 定时抓取法学院公告页
- 关键词过滤：夏令营、推免、推荐免试、招生、优秀大学生等
- 自动补全相对链接
- SQLite 去重入库
- 可选 Server 酱微信推送

## 项目结构

```text
law-school-crawler/
├── crawler/
│   ├── __init__.py
│   ├── base.py
│   ├── schools.py
│   ├── parser.py
│   └── run.py
├── storage/
│   ├── __init__.py
│   └── db.py
├── notify/
│   ├── __init__.py
│   └── serverchan.py
├── utils/
│   ├── __init__.py
│   └── text.py
├── config.py
├── requirements.txt
├── main.py
└── README.md
```

## 安装

```bash
cd law-school-crawler
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 运行

```bash
python main.py
```

程序启动后会立即执行一次抓取，之后默认每 6 小时自动执行一次。

## 查询页面

启动本地交互页面：

```bash
python web.py
```

打开：

```text
http://127.0.0.1:5000
```

页面支持：

- 查看通知总数、已入库学校数、最近入库时间
- 按关键词查询通知
- 按学校筛选通知
- 按学校类型筛选：985、五院四系
- 按通知类型筛选：夏令营、预推免、推免、招生
- 按年份筛选历年通知，默认可选 2021-2027
- 在页面保存 Server 酱 SendKey 并启用微信推送
- 点击“立即抓取”手动触发一次爬虫
- 点击“打开”跳转到原公告

抓取逻辑包含两类数据源：

- `crawler/xingke.py`：同步结构化保研信息库中的法学夏令营、预推免、推免数据
- `crawler/run.py`：继续巡检 985 + 五院四系法学院官网公告页，发现新链接后入库和推送

## 微信推送

不需要填写微信号。微信推送通过 Server 酱完成：

1. 打开页面中的“绑定微信”，或访问 `https://sct.ftqq.com/`
2. 按 Server 酱提示扫码绑定微信
3. 复制 SendKey
4. 回到本项目页面，填写 SendKey 并勾选“启用新通知推送”
5. 保存设置

之后每次抓取到新通知，系统会自动推送到绑定的微信。

## 配置

可通过环境变量配置：

```bash
export RUN_INTERVAL_HOURS=6
export ENABLE_NOTIFY=true
export SERVERCHAN_KEY=你的Server酱SendKey
export DATABASE_PATH=/absolute/path/to/data.db
```

如果不配置 `ENABLE_NOTIFY=true` 和 `SERVERCHAN_KEY`，系统只会入库和打印新通知，不会推送微信。

## 添加学校

在 `crawler/schools.py` 的 `SCHOOLS` 中继续追加：

```python
{
    "name": "学校名称",
    "type": "985",
    "urls": [
        "https://example.edu.cn/notice.htm",
    ],
}
```

## 数据库

默认数据库文件为项目根目录下的 `data.db`，表结构为：

```sql
CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    school TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    date TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

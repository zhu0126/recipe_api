# 食譜管理 API

FastAPI 後端，提供食譜查詢、冰箱管理、收藏功能。

## 快速啟動

```bash
pip install -r requirements.txt
cp .env.example .env        # 填入資料庫設定
python scripts/seed.py      # 建立測試資料（選用）
uvicorn src.main:app --reload --port 8000
```

互動文件：http://localhost:8000/docs

## 目錄結構

```
project/
├── src/
│   ├── main.py          程式入口
│   ├── config.py        環境變數設定
│   ├── database.py      DB 連線
│   ├── models/          資料表定義
│   ├── schemas/         Pydantic 驗證
│   ├── routes/          API 路由（只負責接收/回傳）
│   ├── services/        商業邏輯
│   └── utils/           共用工具
├── tests/               自動化測試
├── scripts/             一次性工具（seed、匯入資料）
├── docs/                API 文件
└── data/                測試 JSON/CSV
```

## 執行測試

```bash
pytest tests/ -v
```

## 換資料庫

在 `.env` 修改 `DATABASE_URL`：
- MySQL：`mysql+aiomysql://user:pass@localhost/recipe_db`
- PostgreSQL：`postgresql+asyncpg://user:pass@localhost/recipe_db`

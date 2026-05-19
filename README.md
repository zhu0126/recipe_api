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
├── .git/                  Git 版本控制
├── .gitignore            忽略不必要的檔案
├── .env.example          環境變數範例設定
├── .pytest_cache/        pytest 快取資料
├── recipe_app.db         本機 SQLite 測試資料庫
├── requirements.txt      Python 套件依賴
├── data/                 測試資料（CSV / JSON）
├── docs/                 API 文件與專案說明
├── scripts/              一次性工具與資料初始化腳本
│   └── seed.py           建立測試資料
├── src/                  應用程式原始碼
│   ├── __init__.py
│   ├── main.py           程式入口
│   ├── config.py         環境與設定讀取
│   ├── database.py       資料庫連線設定
│   ├── models/           ORM 資料表定義
│   │   └── tables.py
│   ├── schemas/          Pydantic 請求/回應驗證
│   ├── routes/           API 路由
│   ├── services/         商業邏輯與資料處理
│   └── utils/            共用輔助工具
└── tests/                自動化測試
    ├── conftest.py
    ├── test_favorites.py
    ├── test_fridge.py
    ├── test_ingredients.py
    ├── test_recipes.py
    └── test_integration.py
```

## 執行測試

```bash
pytest tests/ -v
```

## 換資料庫

在 `.env` 修改 `DATABASE_URL`：
- MySQL：`mysql+aiomysql://user:pass@localhost/recipe_db`
- PostgreSQL：`postgresql+asyncpg://user:pass@localhost/recipe_db`

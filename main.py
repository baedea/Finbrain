from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from routers import goal_simulator
import os

# 建立 FastAPI 應用
app = FastAPI(
    title="多元投資理財模擬器",
    description="提供債券、ETF、房屋、股票等多種投資計算與模擬工具",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 註冊 API 路由
app.include_router(
    goal_simulator.router, 
    prefix="/api/v1", 
    tags=["投資計算與模擬"]
)

# 掛載靜態檔案 - 修正路徑問題
static_dir = "static"
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
    
# 如果存在 static 目錄才掛載
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def read_root():
    """主頁面"""
    # 檢查 index.html 是否存在於 static 目錄
    index_path = os.path.join("static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    elif os.path.exists("index.html"):
        return FileResponse("index.html")
    else:
        return {
            "message": "多元投資理財模擬器",
            "version": "2.0.0",
            "status": "running",
            "available_endpoints": [
                "/docs - API 文檔",
                "/api/v1/bond-deposit - 債券/定存計算",
                "/api/v1/etf-investment - ETF定期定額計算", 
                "/api/v1/house-investment - 房屋投資分析",
                "/api/v1/stock-simulation - 股票投資模擬",
                "/api/v1/financial-goal - 財務目標規劃",
                "/api/v1/investment-types - 投資類型清單"
            ]
        }

@app.get("/health")
async def health_check():
    """健康檢查"""
    return {
        "status": "healthy", 
        "message": "多元投資模擬器運行正常",
        "version": "2.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
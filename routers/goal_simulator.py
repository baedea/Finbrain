from fastapi import APIRouter, HTTPException
from typing import List

from models.request_models import (
    BondDepositRequest, ETFInvestmentRequest,
    HouseInvestmentRequest, StockSimulationRequest,
    FinancialGoalRequest
)
from models.response_models import (
    BondDepositResponse, ETFInvestmentResponse,
    HouseInvestmentResponse, StockSimulationResponse,
    FinancialGoalResponse, InvestmentTypesResponse, InvestmentTypeInfo
)
from services.goal_calculator import InvestmentCalculator

# 建立路由器
router = APIRouter()

# 初始化計算器
calculator = InvestmentCalculator()

# =============== 債券/定存計算 API ===============
@router.post("/bond-deposit", response_model=BondDepositResponse)
async def calculate_bond_deposit(request: BondDepositRequest):
    """
    債券/定存投資計算
    
    計算債券或定存投資的名目報酬、實質報酬，並考慮通膨影響
    """
    try:
        result = calculator.calculate_bond_deposit(request)
        if not result.success:
            raise HTTPException(status_code=400, detail=result.message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"計算錯誤: {str(e)}")

# =============== ETF定期定額計算 API ===============
@router.post("/etf-investment", response_model=ETFInvestmentResponse)
async def calculate_etf_investment(request: ETFInvestmentRequest):
    """
    ETF定期定額投資計算
    
    模擬ETF定期定額投資，分離配息與價格成長效果
    """
    try:
        result = calculator.calculate_etf_investment(request)
        if not result.success:
            raise HTTPException(status_code=400, detail=result.message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"計算錯誤: {str(e)}")

# =============== 房屋投資分析 API ===============
@router.post("/house-investment", response_model=HouseInvestmentResponse)
async def calculate_house_investment(request: HouseInvestmentRequest):
    """
    房屋投資分析
    
    分析房屋投資的現金流、報酬率，支援兩種情境分析
    """
    try:
        result = calculator.calculate_house_investment(request)
        if not result.success:
            raise HTTPException(status_code=400, detail=result.message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"計算錯誤: {str(e)}")

# =============== 股票投資模擬 API ===============
@router.post("/stock-simulation", response_model=StockSimulationResponse)
async def calculate_stock_simulation(request: StockSimulationRequest):
    """
    股票投資蒙地卡羅模擬
    
    使用蒙地卡羅方法模擬股票投資的風險與報酬分布
    """
    try:
        result = calculator.calculate_stock_simulation(request)
        if not result.success:
            raise HTTPException(status_code=400, detail=result.message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"計算錯誤: {str(e)}")

# =============== 綜合財務目標模擬 API ===============
@router.post("/financial-goal", response_model=FinancialGoalResponse)
async def simulate_financial_goal(request: FinancialGoalRequest):
    """
    綜合財務目標模擬
    
    根據投資組合配置，模擬是否能達成財務目標並提供建議
    """
    try:
        result = calculator.calculate_financial_goal(request)
        if not result.success:
            raise HTTPException(status_code=400, detail=result.message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"計算錯誤: {str(e)}")

# =============== 投資類型資訊 API ===============
@router.get("/investment-types", response_model=InvestmentTypesResponse)
async def get_investment_types():
    """取得可用的投資類型資訊"""
    try:
        investment_types = [
            InvestmentTypeInfo(
                id="stock",
                name="股票",
                expected_return="12%",
                risk="高",
                description="具有高成長潛力但波動較大的股票投資",
                min_amount=10000,
                liquidity="高"
            ),
            InvestmentTypeInfo(
                id="bond",
                name="債券",
                expected_return="4%",
                risk="低",
                description="穩定收益的債券投資，適合保守型投資者",
                min_amount=50000,
                liquidity="中"
            ),
            InvestmentTypeInfo(
                id="etf",
                name="ETF",
                expected_return="8%",
                risk="中",
                description="追蹤指數的交易所買賣基金，分散投資風險",
                min_amount=5000,
                liquidity="高"
            ),
            InvestmentTypeInfo(
                id="house",
                name="房地產",
                expected_return="5%",
                risk="中",
                description="不動產投資，具有抗通膨特性但流動性較低",
                min_amount=2000000,
                liquidity="低"
            ),
            InvestmentTypeInfo(
                id="deposit",
                name="定存",
                expected_return="2%",
                risk="極低",
                description="銀行定期存款，資本安全但報酬較低",
                min_amount=1000,
                liquidity="低"
            )
        ]
        
        return InvestmentTypesResponse(
            success=True,
            investment_types=investment_types
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取得投資類型錯誤: {str(e)}")

# =============== 健康檢查 API ===============
@router.get("/health")
async def health_check():
    """API 健康檢查"""
    return {
        "status": "healthy",
        "message": "投資計算 API 運行正常",
        "available_endpoints": [
            "/bond-deposit - 債券/定存計算",
            "/etf-investment - ETF定期定額計算",
            "/house-investment - 房屋投資分析", 
            "/stock-simulation - 股票投資模擬",
            "/financial-goal - 綜合財務目標模擬",
            "/investment-types - 投資類型清單"
        ]
    }

# =============== 批量計算 API ===============
@router.post("/batch-compare")
async def batch_investment_compare(
    bond_request: BondDepositRequest,
    etf_request: ETFInvestmentRequest,
    stock_request: StockSimulationRequest
):
    """
    批量投資比較
    
    同時計算多種投資方式的報酬，便於比較分析
    """
    try:
        results = {}
        
        # 債券/定存計算
        bond_result = calculator.calculate_bond_deposit(bond_request)
        if bond_result.success:
            results["bond"] = {
                "type": "債券/定存",
                "final_value": bond_result.final_value,
                "total_return": bond_result.final_value - bond_request.principal,
                "annual_return": bond_result.nominal_return,
                "risk_level": "低"
            }
        
        # ETF計算
        etf_result = calculator.calculate_etf_investment(etf_request)
        if etf_result.success:
            results["etf"] = {
                "type": "ETF定期定額",
                "final_value": etf_result.final_value,
                "total_return": etf_result.profit,
                "annual_return": etf_result.annualized_return,
                "risk_level": "中"
            }
        
        # 股票模擬
        stock_result = calculator.calculate_stock_simulation(stock_request)
        if stock_result.success:
            results["stock"] = {
                "type": "股票投資",
                "final_value": stock_result.mean,
                "total_return": stock_result.mean - stock_request.initial_amount - (stock_request.monthly_amount * stock_request.years),
                "annual_return": stock_result.mean_return,
                "risk_level": "高",
                "worst_case": stock_result.percentile_5,
                "best_case": stock_result.percentile_95
            }
        
        return {
            "success": True,
            "comparison_results": results,
            "summary": {
                "total_scenarios": len(results),
                "recommendation": "根據風險承受度選擇合適的投資組合"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量計算錯誤: {str(e)}")

# ===============
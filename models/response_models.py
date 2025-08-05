from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# =============== 基礎回應模型 ===============
class BaseResponse(BaseModel):
    """基礎回應模型"""
    success: bool
    message: Optional[str] = None

# =============== 債券/定存回應模型 ===============
class BondDepositResponse(BaseResponse):
    """債券/定存投資計算回應"""
    final_value: float  # 最終價值 (名目)
    real_value: float   # 實質價值 (扣除通膨)
    nominal_return: float  # 名目年化報酬率 (%)
    real_return: float     # 實質年化報酬率 (%)
    inflation_impact: float  # 通膨影響金額
    
    # 額外分析資訊
    total_interest: float  # 總利息收入
    inflation_loss: float  # 通膨損失
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "final_value": 1131408.04,
                "real_value": 1021518.28,
                "nominal_return": 2.5,
                "real_return": 0.49,
                "inflation_impact": 109889.76,
                "total_interest": 131408.04,
                "inflation_loss": 109889.76
            }
        }

# =============== ETF定期定額回應模型 ===============
class ETFInvestmentResponse(BaseResponse):
    """ETF定期定額投資計算回應"""
    final_value: float      # 最終價值
    total_investment: float # 總投資金額
    profit: float          # 獲利
    roi: float            # 投資報酬率 (%)
    irr: float            # 內部報酬率 (%)
    annualized_return: float  # 年化報酬率 (%)
    dividend_income: float    # 累積配息收入
    capital_gain: float      # 資本利得
    
    # 報酬來源分析
    dividend_ratio: float    # 配息收入占比 (%)
    capital_gain_ratio: float # 資本利得占比 (%)
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "final_value": 1735537.35,
                "total_investment": 1300000.0,
                "profit": 435537.35,
                "roi": 33.5,
                "irr": 8.2,
                "annualized_return": 8.1,
                "dividend_income": 150000.0,
                "capital_gain": 285537.35,
                "dividend_ratio": 34.4,
                "capital_gain_ratio": 65.6
            }
        }

# =============== 房屋投資回應模型 =============== 
class HouseInvestmentResponse(BaseResponse):
    """房屋投資分析回應"""
    scenario: str              # 情境描述
    actual_cash_outflow: float # 實際現金支出
    actual_sale_income: float  # 賣房實際收入
    current_value: float       # 房屋現值
    profit: float             # 獲利
    roi: float               # 投資報酬率 (%)
    annual_return: float     # 預期年報酬 (%)
    
    # 貸款相關資訊
    monthly_payment: float    # 每月還款金額
    loan_years: int          # 貸款年限
    interest_paid: float     # 利息支出總額
    total_loan_payments: float # 總還款金額
    remaining_principal: float # 剩餘本金
    holding_cost: float      # 持有成本
    
    # 詳細分析
    loan_amount: float       # 貸款金額
    down_payment_ratio: float # 頭期款比例 (%)
    leverage_ratio: float    # 槓桿比例
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "scenario": "情境A：持有10年後賣出",
                "actual_cash_outflow": 4435171.0,
                "actual_sale_income": 9565067.0,
                "current_value": 14000000.0,
                "profit": 5129896.0,
                "roi": 115.66,
                "annual_return": 3.41,
                "monthly_payment": 40317.0,
                "loan_years": 20,
                "interest_paid": 1838032.0,
                "total_loan_payments": 9838032.0,
                "remaining_principal": 4434933.0,
                "holding_cost": 500000.0,
                "loan_amount": 8000000.0,
                "down_payment_ratio": 20.0,
                "leverage_ratio": 4.0
            }
        }

# =============== 股票投資模擬回應模型 ===============
class StockSimulationResponse(BaseResponse):
    """股票投資蒙地卡羅模擬回應"""
    mean: float           # 平均最終價值
    percentile_5: float   # 5% 最差情況
    percentile_95: float  # 95% 最佳情況
    total_investment: float # 總投資金額
    mean_return: float    # 平均年化報酬率 (%)
    worst_case: float     # 最差情況年化報酬率 (%)
    best_case: float      # 最佳情況年化報酬率 (%)
    
    # 風險分析
    probability_positive: float  # 獲利機率 (%)
    probability_target: Optional[float] = None  # 達標機率 (%)
    value_at_risk: float        # 風險價值 (5% VaR)
    expected_shortfall: float   # 預期損失
    
    # 統計資訊
    simulation_count: int       # 模擬次數
    volatility_realized: float  # 實現波動率 (%)
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "mean": 8742633.0,
                "percentile_5": 5234891.0,
                "percentile_95": 14589332.0,
                "total_investment": 4000000.0,
                "mean_return": 8.12,
                "worst_case": 2.73,
                "best_case": 13.85,
                "probability_positive": 87.5,
                "value_at_risk": 5234891.0,
                "expected_shortfall": 4645123.0,
                "simulation_count": 10000,
                "volatility_realized": 15.2
            }
        }

# =============== 年度預測模型 ===============
class YearlyProjection(BaseModel):
    """年度投資預測"""
    year: int
    total_investment: float  # 累積投入
    portfolio_value: float   # 投資組合價值
    total_return: float      # 總報酬
    return_rate: float       # 報酬率 (%)

# =============== 投資建議模型 ===============
class RecommendationItem(BaseModel):
    """建議項目"""
    type: str           # 建議類型
    description: str    # 建議內容
    impact: str        # 影響說明
    priority: int      # 優先順序 (1=高, 2=中, 3=低)

# =============== 目標分析模型 ===============
class GoalAnalysis(BaseModel):
    """達標分析"""
    can_achieve_goal: bool    # 是否能達成目標
    probability: float        # 達標機率 (0-1)
    shortfall_amount: float   # 不足金額
    required_monthly_increase: float  # 需要增加的月投資額

# =============== 綜合財務目標回應模型 ===============
class FinancialGoalResponse(BaseResponse):
    """綜合財務目標模擬回應"""
    goal_name: str
    projections: List[YearlyProjection]    # 年度預測
    final_amount: float                    # 最終金額
    total_investment: float                # 總投資
    total_return: float                    # 總報酬
    average_annual_return: float           # 平均年化報酬率
    goal_analysis: Optional[GoalAnalysis]  # 目標分析
    recommendations: List[RecommendationItem]  # 投資建議
    
    # 圖表資料
    chart_data: Dict[str, Any] = {
        "years": [],
        "portfolio_values": [],
        "total_investments": [],
        "returns": []
    }
    
    # 風險分析
    portfolio_risk: float                  # 投資組合風險
    risk_adjusted_return: float            # 風險調整報酬率
    sharpe_ratio: Optional[float]          # 夏普比率

# =============== 投資類型資訊模型 ===============
class InvestmentTypeInfo(BaseModel):
    """投資類型資訊"""
    id: str
    name: str
    expected_return: str    # 預期報酬率
    risk: str              # 風險等級
    description: str       # 描述
    min_amount: float      # 最小投資金額
    liquidity: str         # 流動性

class InvestmentTypesResponse(BaseResponse):
    """投資類型清單回應"""
    investment_types: List[InvestmentTypeInfo]

# =============== 錯誤回應模型 ===============
class ErrorResponse(BaseModel):
    """錯誤回應模型"""
    success: bool = False
    error_code: str
    error_message: str
    details: Optional[Dict[str, Any]] = None
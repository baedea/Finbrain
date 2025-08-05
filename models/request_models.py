from pydantic import BaseModel, Field, validator
from typing import Optional
from enum import Enum

class InvestmentType(str, Enum):
    """投資類型枚舉"""
    STOCK = "stock"
    BOND = "bond" 
    ETF = "etf"
    HOUSE = "house"
    DEPOSIT = "deposit"

class RiskTolerance(str, Enum):
    """風險承受度枚舉"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class HouseScenario(str, Enum):
    """房屋投資情境"""
    A = "A"  # 提前賣出
    B = "B"  # 持有到貸款還完

# =============== 債券/定存計算請求模型 ===============
class BondDepositRequest(BaseModel):
    """債券/定存投資計算請求"""
    principal: float = Field(..., gt=0, description="本金 (TWD)")
    interest_rate: float = Field(..., ge=0, description="利率 (%)")
    years: int = Field(..., gt=0, le=50, description="投資年限")
    is_compound: bool = Field(True, description="是否複利，預設為 True")
    inflation_rate: float = Field(2.0, ge=0, le=20, description="通膨率 (%)，預設為 2.0%")

    class Config:
        json_schema_extra = {
            "example": {
                "principal": 1000000,
                "interest_rate": 2.5,
                "years": 5,
                "is_compound": True,
                "inflation_rate": 2.0
            }
        }

# =============== ETF定期定額請求模型 ===============
class ETFInvestmentRequest(BaseModel):
    """ETF定期定額投資計算請求"""
    initial_amount: float = Field(..., ge=0, description="初始投入金額 (TWD)")
    monthly_amount: float = Field(..., ge=0, description="每月定期投入 (TWD)")
    dividend_yield: float = Field(..., ge=0, le=20, description="年配息率 (%)")
    price_growth: float = Field(..., ge=-50, le=50, description="年價格成長率 (%)")
    years: int = Field(..., gt=0, le=50, description="投資年限")

    class Config:
        json_schema_extra = {
            "example": {
                "initial_amount": 100000,
                "monthly_amount": 10000,
                "dividend_yield": 3.0,
                "price_growth": 5.0,
                "years": 10
            }
        }

# =============== 房屋投資請求模型 ===============
class HouseInvestmentRequest(BaseModel):
    """房屋投資分析請求"""
    house_price: float = Field(..., gt=0, description="房屋價格 (TWD)")
    down_payment: float = Field(..., gt=0, description="頭期款 (TWD)")
    loan_rate: float = Field(..., ge=0, le=20, description="貸款利率 (%)")
    loan_years: int = Field(..., gt=0, le=40, description="貸款年限")
    appreciation_rate_a: float = Field(..., ge=-50, le=200, description="情境A預期房價總漲幅 (%)")
    appreciation_rate_b: float = Field(..., ge=-50, le=200, description="情境B預期房價總漲幅 (%)")
    annual_cost: float = Field(..., ge=0, description="年度持有成本 (TWD)")
    simulation_years: int = Field(..., gt=0, le=50, description="模擬年數")
    scenario: HouseScenario = Field(HouseScenario.A, description="情境選擇 (A=提前賣出, B=持有到貸款還完)")

    @validator('down_payment')
    def down_payment_not_exceed_house_price(cls, v, values):
        if 'house_price' in values and v >= values['house_price']:
            raise ValueError('頭期款不能大於或等於房屋價格')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "house_price": 10000000,
                "down_payment": 2000000,
                "loan_rate": 2.0,
                "loan_years": 20,
                "appreciation_rate_a": 40,
                "appreciation_rate_b": 60,
                "annual_cost": 50000,
                "simulation_years": 10,
                "scenario": "A"
            }
        }

# =============== 股票投資模擬請求模型 ===============
class StockSimulationRequest(BaseModel):
    """股票投資蒙地卡羅模擬請求"""
    initial_amount: float = Field(..., ge=0, description="初始投入金額 (TWD)")
    monthly_amount: float = Field(..., ge=0, description="每年額外投入金額 (TWD)")
    expected_return: float = Field(..., ge=-50, le=100, description="預期年報酬率 (%)")
    volatility: float = Field(..., gt=0, le=100, description="波動率 (%)")
    years: int = Field(..., gt=0, le=50, description="投資年限")
    simulations: int = Field(10000, ge=1000, le=100000, description="模擬次數 (預設 10,000)")

    class Config:
        json_schema_extra = {
            "example": {
                "initial_amount": 2000000,
                "monthly_amount": 200000,
                "expected_return": 12,
                "volatility": 15,
                "years": 10,
                "simulations": 10000
            }
        }

# =============== 綜合財務目標模擬請求模型 ===============
class FinancialGoalRequest(BaseModel):
    """綜合財務目標模擬請求（可選功能）"""
    goal_name: str = Field(..., min_length=1, max_length=100, description="目標名稱")
    target_amount: Optional[float] = Field(None, gt=0, description="目標金額 (TWD)")
    initial_amount: float = Field(..., ge=0, description="初始投入金額 (TWD)")
    monthly_amount: float = Field(..., ge=0, description="每月定期投入 (TWD)")
    investment_period: int = Field(..., gt=0, le=50, description="投資期間（年）")
    risk_tolerance: RiskTolerance = Field(RiskTolerance.MEDIUM, description="風險承受度")
    
    # 投資組合配置 (可選)
    stock_allocation: float = Field(0, ge=0, le=100, description="股票配置比例 (%)")
    bond_allocation: float = Field(0, ge=0, le=100, description="債券配置比例 (%)")
    etf_allocation: float = Field(0, ge=0, le=100, description="ETF配置比例 (%)")
    deposit_allocation: float = Field(0, ge=0, le=100, description="定存配置比例 (%)")

    @validator('deposit_allocation')
    def validate_total_allocation(cls, v, values):
        total = (
            values.get('stock_allocation', 0) +
            values.get('bond_allocation', 0) +  
            values.get('etf_allocation', 0) +
            v
        )
        if abs(total - 100.0) > 0.01:
            raise ValueError(f'投資配置總和必須為100%，目前為{total}%')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "goal_name": "退休準備金",
                "target_amount": 10000000,
                "initial_amount": 1000000,
                "monthly_amount": 30000,
                "investment_period": 20,
                "risk_tolerance": "medium",
                "stock_allocation": 60.0,
                "bond_allocation": 20.0,
                "etf_allocation": 15.0,
                "deposit_allocation": 5.0
            }
        }
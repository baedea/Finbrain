import numpy as np
from typing import Dict, List, Optional
import math

from models.request_models import (
    BondDepositRequest, ETFInvestmentRequest, 
    HouseInvestmentRequest, StockSimulationRequest,
    FinancialGoalRequest
)
from models.response_models import (
    BondDepositResponse, ETFInvestmentResponse,
    HouseInvestmentResponse, StockSimulationResponse,
    FinancialGoalResponse, YearlyProjection, GoalAnalysis, RecommendationItem
)

class InvestmentCalculator:
    """統一的投資計算器"""
    
    def __init__(self):
        """初始化計算器"""
        self.risk_free_rate = 0.02  # 無風險利率 2%
        
    # =============== 債券/定存計算 ===============
    def calculate_bond_deposit(self, request: BondDepositRequest) -> BondDepositResponse:
        """債券/定存投資模擬計算"""
        try:
            # 輸入驗證
            if request.principal <= 0:
                raise ValueError("本金必須大於 0")
            if request.years <= 0:
                raise ValueError("投資年限必須大於 0")
            if request.interest_rate < 0:
                raise ValueError("利率不能為負數")
            
            # 將百分比轉換為小數
            interest_rate_decimal = request.interest_rate / 100
            inflation_rate_decimal = request.inflation_rate / 100
            
            # 計算最終價值 (名目價值)
            if request.is_compound:
                # 複利計算
                final_value = request.principal * (1 + interest_rate_decimal) ** request.years
            else:
                # 單利計算
                final_value = request.principal * (1 + interest_rate_decimal * request.years)
            
            # 計算實質價值 (扣除通膨影響)
            real_value = final_value / ((1 + inflation_rate_decimal) ** request.years)
            
            # 計算名目年化報酬率
            nominal_return = request.interest_rate
            
            # 計算實質年化報酬率
            # 使用費雪方程式: (1 + 實質利率) = (1 + 名目利率) / (1 + 通膨率)
            real_return = ((1 + interest_rate_decimal) / (1 + inflation_rate_decimal) - 1) * 100
            
            # 計算通膨影響金額
            inflation_impact = final_value - real_value
            
            # 計算總利息收入
            total_interest = final_value - request.principal
            
            return BondDepositResponse(
                success=True,
                final_value=round(final_value, 2),
                real_value=round(real_value, 2),
                nominal_return=round(nominal_return, 2),
                real_return=round(real_return, 2),
                inflation_impact=round(inflation_impact, 2),
                total_interest=round(total_interest, 2),
                inflation_loss=round(inflation_impact, 2)
            )
            
        except Exception as e:
            return BondDepositResponse(
                success=False,
                message=f"計算錯誤: {str(e)}",
                final_value=0, real_value=0, nominal_return=0, 
                real_return=0, inflation_impact=0, total_interest=0, inflation_loss=0
            )

    # =============== ETF定期定額計算 ===============
    def calculate_etf_investment(self, request: ETFInvestmentRequest) -> ETFInvestmentResponse:
        """ETF定期定額投資計算"""
        try:
            # 轉換百分比為小數
            dividend_rate = request.dividend_yield / 100
            growth_rate = request.price_growth / 100
            
            monthly_dividend_rate = dividend_rate / 12
            monthly_growth_rate = growth_rate / 12
            total_months = request.years * 12
            
            # 計算最終價值（考慮配息再投入）
            current_shares = 0  # 持有股數
            current_price = 100  # 假設初始股價為100（基準價格）
            total_dividend_income = 0  # 累積配息收入
            
            # 初始投入
            if request.initial_amount > 0:
                initial_shares = request.initial_amount / current_price
                current_shares += initial_shares
            
            # 逐月計算
            for month in range(total_months):
                # 股價成長
                current_price *= (1 + monthly_growth_rate)
                
                # 月配息（假設每月配息1/12）
                monthly_dividend = current_shares * current_price * monthly_dividend_rate
                total_dividend_income += monthly_dividend
                
                # 配息再投入購買股份
                if monthly_dividend > 0:
                    dividend_shares = monthly_dividend / current_price
                    current_shares += dividend_shares
                
                # 每月定投
                if request.monthly_amount > 0:
                    monthly_shares = request.monthly_amount / current_price
                    current_shares += monthly_shares
            
            # 最終價值
            final_value = current_shares * current_price
            
            # 計算總投資金額
            total_investment = request.initial_amount + request.monthly_amount * total_months
            
            # 計算獲利
            profit = final_value - total_investment
            
            # 計算資本利得
            capital_gain = final_value - total_investment - total_dividend_income
            
            # 計算年化報酬率
            if total_investment > 0:
                annualized_return = ((final_value / total_investment) ** (1/request.years) - 1) * 100
            else:
                annualized_return = 0
            
            # 簡化的IRR計算（避免使用scipy）
            try:
                irr = self._calculate_irr_simple(
                    total_investment, final_value, request.years, request.monthly_amount
                )
            except:
                irr = annualized_return
            
            # 計算投資報酬率 (ROI)
            if total_investment > 0:
                roi = (profit / total_investment) * 100
            else:
                roi = 0
            
            # 計算報酬來源比例
            if profit > 0:
                dividend_ratio = (total_dividend_income / profit) * 100
                capital_gain_ratio = (capital_gain / profit) * 100
            else:
                dividend_ratio = 0
                capital_gain_ratio = 0
            
            return ETFInvestmentResponse(
                success=True,
                final_value=round(final_value, 2),
                total_investment=round(total_investment, 2),
                profit=round(profit, 2),
                roi=round(roi, 2),
                irr=round(irr, 2),
                annualized_return=round(annualized_return, 2),
                dividend_income=round(total_dividend_income, 2),
                capital_gain=round(capital_gain, 2),
                dividend_ratio=round(dividend_ratio, 2),
                capital_gain_ratio=round(capital_gain_ratio, 2)
            )
            
        except Exception as e:
            return ETFInvestmentResponse(
                success=False,
                message=f"計算錯誤: {str(e)}",
                final_value=0, total_investment=0, profit=0, roi=0, irr=0,
                annualized_return=0, dividend_income=0, capital_gain=0,
                dividend_ratio=0, capital_gain_ratio=0
            )

    def _calculate_irr_simple(self, total_investment: float, final_value: float, 
                             years: int, monthly_amount: float) -> float:
        """簡化的IRR計算，避免使用scipy"""
        # 使用二分搜尋法來找IRR
        low_rate = -0.5  # -50%
        high_rate = 2.0  # 200%
        tolerance = 0.0001
        max_iterations = 100
        
        for _ in range(max_iterations):
            mid_rate = (low_rate + high_rate) / 2
            npv = self._calculate_npv(total_investment, final_value, years, monthly_amount, mid_rate)
            
            if abs(npv) < tolerance:
                return mid_rate * 100
            elif npv > 0:
                low_rate = mid_rate
            else:
                high_rate = mid_rate
        
        # 如果無法收斂，返回簡化的年化報酬率
        return ((final_value / total_investment) ** (1/years) - 1) * 100
    
    def _calculate_npv(self, total_investment: float, final_value: float, 
                      years: int, monthly_amount: float, rate: float) -> float:
        """計算淨現值"""
        npv = -total_investment
        npv += final_value / ((1 + rate) ** years)
        return npv

    # =============== 房屋投資分析 ===============
    def calculate_house_investment(self, request: HouseInvestmentRequest) -> HouseInvestmentResponse:
        """房屋投資分析計算"""
        try:
            # 計算貸款金額
            loan_amount = request.house_price - request.down_payment
            
            # 計算月利率
            monthly_rate = request.loan_rate / 100 / 12
            
            # 計算總還款月數
            total_months = request.loan_years * 12
            
            # 計算每月還款金額 (本息均攤)
            if monthly_rate > 0:
                monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** total_months) / \
                                 ((1 + monthly_rate) ** total_months - 1)
            else:
                monthly_payment = loan_amount / total_months
            
            if request.scenario == "A":
                # 情境A：持有simulation_years年後賣出
                
                # 使用情境A的漲幅
                annual_appreciation_rate = ((1 + request.appreciation_rate_a / 100) ** (1 / request.simulation_years) - 1) * 100
                current_value = request.house_price * (1 + request.appreciation_rate_a / 100)
                
                # 計算模擬期間的還款金額
                months_in_simulation = request.simulation_years * 12
                total_loan_payments = monthly_payment * months_in_simulation
                
                # 計算模擬期間已還本金
                if monthly_rate > 0:
                    # 使用貸款餘額公式計算剩餘本金
                    remaining_principal = loan_amount * ((1 + monthly_rate) ** total_months - 
                                                       (1 + monthly_rate) ** months_in_simulation) / \
                                         ((1 + monthly_rate) ** total_months - 1)
                else:
                    remaining_principal = loan_amount * (total_months - months_in_simulation) / total_months
                
                principal_paid = loan_amount - remaining_principal
                interest_paid = total_loan_payments - principal_paid
                
                # 計算持有成本
                total_holding_cost = request.annual_cost * request.simulation_years
                
                # 實際現金支出 = 頭期款 + 模擬期間還款 + 持有成本
                actual_cash_outflow = request.down_payment + total_loan_payments + total_holding_cost
                
                # 賣房實際收入 = 房屋現值 - 剩餘本金（還債）
                actual_sale_income = current_value - remaining_principal
                
                scenario_description = f"情境A：持有{request.simulation_years}年後賣出"
                
            else:  # scenario == "B"
                # 情境B：持有到貸款還完
                
                # 使用情境B的漲幅和貸款年限
                annual_appreciation_rate = ((1 + request.appreciation_rate_b / 100) ** (1 / request.loan_years) - 1) * 100
                current_value = request.house_price * (1 + request.appreciation_rate_b / 100)
                
                # 計算整個貸款期間的總還款
                total_loan_payments = monthly_payment * total_months
                
                # 計算整個買款期間的利息支出
                interest_paid = total_loan_payments - loan_amount
                
                # 計算持有成本（以貸款年限計算）
                total_holding_cost = request.annual_cost * request.loan_years
                
                # 實際現金支出 = 頭期款 + 全部還款 + 持有成本
                actual_cash_outflow = request.down_payment + total_loan_payments + total_holding_cost
                
                # 賣房實際收入 = 房屋現值（債務已還完）
                actual_sale_income = current_value
                
                remaining_principal = 0  # 貸款已還完
                scenario_description = f"情境B：持有到貸款還完({request.loan_years}年)"
            
            # 計算獲利 = 賣房實際收入 - 實際現金支出
            profit = actual_sale_income - actual_cash_outflow
            
            # 計算投資報酬率 = 獲利 / 實際現金支出 * 100
            roi = (profit / actual_cash_outflow) * 100 if actual_cash_outflow > 0 else 0
            
            # 計算額外分析數據
            down_payment_ratio = (request.down_payment / request.house_price) * 100
            leverage_ratio = request.house_price / request.down_payment if request.down_payment > 0 else 0
            
            return HouseInvestmentResponse(
                success=True,
                scenario=scenario_description,
                actual_cash_outflow=round(actual_cash_outflow, 0),
                actual_sale_income=round(actual_sale_income, 0),
                current_value=round(current_value, 0),
                profit=round(profit, 0),
                roi=round(roi, 2),
                annual_return=round(annual_appreciation_rate, 2),
                monthly_payment=round(monthly_payment, 0),
                loan_years=request.loan_years,
                interest_paid=round(interest_paid, 0),
                total_loan_payments=round(total_loan_payments, 0),
                remaining_principal=round(remaining_principal, 0),
                holding_cost=round(total_holding_cost, 0),
                loan_amount=round(loan_amount, 0),
                down_payment_ratio=round(down_payment_ratio, 2),
                leverage_ratio=round(leverage_ratio, 2)
            )
            
        except Exception as e:
            return HouseInvestmentResponse(
                success=False,
                message=f"計算錯誤: {str(e)}",
                scenario="", actual_cash_outflow=0, actual_sale_income=0,
                current_value=0, profit=0, roi=0, annual_return=0,
                monthly_payment=0, loan_years=0, interest_paid=0,
                total_loan_payments=0, remaining_principal=0, holding_cost=0,
                loan_amount=0, down_payment_ratio=0, leverage_ratio=0
            )

    # =============== 股票投資模擬 ===============
    def calculate_stock_simulation(self, request: StockSimulationRequest) -> StockSimulationResponse:
        """股票投資蒙地卡羅模擬"""
        try:
            # 轉換百分比為小數
            expected_return_decimal = request.expected_return / 100
            volatility_decimal = request.volatility / 100
            
            # 儲存所有模擬結果
            final_values = []
            
            # 執行蒙地卡羅模擬
            for _ in range(request.simulations):
                portfolio_value = request.initial_amount
                
                for year in range(request.years):
                    # 每年額外投入
                    portfolio_value += request.monthly_amount
                    
                    # 生成隨機年報酬率 (常態分布)
                    random_return = np.random.normal(expected_return_decimal, volatility_decimal)
                    
                    # 計算該年結束後的投資組合價值
                    portfolio_value *= (1 + random_return)
                
                final_values.append(portfolio_value)
            
            # 轉換為 numpy 陣列並排序
            final_values = np.array(final_values)
            final_values_sorted = np.sort(final_values)
            
            # 計算統計值
            mean = np.mean(final_values)
            percentile_5 = np.percentile(final_values_sorted, 5)
            percentile_95 = np.percentile(final_values_sorted, 95)
            total_investment = request.initial_amount + (request.monthly_amount * request.years)
            
            # 計算年化報酬率 = (最終價值 / 總投資金額) ^ (1/年數) - 1
            mean_return = (pow(mean / total_investment, 1/request.years) - 1) * 100
            worst_case = (pow(percentile_5 / total_investment, 1/request.years) - 1) * 100
            best_case = (pow(percentile_95 / total_investment, 1/request.years) - 1) * 100
            
            # 計算獲利機率
            profitable_simulations = np.sum(final_values > total_investment)
            probability_positive = (profitable_simulations / request.simulations) * 100
            
            # 計算風險指標
            value_at_risk = percentile_5
            expected_shortfall = np.mean(final_values[final_values <= percentile_5])
            
            # 計算實現波動率
            returns = (final_values / total_investment) - 1
            volatility_realized = np.std(returns) * 100
            
            return StockSimulationResponse(
                success=True,
                mean=round(mean, 0),
                percentile_5=round(percentile_5, 0),
                percentile_95=round(percentile_95, 0),
                total_investment=total_investment,
                mean_return=round(mean_return, 2),
                worst_case=round(worst_case, 2),
                best_case=round(best_case, 2),
                probability_positive=round(probability_positive, 2),
                value_at_risk=round(value_at_risk, 0),
                expected_shortfall=round(expected_shortfall, 0),
                simulation_count=request.simulations,
                volatility_realized=round(volatility_realized, 2)
            )
            
        except Exception as e:
            return StockSimulationResponse(
                success=False,
                message=f"計算錯誤: {str(e)}",
                mean=0, percentile_5=0, percentile_95=0, total_investment=0,
                mean_return=0, worst_case=0, best_case=0, probability_positive=0,
                value_at_risk=0, expected_shortfall=0, simulation_count=0, volatility_realized=0
            )

    # =============== 綜合財務目標計算 ===============
    def calculate_financial_goal(self, request: FinancialGoalRequest) -> FinancialGoalResponse:
        """綜合財務目標模擬計算"""
        try:
            # 計算投資組合預期報酬率和風險
            expected_return, portfolio_risk = self._calculate_portfolio_metrics(
                request.stock_allocation,
                request.bond_allocation, 
                request.etf_allocation,
                request.deposit_allocation
            )
            
            # 模擬投資成長
            projections = self._simulate_investment_growth(
                request.initial_amount,
                request.monthly_amount,
                expected_return,
                request.investment_period
            )
            
            final_projection = projections[-1]
            
            # 分析目標達成情況
            goal_analysis = None
            if request.target_amount:
                goal_analysis = self._analyze_goal_achievement(
                    request.target_amount,
                    final_projection.portfolio_value,
                    request.monthly_amount,
                    expected_return,
                    request.investment_period
                )
            
            # 產生投資建議
            recommendations = self._generate_recommendations(
                request, goal_analysis, portfolio_risk
            )
            
            # 準備圖表資料
            chart_data = {
                "years": [p.year for p in projections],
                "portfolio_values": [p.portfolio_value for p in projections],
                "total_investments": [p.total_investment for p in projections],
                "returns": [p.total_return for p in projections]
            }
            
            # 計算風險調整報酬率和夏普比率
            risk_adjusted_return = expected_return - portfolio_risk
            sharpe_ratio = (expected_return - self.risk_free_rate) / portfolio_risk if portfolio_risk > 0 else None
            
            return FinancialGoalResponse(
                success=True,
                goal_name=request.goal_name,
                projections=projections,
                final_amount=final_projection.portfolio_value,
                total_investment=final_projection.total_investment,
                total_return=final_projection.total_return,
                average_annual_return=final_projection.return_rate / request.investment_period,
                goal_analysis=goal_analysis,
                recommendations=recommendations,
                chart_data=chart_data,
                portfolio_risk=round(portfolio_risk * 100, 2),
                risk_adjusted_return=round(risk_adjusted_return * 100, 2),
                sharpe_ratio=round(sharpe_ratio, 2) if sharpe_ratio else None
            )
            
        except Exception as e:
            return FinancialGoalResponse(
                success=False,
                message=f"計算錯誤: {str(e)}",
                goal_name=request.goal_name,
                projections=[], final_amount=0, total_investment=0,
                total_return=0, average_annual_return=0, goal_analysis=None,
                recommendations=[], chart_data={}, portfolio_risk=0,
                risk_adjusted_return=0, sharpe_ratio=None
            )

    # =============== 輔助方法 ===============
    def _calculate_portfolio_metrics(self, stock_pct: float, bond_pct: float, 
                                   etf_pct: float, deposit_pct: float) -> tuple:
        """計算投資組合預期報酬率和風險"""
        # 各類資產的預期報酬率和風險
        asset_returns = {
            'stock': 0.12,    # 12% 股票
            'bond': 0.04,     # 4% 債券
            'etf': 0.08,      # 8% ETF
            'deposit': 0.02   # 2% 定存
        }
        
        asset_risks = {
            'stock': 0.20,    # 20% 股票風險
            'bond': 0.05,     # 5% 債券風險
            'etf': 0.15,      # 15% ETF風險
            'deposit': 0.01   # 1% 定存風險
        }
        
        # 計算加權平均報酬率
        expected_return = (
            (stock_pct / 100) * asset_returns['stock'] +
            (bond_pct / 100) * asset_returns['bond'] +
            (etf_pct / 100) * asset_returns['etf'] +
            (deposit_pct / 100) * asset_returns['deposit']
        )
        
        # 計算投資組合風險（簡化為加權平均）
        portfolio_risk = (
            (stock_pct / 100) * asset_risks['stock'] +
            (bond_pct / 100) * asset_risks['bond'] +
            (etf_pct / 100) * asset_risks['etf'] +
            (deposit_pct / 100) * asset_risks['deposit']
        )
        
        return expected_return, portfolio_risk

    def _simulate_investment_growth(self, initial_amount: float, monthly_amount: float,
                                  expected_return: float, years: int) -> List[YearlyProjection]:
        """模擬投資成長"""
        projections = []
        current_value = initial_amount
        total_invested = initial_amount
        
        for year in range(1, years + 1):
            # 年初加入月投資金額
            annual_investment = monthly_amount * 12
            total_invested += annual_investment
            current_value += annual_investment
            
            # 計算投資報酬
            current_value *= (1 + expected_return)
            total_return = current_value - total_invested
            return_rate = (total_return / total_invested) * 100 if total_invested > 0 else 0
            
            projections.append(YearlyProjection(
                year=year,
                total_investment=round(total_invested, 2),
                portfolio_value=round(current_value, 2),
                total_return=round(total_return, 2),
                return_rate=round(return_rate, 2)
            ))
        
        return projections

    def _analyze_goal_achievement(self, target_amount: float, final_amount: float,
                                monthly_amount: float, expected_return: float,
                                years: int) -> GoalAnalysis:
        """分析目標達成情況"""
        can_achieve = final_amount >= target_amount
        shortfall = max(0, target_amount - final_amount)
        
        # 計算達成目標所需的額外月投資
        if shortfall > 0:
            # 簡化計算：假設額外投資有相同報酬率
            required_increase = shortfall / (years * 12 * (1 + expected_return))
        else:
            required_increase = 0
        
        # 根據風險估算成功機率
        probability = 0.8 if can_achieve else 0.3
        
        return GoalAnalysis(
            can_achieve_goal=can_achieve,
            probability=probability,
            shortfall_amount=round(shortfall, 2),
            required_monthly_increase=round(required_increase, 2)
        )

    def _generate_recommendations(self, request: FinancialGoalRequest, 
                                goal_analysis: Optional[GoalAnalysis],
                                portfolio_risk: float) -> List[RecommendationItem]:
        """產生投資建議"""
        recommendations = []
        
        # 檢查目標達成
        if goal_analysis and not goal_analysis.can_achieve_goal:
            recommendations.append(RecommendationItem(
                type="目標調整",
                description=f"建議增加每月投資 ${goal_analysis.required_monthly_increase:,.0f} 或延長投資期間",
                impact="提高達標機率",
                priority=1
            ))
        
        # 檢查風險配置
        if request.stock_allocation > 70:
            recommendations.append(RecommendationItem(
                type="風險管理",
                description="股票配置過高，建議增加穩健型投資降低風險",
                impact="減少投資組合波動",
                priority=2
            ))
        
        if request.deposit_allocation > 50:
            recommendations.append(RecommendationItem(
                type="報酬優化", 
                description="定存比例過高，建議適度增加成長型投資",
                impact="提升長期報酬潛力",
                priority=2
            ))
        
        # 檢查投資期間
        if request.investment_period < 5:
            recommendations.append(RecommendationItem(
                type="時間規劃",
                description="投資期間較短，建議採用較保守的配置策略",
                impact="降低短期波動風險",
                priority=3
            ))
        
        return recommendations
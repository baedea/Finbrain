// 主要應用程式類別
class InvestmentApp {
    constructor() {
        this.currentTab = 'bond';
        this.charts = {};
        this.init();
    }

    // 初始化應用程式
    init() {
        this.setupTabs();
        this.setupForms();
        this.setupValidation();
        this.loadInitialData();
    }

    // 設定標籤切換
    setupTabs() {
        const tabBtns = document.querySelectorAll('.tab-btn');
        const tabContents = document.querySelectorAll('.tab-content');

        tabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const tabId = btn.dataset.tab;
                
                // 更新按鈕狀態
                tabBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                // 更新內容顯示
                tabContents.forEach(content => {
                    content.classList.remove('active');
                });
                document.getElementById(tabId).classList.add('active');
                
                this.currentTab = tabId;
                APIUtils.clearResult(`${tabId}-result`);
            });
        });
    }

    // 設定表單提交
    setupForms() {
        // 債券/定存表單
        document.getElementById('bond-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleBondCalculation(e.target);
        });

        // ETF投資表單
        document.getElementById('etf-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleETFCalculation(e.target);
        });

        // 房屋投資表單
        document.getElementById('house-form').addEventListener('submit', async (e) => {
            e.preventDefault();  
            await this.handleHouseCalculation(e.target);
        });

        // 股票模擬表單
        document.getElementById('stock-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleStockCalculation(e.target);
        });

        // 財務目標表單
        document.getElementById('goal-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleGoalCalculation(e.target);
        });
    }

    // 設定即時驗證
    setupValidation() {
        // 財務目標配置比例即時計算
        const allocationInputs = document.querySelectorAll('#goal input[name$="_allocation"]');
        allocationInputs.forEach(input => {
            input.addEventListener('input', this.updateAllocationTotal);
        });
    }

    // 更新配置總計
    updateAllocationTotal() {
        const stockAllocation = parseFloat(document.querySelector('input[name="stock_allocation"]').value) || 0;
        const bondAllocation = parseFloat(document.querySelector('input[name="bond_allocation"]').value) || 0;
        const etfAllocation = parseFloat(document.querySelector('input[name="etf_allocation"]').value) || 0;
        const depositAllocation = parseFloat(document.querySelector('input[name="deposit_allocation"]').value) || 0;
        
        const total = stockAllocation + bondAllocation + etfAllocation + depositAllocation;
        const totalElement = document.getElementById('total-allocation');
        
        totalElement.textContent = total;
        totalElement.style.color = total === 100 ? '#28a745' : total > 100 ? '#dc3545' : '#ffc107';
    }

    // 載入初始數據
    async loadInitialData() {
        try {
            // 可以在這裡載入投資類型等初始數據
            // const types = await api.getInvestmentTypes();
            // console.log('可用投資類型:', types);
        } catch (error) {
            console.warn('載入初始數據失敗:', error);
        }
    }

    // 債券/定存計算處理
    async handleBondCalculation(form) {
        try {
            APIUtils.showLoading();
            
            const formData = new FormData(form);
            const data = APIUtils.formDataToObject(formData);
            
            // 處理複選框
            data.is_compound = form.querySelector('input[name="is_compound"]').checked;
            
            const result = await api.calculateBondDeposit(data);
            this.displayBondResult(result);
            
        } catch (error) {
            APIUtils.showError(document.getElementById('bond-result'), error.message);
        } finally {
            APIUtils.hideLoading();
        }
    }

    // ETF投資計算處理
    async handleETFCalculation(form) {
        try {
            APIUtils.showLoading();
            
            const formData = new FormData(form);
            const data = APIUtils.formDataToObject(formData);
            
            const result = await api.calculateETFInvestment(data);
            this.displayETFResult(result);
            
        } catch (error) {
            APIUtils.showError(document.getElementById('etf-result'), error.message);
        } finally {
            APIUtils.hideLoading();
        }
    }

    // 房屋投資計算處理
    async handleHouseCalculation(form) {
        try {
            APIUtils.showLoading();
            
            const formData = new FormData(form);
            const data = APIUtils.formDataToObject(formData);
            
            const result = await api.calculateHouseInvestment(data);
            this.displayHouseResult(result);
            
        } catch (error) {
            APIUtils.showError(document.getElementById('house-result'), error.message);
        } finally {
            APIUtils.hideLoading();
        }
    }

    // 股票模擬計算處理
    async handleStockCalculation(form) {
        try {
            APIUtils.showLoading();
            
            const formData = new FormData(form);
            const data = APIUtils.formDataToObject(formData);
            
            const result = await api.calculateStockSimulation(data);
            this.displayStockResult(result);
            
        } catch (error) {
            APIUtils.showError(document.getElementById('stock-result'), error.message);
        } finally {
            APIUtils.hideLoading();
        }
    }

    // 財務目標計算處理
    async handleGoalCalculation(form) {
        try {
            APIUtils.showLoading();
            
            const formData = new FormData(form);
            const data = APIUtils.formDataToObject(formData);
            
            // 驗證配置總和
            const total = data.stock_allocation + data.bond_allocation + data.etf_allocation + data.deposit_allocation;
            if (Math.abs(total - 100) > 0.01) {
                throw new Error(`投資配置總和必須為100%，目前為${total}%`);
            }
            
            const result = await api.calculateFinancialGoal(data);
            this.displayGoalResult(result);
            
        } catch (error) {
            APIUtils.showError(document.getElementById('goal-result'), error.message);
        } finally {
            APIUtils.hideLoading();
        }
    }

    // 顯示債券/定存結果
    displayBondResult(result) {
        const container = document.getElementById('bond-result');
        
        container.innerHTML = `
            <h3>計算結果</h3>
            <div class="result-grid">
                <div class="result-item">
                    <div class="label">最終價值 (名目)</div>
                    <div class="value">${APIUtils.formatCurrency(result.final_value)}</div>
                </div>
                <div class="result-item">
                    <div class="label">實質價值 (扣除通膨)</div>
                    <div class="value">${APIUtils.formatCurrency(result.real_value)}</div>
                </div>
                <div class="result-item">
                    <div class="label">名目年化報酬率</div>
                    <div class="value positive">${APIUtils.formatPercentage(result.nominal_return)}</div>
                </div>
                <div class="result-item">
                    <div class="label">實質年化報酬率</div>
                    <div class="value ${result.real_return > 0 ? 'positive' : 'negative'}">${APIUtils.formatPercentage(result.real_return)}</div>
                </div>
                <div class="result-item">
                    <div class="label">總利息收入</div>
                    <div class="value positive">${APIUtils.formatCurrency(result.total_interest)}</div>
                </div>
                <div class="result-item">
                    <div class="label">通膨損失</div>
                    <div class="value negative">${APIUtils.formatCurrency(result.inflation_impact)}</div>
                </div>
            </div>
        `;
        
        container.classList.add('show');
    }

    // 顯示ETF投資結果
    displayETFResult(result) {
        const container = document.getElementById('etf-result');
        
        container.innerHTML = `
            <h3>ETF投資結果</h3>
            <div class="result-grid">
                <div class="result-item">
                    <div class="label">最終價值</div>
                    <div class="value">${APIUtils.formatCurrency(result.final_value)}</div>
                </div>
                <div class="result-item">
                    <div class="label">總投資金額</div>
                    <div class="value">${APIUtils.formatCurrency(result.total_investment)}</div>
                </div>
                <div class="result-item">
                    <div class="label">總獲利</div>
                    <div class="value ${result.profit > 0 ? 'positive' : 'negative'}">${APIUtils.formatCurrency(result.profit)}</div>
                </div>
                <div class="result-item">
                    <div class="label">投資報酬率</div>
                    <div class="value ${result.roi > 0 ? 'positive' : 'negative'}">${APIUtils.formatPercentage(result.roi)}</div>
                </div>
                <div class="result-item">
                    <div class="label">年化報酬率</div>
                    <div class="value ${result.annualized_return > 0 ? 'positive' : 'negative'}">${APIUtils.formatPercentage(result.annualized_return)}</div>
                </div>
                <div class="result-item">
                    <div class="label">內部報酬率 (IRR)</div>
                    <div class="value ${result.irr > 0 ? 'positive' : 'negative'}">${APIUtils.formatPercentage(result.irr)}</div>
                </div>
            </div>
            <h4>報酬來源分析</h4>
            <div class="result-grid">
                <div class="result-item">
                    <div class="label">配息收入</div>
                    <div class="value positive">${APIUtils.formatCurrency(result.dividend_income)}</div>
                </div>
                <div class="result-item">
                    <div class="label">資本利得</div>
                    <div class="value positive">${APIUtils.formatCurrency(result.capital_gain)}</div>
                </div>
                <div class="result-item">
                    <div class="label">配息占比</div>
                    <div class="value">${APIUtils.formatPercentage(result.dividend_ratio)}</div>
                </div>
                <div class="result-item">
                    <div class="label">資本利得占比</div>
                    <div class="value">${APIUtils.formatPercentage(result.capital_gain_ratio)}</div>
                </div>
            </div>
        `;
        
        container.classList.add('show');
    }

    // 顯示房屋投資結果
    displayHouseResult(result) {
        const container = document.getElementById('house-result');
        
        container.innerHTML = `
            <h3>房屋投資分析結果</h3>
            <p><strong>${result.scenario}</strong></p>
            <div class="result-grid">
                <div class="result-item">
                    <div class="label">實際現金支出</div>
                    <div class="value">${APIUtils.formatCurrency(result.actual_cash_outflow)}</div>
                </div>
                <div class="result-item">
                    <div class="label">賣房實際收入</div>
                    <div class="value">${APIUtils.formatCurrency(result.actual_sale_income)}</div>
                </div>
                <div class="result-item">
                    <div class="label">房屋現值</div>
                    <div class="value">${APIUtils.formatCurrency(result.current_value)}</div>
                </div>
                <div class="result-item">
                    <div class="label">投資獲利</div>
                    <div class="value ${result.profit > 0 ? 'positive' : 'negative'}">${APIUtils.formatCurrency(result.profit)}</div>
                </div>
                <div class="result-item">
                    <div class="label">投資報酬率</div>
                    <div class="value ${result.roi > 0 ? 'positive' : 'negative'}">${APIUtils.formatPercentage(result.roi)}</div>
                </div>
                <div class="result-item">
                    <div class="label">年化報酬率</div>
                    <div class="value ${result.annual_return > 0 ? 'positive' : 'negative'}">${APIUtils.formatPercentage(result.annual_return)}</div>
                </div>
            </div>
            <h4>貸款詳細資訊</h4>
            <div class="result-grid">
                <div class="result-item">
                    <div class="label">貸款金額</div>
                    <div class="value">${APIUtils.formatCurrency(result.loan_amount)}</div>
                </div>
                <div class="result-item">
                    <div class="label">每月還款</div>
                    <div class="value">${APIUtils.formatCurrency(result.monthly_payment)}</div>
                </div>
                <div class="result-item">
                    <div class="label">利息支出</div>
                    <div class="value negative">${APIUtils.formatCurrency(result.interest_paid)}</div>
                </div>
                <div class="result-item">
                    <div class="label">剩餘本金</div>
                    <div class="value">${APIUtils.formatCurrency(result.remaining_principal)}</div>
                </div>
                <div class="result-item">
                    <div class="label">持有成本</div>
                    <div class="value negative">${APIUtils.formatCurrency(result.holding_cost)}</div>
                </div>
                <div class="result-item">
                    <div class="label">槓桿比例</div>
                    <div class="value">${APIUtils.formatNumber(result.leverage_ratio, 1)}倍</div>
                </div>
            </div>
        `;
        
        container.classList.add('show');
    }

    // 顯示股票模擬結果
    displayStockResult(result) {
        const container = document.getElementById('stock-result');
        
        container.innerHTML = `
            <h3>股票投資模擬結果</h3>
            <p>基於 ${APIUtils.formatNumber(result.simulation_count)} 次蒙地卡羅模擬</p>
            <div class="result-grid">
                <div class="result-item">
                    <div class="label">預期最終價值</div>
                    <div class="value">${APIUtils.formatCurrency(result.mean)}</div>
                </div>
                <div class="result-item">
                    <div class="label">總投資金額</div>
                    <div class="value">${APIUtils.formatCurrency(result.total_investment)}</div>
                </div>
                <div class="result-item">
                    <div class="label">平均年化報酬率</div>
                    <div class="value ${result.mean_return > 0 ? 'positive' : 'negative'}">${APIUtils.formatPercentage(result.mean_return)}</div>
                </div>
                <div class="result-item">
                    <div class="label">獲利機率</div>
                    <div class="value ${result.probability_positive > 50 ? 'positive' : 'negative'}">${APIUtils.formatPercentage(result.probability_positive)}</div>
                </div>
            </div>
            <h4>風險分析</h4>
            <div class="result-grid">
                <div class="result-item">
                    <div class="label">最佳情況 (95%)</div>
                    <div class="value positive">${APIUtils.formatCurrency(result.percentile_95)}</div>
                </div>
                <div class="result-item">
                    <div class="label">最差情況 (5%)</div>
                    <div class="value negative">${APIUtils.formatCurrency(result.percentile_5)}</div>
                </div>
                <div class="result-item">
                    <div class="label">最佳年化報酬</div>
                    <div class="value positive">${APIUtils.formatPercentage(result.best_case)}</div>
                </div>
                <div class="result-item">
                    <div class="label">最差年化報酬</div>
                    <div class="value negative">${APIUtils.formatPercentage(result.worst_case)}</div>
                </div>
                <div class="result-item">
                    <div class="label">風險價值 (VaR)</div>
                    <div class="value">${APIUtils.formatCurrency(result.value_at_risk)}</div>
                </div>
                <div class="result-item">
                    <div class="label">實現波動率</div>
                    <div class="value">${APIUtils.formatPercentage(result.volatility_realized)}</div>
                </div>
            </div>
        `;
        
        container.classList.add('show');
    }

    // 顯示財務目標結果
    displayGoalResult(result) {
        const container = document.getElementById('goal-result');
        
        let goalAnalysisHtml = '';
        if (result.goal_analysis) {
            const analysis = result.goal_analysis;
            goalAnalysisHtml = `
                <h4>目標達成分析</h4>
                <div class="result-grid">
                    <div class="result-item">
                        <div class="label">能否達成目標</div>
                        <div class="value ${analysis.can_achieve_goal ? 'positive' : 'negative'}">
                            ${analysis.can_achieve_goal ? '✅ 可以達成' : '❌ 無法達成'}
                        </div>
                    </div>
                    <div class="result-item">
                        <div class="label">達成機率</div>
                        <div class="value">${APIUtils.formatPercentage(analysis.probability * 100)}</div>
                    </div>
                    ${analysis.shortfall_amount > 0 ? `
                        <div class="result-item">
                            <div class="label">不足金額</div>
                            <div class="value negative">${APIUtils.formatCurrency(analysis.shortfall_amount)}</div>
                        </div>
                        <div class="result-item">
                            <div class="label">需增加月投資</div>
                            <div class="value">${APIUtils.formatCurrency(analysis.required_monthly_increase)}</div>
                        </div>
                    ` : ''}
                </div>
            `;
        }

        let recommendationsHtml = '';
        if (result.recommendations && result.recommendations.length > 0) {
            recommendationsHtml = `
                <div class="recommendations">
                    <h4>投資建議</h4>
                    ${result.recommendations.map(rec => `
                        <div class="recommendation-item">
                            <div class="type">${rec.type}</div>
                            <div class="description">${rec.description}</div>
                            <div class="impact">影響: ${rec.impact}</div>
                        </div>
                    `).join('')}
                </div>
            `;
        }

        container.innerHTML = `
            <h3>${result.goal_name} - 財務目標分析</h3>
            <div class="result-grid">
                <div class="result-item">
                    <div class="label">預期最終資產</div>
                    <div class="value">${APIUtils.formatCurrency(result.final_amount)}</div>
                </div>
                <div class="result-item">
                    <div class="label">總投資金額</div>
                    <div class="value">${APIUtils.formatCurrency(result.total_investment)}</div>
                </div>
                <div class="result-item">
                    <div class="label">總報酬</div>
                    <div class="value ${result.total_return > 0 ? 'positive' : 'negative'}">${APIUtils.formatCurrency(result.total_return)}</div>
                </div>
                <div class="result-item">
                    <div class="label">平均年化報酬率</div>
                    <div class="value ${result.average_annual_return > 0 ? 'positive' : 'negative'}">${APIUtils.formatPercentage(result.average_annual_return)}</div>
                </div>
                <div class="result-item">
                    <div class="label">投資組合風險</div>
                    <div class="value">${APIUtils.formatPercentage(result.portfolio_risk)}</div>
                </div>
                ${result.sharpe_ratio ? `
                    <div class="result-item">
                        <div class="label">夏普比率</div>
                        <div class="value">${APIUtils.formatNumber(result.sharpe_ratio, 2)}</div>
                    </div>
                ` : ''}
            </div>
            ${goalAnalysisHtml}
            ${recommendationsHtml}
        `;
        
        container.classList.add('show');

        // 繪製圖表
        if (result.chart_data && result.chart_data.years) {
            this.drawGoalChart(result.chart_data);
        }
    }

    // 繪製財務目標圖表
    drawGoalChart(chartData) {
        const canvas = document.getElementById('goal-chart');
        canvas.style.display = 'block';
        
        // 清除舊圖表
        if (this.charts.goal) {
            this.charts.goal.destroy();
        }

        const ctx = canvas.getContext('2d');
        this.charts.goal = new Chart(ctx, {
            type: 'line',
            data: {
                labels: chartData.years,
                datasets: [
                    {
                        label: '投資組合價值',
                        data: chartData.portfolio_values,
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: '累積投入',
                        data: chartData.total_investments,
                        borderColor: '#764ba2',
                        backgroundColor: 'rgba(118, 75, 162, 0.1)',
                        fill: true,
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: '投資成長預測圖'
                    },
                    legend: {
                        display: true
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '₹' + (value / 1000000).toFixed(1) + 'M';
                            }
                        }
                    }
                }
            }
        });
    }
}

// 應用程式初始化
document.addEventListener('DOMContentLoaded', () => {
    const app = new InvestmentApp();
});
// API 基礎設定
const API_BASE = '/api/v1';

// API 呼叫封裝類別
class InvestmentAPI {
    constructor() {
        this.baseURL = API_BASE;
    }

    // 通用 API 呼叫方法
    async call(endpoint, data = null, method = 'GET') {
        try {
            const config = {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
            };

            if (data && method !== 'GET') {
                config.body = JSON.stringify(data);
            }

            const response = await fetch(`${this.baseURL}${endpoint}`, config);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => null);
                throw new Error(errorData?.detail || `HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`API 呼叫錯誤 (${endpoint}):`, error);
            throw error;
        }
    }

    // 債券/定存計算
    async calculateBondDeposit(data) {
        return await this.call('/bond-deposit', data, 'POST');
    }

    // ETF定期定額計算
    async calculateETFInvestment(data) {
        return await this.call('/etf-investment', data, 'POST');
    }

    // 房屋投資分析
    async calculateHouseInvestment(data) {
        return await this.call('/house-investment', data, 'POST');
    }

    // 股票投資模擬
    async calculateStockSimulation(data) {
        return await this.call('/stock-simulation', data, 'POST');
    }

    // 財務目標規劃
    async calculateFinancialGoal(data) {
        return await this.call('/financial-goal', data, 'POST');
    }

    // 取得投資類型
    async getInvestmentTypes() {
        return await this.call('/investment-types');
    }

    // 健康檢查
    async healthCheck() {
        return await this.call('/health');
    }

    // 批量比較 (如果後端有實作)
    async batchCompare(bondData, etfData, stockData) {
        return await this.call('/batch-compare', {
            bond_request: bondData,
            etf_request: etfData,
            stock_request: stockData
        }, 'POST');
    }
}

// 工具函數
class APIUtils {
    // 格式化數字為台幣
    static formatCurrency(amount) {
        if (typeof amount !== 'number') return 'N/A';
        return new Intl.NumberFormat('zh-TW', {
            style: 'currency',
            currency: 'TWD',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0,
        }).format(amount);
    }

    // 格式化百分比
    static formatPercentage(value, decimals = 2) {
        if (typeof value !== 'number') return 'N/A';
        return `${value.toFixed(decimals)}%`;
    }

    // 格式化數字 (千分位)
    static formatNumber(value, decimals = 0) {
        if (typeof value !== 'number') return 'N/A';
        return new Intl.NumberFormat('zh-TW', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals,
        }).format(value);
    }

    // 表單數據轉換
    static formDataToObject(formData) {
        const obj = {};
        for (let [key, value] of formData.entries()) {
            // 處理數字欄位
            if (value === '' || value === null) {
                obj[key] = null;
            } else if (!isNaN(value) && value !== '') {
                obj[key] = parseFloat(value);
            } else if (value === 'true') {
                obj[key] = true;
            } else if (value === 'false') {
                obj[key] = false;
            } else {
                obj[key] = value;
            }
        }
        return obj;
    }

    // 驗證表單數據
    static validateFormData(data, requiredFields = []) {
        const errors = [];
        
        for (const field of requiredFields) {
            if (data[field] === undefined || data[field] === null || data[field] === '') {
                errors.push(`${field} 為必填欄位`);
            }
        }

        return errors;
    }

    // 顯示錯誤訊息
    static showError(container, message) {
        container.innerHTML = `
            <div class="error">
                <strong>錯誤:</strong> ${message}
            </div>
        `;
        container.classList.add('show');
    }

    // 顯示成功訊息
    static showSuccess(container, message) {
        container.innerHTML = `
            <div class="success">
                ${message}
            </div>
        `;
        container.classList.add('show');
    }

    // 載入狀態控制
    static showLoading() {
        document.getElementById('loading').classList.add('show');
    }

    static hideLoading() {
        document.getElementById('loading').classList.remove('show');
    }

    // 清除結果
    static clearResult(containerId) {
        const container = document.getElementById(containerId);
        container.classList.remove('show');
        container.innerHTML = '';
    }
}

// 全域 API 實例
const api = new InvestmentAPI();
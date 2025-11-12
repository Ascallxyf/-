// 智能穿搭推荐平台 - 主 JavaScript 文件

// API 基础 URL
const API_BASE_URL = '/api';

// 工具函数: 发送 API 请求
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        },
        ...options
    };

    try {
        const response = await fetch(url, config);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || '请求失败');
        }

        return data;
    } catch (error) {
        console.error('API 请求错误:', error);
        showNotification(error.message, 'error');
        throw error;
    }
}

// 工具函数: 显示通知
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 25px;
        background: ${type === 'error' ? '#e74c3c' : type === 'success' ? '#2ecc71' : '#4a90e2'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// 工具函数: 格式化日期
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    });
}

// 工具函数: 显示加载状态
function showLoading(element) {
    element.disabled = true;
    element.innerHTML = '<span class="loading"></span> 加载中...';
}

function hideLoading(element, originalText) {
    element.disabled = false;
    element.innerHTML = originalText;
}

// 衣橱管理
class WardrobeManager {
    async getItems() {
        return await apiRequest('/wardrobe/items');
    }

    async addItem(itemData) {
        return await apiRequest('/wardrobe/items', {
            method: 'POST',
            body: JSON.stringify(itemData)
        });
    }

    async deleteItem(itemId) {
        return await apiRequest(`/wardrobe/items/${itemId}`, {
            method: 'DELETE'
        });
    }

    async updateItem(itemId, itemData) {
        return await apiRequest(`/wardrobe/items/${itemId}`, {
            method: 'PUT',
            body: JSON.stringify(itemData)
        });
    }
}

// 推荐服务
class RecommendationService {
    async getRecommendations(context = {}) {
        return await apiRequest('/recommend/outfit', {
            method: 'POST',
            body: JSON.stringify(context)
        });
    }

    async analyzeStyle(imageUrl) {
        return await apiRequest('/recommend/style', {
            method: 'POST',
            body: JSON.stringify({ image_url: imageUrl })
        });
    }

    async getHistory() {
        return await apiRequest('/recommend/history');
    }
}

// 用户画像管理
class UserProfileManager {
    async getProfile() {
        return await apiRequest('/user/profile');
    }

    async updateProfile(profileData) {
        return await apiRequest('/user/profile', {
            method: 'PUT',
            body: JSON.stringify(profileData)
        });
    }
}

// 全局实例
const wardrobeManager = new WardrobeManager();
const recommendationService = new RecommendationService();
const userProfileManager = new UserProfileManager();

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    console.log('智能穿搭推荐平台已加载');

    // 添加动画样式
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
});

// 导出到全局
window.apiRequest = apiRequest;
window.showNotification = showNotification;
window.formatDate = formatDate;
window.wardrobeManager = wardrobeManager;
window.recommendationService = recommendationService;
window.userProfileManager = userProfileManager;

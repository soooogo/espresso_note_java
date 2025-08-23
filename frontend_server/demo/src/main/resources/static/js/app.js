// API ベースURL
const API_BASE_URL = '/api';

// 共通のAPI通信関数
class ApiService {
    static async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };
        
        const finalOptions = { ...defaultOptions, ...options };
        
        try {
            const response = await fetch(url, finalOptions);
            
            if (!response.ok) {
                if (response.status === 401) {
                    // 認証エラーの場合はログインページにリダイレクト
                    window.location.href = '/login';
                    return;
                }
                
                // エラーレスポンスの詳細を取得
                let errorData = null;
                try {
                    errorData = await response.text();
                } catch (e) {
                    errorData = `HTTP error! status: ${response.status}`;
                }
                
                const error = new Error(`HTTP error! status: ${response.status}`);
                error.response = { status: response.status, data: errorData };
                throw error;
            }
            
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }
    
    static async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }
    
    static async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }
    
    static async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }
    
    static async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }
}

// ユーティリティ関数
class Utils {
    static showAlert(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`;
        alertDiv.textContent = message;
        
        const container = document.querySelector('.main-content');
        container.insertBefore(alertDiv, container.firstChild);
        
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
    
    static formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('ja-JP');
    }
    
    static validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }
    
    static showLoading(element) {
        element.innerHTML = '<div class="loading">読み込み中...</div>';
    }
    
    static hideLoading(element) {
        element.innerHTML = '';
    }
}

// フォーム処理
class FormHandler {
    static getFormData(formElement) {
        const formData = new FormData(formElement);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }
        
        return data;
    }
    
    static clearForm(formElement) {
        formElement.reset();
    }
    
    static validateRequired(formElement) {
        const requiredFields = formElement.querySelectorAll('[required]');
        let isValid = true;
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.style.borderColor = '#dc3545';
                isValid = false;
            } else {
                field.style.borderColor = '#e1e5e9';
            }
        });
        
        return isValid;
    }
}

// ページナビゲーション
class Navigation {
    static navigateTo(page) {
        window.location.href = page;
    }
    
    static setActiveNavLink(pageName) {
        const navLinks = document.querySelectorAll('.nav-links a');
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === pageName) {
                link.classList.add('active');
            }
        });
    }
}

// データテーブル
class DataTable {
    static createTable(data, columns) {
        if (!data || data.length === 0) {
            return '<p>データがありません</p>';
        }
        
        let table = '<table class="table">';
        
        // ヘッダー
        table += '<thead><tr>';
        columns.forEach(column => {
            table += `<th>${column.header}</th>`;
        });
        table += '</tr></thead>';
        
        // ボディ
        table += '<tbody>';
        data.forEach(row => {
            table += '<tr>';
            columns.forEach(column => {
                const value = column.render ? column.render(row[column.key], row) : row[column.key];
                table += `<td>${value}</td>`;
            });
            table += '</tr>';
        });
        table += '</tbody></table>';
        
        return table;
    }
}

// モーダル
class Modal {
    static show(title, content) {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>${title}</h3>
                    <span class="modal-close">&times;</span>
                </div>
                <div class="modal-body">
                    ${content}
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // 閉じる機能
        const closeBtn = modal.querySelector('.modal-close');
        closeBtn.onclick = () => this.hide(modal);
        
        modal.onclick = (e) => {
            if (e.target === modal) {
                this.hide(modal);
            }
        };
    }
    
    static hide(modal) {
        modal.remove();
    }
}

// ページ読み込み時の初期化
document.addEventListener('DOMContentLoaded', function() {
    // 現在のページに応じてナビゲーションをアクティブにする
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    Navigation.setActiveNavLink(currentPage);
    
    // フェードインアニメーション
    const mainContent = document.querySelector('.main-content');
    if (mainContent) {
        mainContent.classList.add('fade-in');
    }
});

// グローバルエラーハンドラー
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    Utils.showAlert('エラーが発生しました', 'danger');
});

// 未処理のPromiseエラー
window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
    Utils.showAlert('エラーが発生しました', 'danger');
});

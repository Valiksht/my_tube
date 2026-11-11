// YouTube Clone - JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // CSRF токен для AJAX запросов
    const csrfToken = getCSRFToken();
    
    // Обработка форм с AJAX
    initFormHandlers();
    
    // Обработка уведомлений
    showNotifications();
});

// Получить CSRF токен из Cookie
function getCSRFToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name.includes('_csrf')) {
            return decodeURIComponent(value);
        }
    }
    return '';
}

// Инициализация обработчиков форм
function initFormHandlers() {
    // Logout формы
    document.querySelectorAll('.logout-form').forEach(form => {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            try {
                const response = await fetch('/api/auth/logout', {
                    method: 'POST',
                    credentials: 'include',
                    headers: {
                        'X-CSRF-Token': getCSRFToken()
                    }
                });
                if (response.ok) {
                    window.location.href = '/';
                }
            } catch (error) {
                console.error('Logout error:', error);
            }
        });
    });
}

// Показать уведомления
function showNotifications() {
    // Можно добавить систему уведомлений здесь
}

// Показать алерт
function showAlert(message, type = 'error') {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    
    const container = document.querySelector('.auth-card') || document.querySelector('.main');
    if (container) {
        container.insertBefore(alert, container.firstChild);
        setTimeout(() => alert.remove(), 5000);
    }
}

// Форматирование чисел (1000 -> 1K)
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

// YouTube Clone - JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initFormHandlers();
    initSearchAutofocus();
});

// Получить CSRF токен из meta-тега
function getCSRFToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    if (meta) {
        return meta.getAttribute('content') || '';
    }
    return '';
}

// Получить CSRF токен из hidden input
function getCSRFTokenFromForm() {
    const input = document.querySelector('input[name="csrf_token"]');
    if (input) {
        return input.value || '';
    }
    return getCSRFToken();
}

// Добавить CSRF-токен ко всем формам
function addCSRFToForms() {
    document.querySelectorAll('form[method="POST"], form[method="post"]').forEach(function(form) {
        if (form.querySelector('input[name="csrf_token"]')) {
            return;
        }
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'csrf_token';
        input.value = getCSRFToken();
        form.insertBefore(input, form.firstChild);
    });
}

// Инициализация обработчиков форм
function initFormHandlers() {
    addCSRFToForms();
    
    // Logout формы
    document.querySelectorAll('.logout-form').forEach(function(form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            var action = form.getAttribute('action');
            fetch(action, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'X-CSRF-Token': getCSRFToken()
                }
            })
            .then(function(response) {
                if (response.ok || response.status === 302) {
                    window.location.href = '/';
                }
            })
            .catch(function(error) {
                console.error('Logout error:', error);
            });
        });
    });
    
    // Like кнопки
    document.querySelectorAll('.like-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            var videoId = this.dataset.videoId;
            var countEl = this.querySelector('.like-count');
            
            fetch('/api/videos/' + videoId + '/likes', {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'X-CSRF-Token': getCSRFToken()
                }
            })
            .then(function(response) {
                if (response.ok) {
                    return fetch('/api/videos/' + videoId + '/likes/count');
                }
                throw new Error('Like failed');
            })
            .then(function(response) {
                return response.json();
            })
            .then(function(data) {
                if (countEl) {
                    countEl.textContent = formatNumber(data.like_count);
                }
            })
            .catch(function(error) {
                console.error('Error:', error);
                showAlert('Не удалось обработать лайк', 'error');
            });
        });
    });
    
    // Subscribe кнопки
    document.querySelectorAll('.subscribe-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            var channelId = this.dataset.channelId;
            
            fetch('/api/channels/' + channelId + '/subscriptions', {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'X-CSRF-Token': getCSRFToken()
                }
            })
            .then(function(response) {
                if (response.ok) {
                    var text = btn.textContent.trim();
                    btn.textContent = text === 'Подписаться' ? 'Отписаться' : 'Подписаться';
                    
                    var countEl = document.querySelector('.channel-subscribers');
                    if (countEl) {
                        return fetch('/api/channels/' + channelId + '/subscriptions/count')
                            .then(function(r) { return r.json(); })
                            .then(function(data) {
                                countEl.textContent = data.subscriber_count + ' подписчиков';
                            });
                    }
                }
                throw new Error('Subscribe failed');
            })
            .catch(function(error) {
                console.error('Error:', error);
                showAlert('Не удалось обновить подписку', 'error');
            });
        });
    });
    
    // Report кнопки
    document.querySelectorAll('.report-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            var targetId = this.dataset.targetId;
            var targetType = this.dataset.targetType;
            var reason = prompt('Причина жалобы:');
            if (reason && reason.length > 10) {
                fetch('/api/moderation/reports', {
                    method: 'POST',
                    credentials: 'include',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRF-Token': getCSRFToken()
                    },
                    body: JSON.stringify({
                        target_type: targetType,
                        target_id: parseInt(targetId),
                        reason: reason
                    })
                })
                .then(function(response) {
                    if (response.ok) {
                        showAlert('Жалоба отправлена', 'success');
                    } else {
                        throw new Error('Report failed');
                    }
                })
                .catch(function(error) {
                    console.error('Error:', error);
                    showAlert('Не удалось отправить жалобу', 'error');
                });
            } else if (reason) {
                showAlert('Причина должна содержать минимум 10 символов', 'error');
            }
        });
    });
}

// Фокус на поле поиска
function initSearchAutofocus() {
    var searchInput = document.querySelector('.search-form input[name="q"]');
    if (searchInput && !searchInput.value) {
        searchInput.focus();
    }
}

// Показать алерт
function showAlert(message, type) {
    type = type || 'error';
    var alert = document.createElement('div');
    alert.className = 'alert alert-' + type;
    alert.textContent = message;
    
    var container = document.querySelector('.container');
    if (container) {
        var firstAlert = container.querySelector('.alert');
        if (firstAlert && firstAlert !== alert) {
            container.insertBefore(alert, firstAlert.nextSibling);
        } else {
            container.insertBefore(alert, container.firstChild);
        }
        setTimeout(function() { alert.remove(); }, 5000);
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

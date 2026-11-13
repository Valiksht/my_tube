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
        // Защита от повторного подключения
        if (btn.dataset.handlerAttached === 'true') return;
        btn.dataset.handlerAttached = 'true';
        
        btn.addEventListener('click', function() {
            // Защита от повторных быстрых кликов
            if (this.dataset.busy === 'true') return;
            this.dataset.busy = 'true';
            
            // Запоминаем текущее состояние для восстановления при ошибке
            var wasActive = this.classList.contains('active');
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
                if (!response.ok) {
                    throw new Error('Like failed');
                }
                // Переключаем класс active только после успешного ответа
                this.classList.toggle('active');
                return fetch('/api/videos/' + videoId + '/likes/count');
            }.bind(this))
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
                // Восстанавливаем предыдущее состояние при ошибке
                if (wasActive) {
                    this.classList.add('active');
                } else {
                    this.classList.remove('active');
                }
                showAlert('Не удалось обработать лайк', 'error');
            })
            .finally(function() {
                this.dataset.busy = 'false';
            }.bind(this));
        });
    });
    
    // Subscribe кнопки
    document.querySelectorAll('.subscribe-btn').forEach(function(btn) {
        // Защита от повторного подключения
        if (btn.dataset.handlerAttached === 'true') return;
        btn.dataset.handlerAttached = 'true';
        
        btn.addEventListener('click', function() {
            // Защита от повторных быстрых кликов
            if (this.dataset.busy === 'true') return;
            this.dataset.busy = 'true';
            
            // Запоминаем текущее состояние для восстановления при ошибке
            var wasSubscribed = this.classList.contains('active');
            var wasText = this.textContent.trim();
            var channelId = this.dataset.channelId;
            
            fetch('/api/channels/' + channelId + '/subscriptions', {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'X-CSRF-Token': getCSRFToken()
                }
            })
            .then(function(response) {
                if (!response.ok) {
                    throw new Error('Subscribe failed');
                }
                // Переключаем класс active и текст только после успешного ответа
                this.classList.toggle('active');
                var isSubscribed = this.classList.contains('active');
                this.textContent = isSubscribed ? 'Отписаться' : 'Подписаться';
                
                var countEl = document.querySelector('.channel-subscribers');
                if (countEl) {
                    return fetch('/api/channels/' + channelId + '/subscriptions/count')
                        .then(function(r) { return r.json(); })
                        .then(function(data) {
                            countEl.textContent = data.subscriber_count + ' подписчиков';
                        });
                }
            }.bind(this))
            .catch(function(error) {
                console.error('Error:', error);
                // Восстанавливаем предыдущее состояние при ошибке
                if (wasSubscribed) {
                    this.classList.add('active');
                    this.textContent = 'Отписаться';
                } else {
                    this.classList.remove('active');
                    this.textContent = 'Подписаться';
                }
                showAlert('Не удалось обновить подписку', 'error');
            })
            .finally(function() {
                this.dataset.busy = 'false';
            }.bind(this));
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
    
    // Comment form
    var commentForm = document.getElementById('comment-form');
    if (commentForm) {
        // Защита от повторного подключения
        if (commentForm.dataset.handlerAttached !== 'true') {
            commentForm.dataset.handlerAttached = 'true';
            
            commentForm.addEventListener('submit', function(e) {
                e.preventDefault();
                
                var contentEl = document.getElementById('comment-content');
                var errorEl = document.getElementById('comment-form-error');
                var successEl = document.getElementById('comment-form-success');
                var content = contentEl.value.trim();
                
                if (!content) {
                    return;
                }
                
                var videoId = this.dataset.videoId;
                
                fetch('/api/videos/' + videoId + '/comments', {
                    method: 'POST',
                    credentials: 'include',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRF-Token': getCSRFToken()
                    },
                    body: JSON.stringify({ content: content })
                })
                .then(function(response) {
                    if (!response.ok) {
                        throw new Error('Comment failed');
                    }
                    return response.json();
                })
                .then(function(data) {
                    // Очистить поле
                    contentEl.value = '';
                    
                    // Показать сообщение об успехе
                    if (successEl) {
                        successEl.textContent = 'Комментарий добавлен';
                        successEl.style.display = 'block';
                        setTimeout(function() { successEl.style.display = 'none'; }, 3000);
                    }
                    
                    // Перезагрузить комментарии
                    return fetch('/api/videos/' + videoId + '/comments?skip=0&limit=50');
                })
                .then(function(response) { return response.json(); })
                .then(function(comments) {
                    // Перерисовать комментарии
                    renderComments(comments);
                })
                .catch(function(error) {
                    console.error('Error:', error);
                    if (errorEl) {
                        errorEl.textContent = 'Не удалось отправить комментарий';
                        errorEl.style.display = 'block';
                        setTimeout(function() { errorEl.style.display = 'none'; }, 5000);
                    }
                });
            });
        }
    }
}

// Рендер комментариев
function renderComments(comments) {
    var section = document.querySelector('.comments-section');
    if (!section) return;
    
    var list = section.querySelector('.comment-list');
    if (!list) {
        list = document.createElement('div');
        list.className = 'comment-list';
        
        // Вставить после формы комментария или после h2
        var form = section.querySelector('#comment-form');
        var h2 = section.querySelector('h2');
        if (form) {
            section.insertBefore(list, form.nextSibling);
        } else if (h2) {
            section.insertBefore(list, h2.nextSibling);
        } else {
            section.appendChild(list);
        }
    }
    
    list.innerHTML = '';
    
    for (var i = 0; i < comments.length; i++) {
        var comment = comments[i];
        var div = document.createElement('div');
        div.className = 'comment';
        div.innerHTML = 
            '<div class="comment-header">' +
                '<span class="comment-author">' + escapeHtml(comment.user.username) + '</span>' +
                '<span class="comment-date">' + escapeHtml(comment.created_at) + '</span>' +
            '</div>' +
            '<p class="comment-content">' + escapeHtml(comment.content) + '</p>';
        list.appendChild(div);
    }
    
    // Обновить счётчик
    var heading = section.querySelector('h2');
    if (heading) {
        heading.textContent = 'Комментарии (' + comments.length + ')';
    }
}

// Экранирование HTML
function escapeHtml(text) {
    if (!text) return '';
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(text));
    return div.innerHTML;
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

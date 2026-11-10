"""Тесты для проверенного рефакторинга."""
import pytest


def test_session_module_syntax():
    """Проверяем синтаксис модуля session.py."""
    import ast
    with open('app/database/session.py', encoding='utf-8') as f:
        source = f.read()
    # Если код проходит через ast.parse — синтаксис корректен
    ast.parse(source)


def test_session_has_required_functions():
    """Проверяем наличие required functions."""
    from app.database import session
    
    assert hasattr(session, 'get_async_session')
    assert hasattr(session, 'get_async_engine')
    assert hasattr(session, '_get_db_url')


def test_session_singleton_pattern():
    """Проверяем паттерн singleton для engine."""
    # При повторных вызовах должен возвращаться тот же engine
    from app.database.session import get_async_engine
    
    engine1 = get_async_engine()
    engine2 = get_async_engine()
    
    assert engine1 is engine2, "Singleton pattern нарушен"


def test_health_endpoint_syntax():
    """Проверяем синтаксис /health endpoint."""
    import ast
    with open('app/main.py', encoding='utf-8') as f:
        source = f.read()
    ast.parse(source)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
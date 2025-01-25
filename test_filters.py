import sqlite3
import pytest
from main import (
    init_db, add_filter_to_db, list_filters_for_user,
    remove_filter_from_db, clear_filters_for_user
)

@pytest.fixture
def test_db():
    """Создает временную БД в памяти для тестирования."""
    conn = sqlite3.connect(":memory:")
    conn.execute("""
        CREATE TABLE user_filters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            location TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    yield conn
    conn.close()

def test_add_filter(test_db):
    user_id = 123
    category = "Cars"
    location = "New York"

    # Добавляем фильтр (ожидаем True, т.к. фильтр новый).
    result = add_filter_to_db(test_db, user_id, category, location)
    assert result is True

    # Повторная попытка (ожидаем False, т.к. дубль).
    result = add_filter_to_db(test_db, user_id, category, location)
    assert result is False

def test_list_filters(test_db):
    user_id = 123
    category = "Cars"
    location = "New York"

    add_filter_to_db(test_db, user_id, category, location)
    filters = list_filters_for_user(test_db, user_id)

    assert len(filters) == 1
    assert filters[0][0] == category
    assert filters[0][1] == location

def test_remove_filter(test_db):
    user_id = 123
    category = "Cars"
    location = "New York"

    add_filter_to_db(test_db, user_id, category, location)
    remove_filter_from_db(test_db, user_id, category, location)
    filters = list_filters_for_user(test_db, user_id)

    assert len(filters) == 0

def test_clear_filters(test_db):
    user_id = 123
    add_filter_to_db(test_db, user_id, "Cars", "NY")
    add_filter_to_db(test_db, user_id, "Bikes", "LA")

    clear_filters_for_user(test_db, user_id)
    filters = list_filters_for_user(test_db, user_id)

    assert len(filters) == 0

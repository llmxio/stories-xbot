"""
Simple test to verify bot components are properly imported and structured.
"""

from bot.filters import ChatType, HasUsernames
from bot.handlers import get_routers
from bot.middlewares import LongOperation


def test_filters():
    """Test filter instantiation."""
    # Test ChatType filter
    chat_filter = ChatType("private")
    assert chat_filter.chat_type == "private"

    chat_filter_list = ChatType(["group", "supergroup"])
    assert chat_filter_list.chat_type == ["group", "supergroup"]

    # Test HasUsernames filter
    username_filter = HasUsernames()
    assert username_filter is not None

    print("✓ Filters test passed")


def test_middlewares():
    """Test middleware instantiation."""
    middleware = LongOperation()
    assert middleware is not None
    print("✓ Middlewares test passed")


def test_handlers():
    """Test handlers structure."""
    routers = get_routers()
    assert len(routers) == 3
    assert all(hasattr(router, "include_router") for router in routers)
    print("✓ Handlers test passed")


if __name__ == "__main__":
    test_filters()
    test_middlewares()
    test_handlers()
    print("🎉 All tests passed!")

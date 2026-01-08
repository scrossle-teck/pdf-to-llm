from src.main import greet


def test_greet_default():
    assert greet() == "Hello, Template!"


def test_greet_custom():
    assert greet("World") == "Hello, World!"
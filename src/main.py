def greet(name: str = "Template") -> str:
    return f"Hello, {name}!"


def main() -> None:
    message = greet()
    print(message)


if __name__ == "__main__":
    main()

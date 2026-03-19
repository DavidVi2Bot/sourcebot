# src/sourcebot/__main__.py
import sys
from sourcebot.cli.main import app
from sourcebot.logging import setup_logging


def main():
    """Entry point for console script"""
    setup_logging()
    try:
        app()
    except KeyboardInterrupt:
        print("\n👋 Bye")
        sys.exit(0)

if __name__ == "__main__":
    main()
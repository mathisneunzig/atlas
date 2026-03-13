from __future__ import annotations

from assistant import HomeLabAssistant
from config import Settings


def main() -> None:
    settings = Settings.from_env()
    assistant = HomeLabAssistant(settings)
    assistant.run_forever()


if __name__ == "__main__":
    main()
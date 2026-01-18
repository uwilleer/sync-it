# ruff: noqa: T201 BLE001 E402

# isort: off
from dotenv import load_dotenv

load_dotenv("../../../../infra/.env", verbose=True)
# isort: on

import asyncio
from pathlib import Path
import sys

from core.settings import service_config
from services.gpt import get_gpt_response


# Добавляем путь к src для импорта модулей
sys.path.insert(0, str(Path(__file__).parent.parent))


async def main() -> None:
    """Тестирует подключение к GPT сервису через Groq API."""
    print("🔍 Testing GPT Service (Groq API)...")
    print(f"Model: {service_config.groq_model}")
    print()

    # Тест 1: Простой запрос
    print("Test 1: Simple prompt")
    print("-" * 50)
    test_prompt = 'Say "OK"'
    print(f"Prompt: {test_prompt}")

    try:
        response = await get_gpt_response(test_prompt)
        if response:
            print(f"✅ Success! Response: {response}")
        else:
            print("❌ Error: No response received")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

    print()

    # Тест 2: Более сложный запрос
    print("Test 2: Complex prompt")
    print("-" * 50)
    test_prompt = "What is 2+2? Answer briefly."
    print(f"Prompt: {test_prompt}")

    try:
        response = await get_gpt_response(test_prompt)
        if response:
            print(f"✅ Success! Response: {response}")
        else:
            print("❌ Error: No response received")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

    print()
    print("✅ All tests passed!")


if __name__ == "__main__":
    asyncio.run(main())

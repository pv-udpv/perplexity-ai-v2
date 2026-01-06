#!/usr/bin/env python3
"""
Streaming response example
"""

import perplexity_ai as pplx


def main():
    client = pplx.Client()

    print("Потоковый ответ:")
    print("="*50)

    # Stream response word by word
    for chunk in client.ask(
        "Explain quantum entanglement in detail",
        mode="copilot",
        stream=True,
    ):
        # Print each chunk as it arrives
        print(chunk.text, end="", flush=True)

    print("\n" + "="*50)
    print("Готово!")


if __name__ == "__main__":
    main()

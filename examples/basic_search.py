#!/usr/bin/env python3
"""
Basic search example
"""

import perplexity_ai as pplx


def main():
    # Create client (no auth needed for basic search)
    client = pplx.Client()

    # Simple query
    print("Простой запрос:")
    response = client.ask(
        "Кто сейчас президент России?",
        mode="concise",
        sources=["web"],
    )
    print(f"\n{response.text}\n")
    print(f"Thread UUID: {response.thread_uuid}")
    print(f"Model: {response.model}")

    # Follow-up question
    print("\n" + "="*50)
    print("Дополнительный вопрос:")
    followup = client.ask(
        "Расскажи подробнее",
        follow_up=response,
    )
    print(f"\n{followup.text}\n")

    # Different sources
    print("\n" + "="*50)
    print("Научный поиск:")
    scholarly = client.ask(
        "Latest quantum computing breakthroughs",
        mode="copilot",
        sources=["scholar"],
    )
    print(f"\n{scholarly.text}\n")


if __name__ == "__main__":
    main()

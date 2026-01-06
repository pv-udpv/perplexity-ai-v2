#!/usr/bin/env python3
"""
Pro model usage example (requires authentication)
"""

import os
import perplexity_ai as pplx


def main():
    # Load credentials from environment
    session_token = os.getenv("PPLX_SESSION_TOKEN")
    cf_clearance = os.getenv("PPLX_CF_CLEARANCE")

    if not session_token:
        print("Error: PPLX_SESSION_TOKEN environment variable not set")
        print("\nGet your tokens from browser cookies:")
        print("1. Open perplexity.ai and login")
        print("2. Open DevTools (F12)")
        print("3. Go to Application > Cookies")
        print("4. Copy __Secure-next-auth.session-token and cf_clearance")
        print("\nSet environment variables:")
        print("export PPLX_SESSION_TOKEN='your-token'")
        print("export PPLX_CF_CLEARANCE='your-clearance'")
        return

    # Create auth
    auth = pplx.PerplexityAuth(
        session_token=session_token,
        cf_clearance=cf_clearance,
    )

    # Create client
    client = pplx.Client(auth=auth)

    # Use Pro model
    print("Using Claude Sonnet Pro model:")
    print("="*50)
    response = client.ask(
        "Provide a deep analysis of quantum computing's impact on cryptography",
        mode="research",
        model="claude37sonnetthinking",
    )
    print(f"\n{response.text}\n")

    # Try different Pro models
    print("\n" + "="*50)
    print("Using GPT-4o:")
    print("="*50)
    response = client.ask(
        "Explain the latest advances in fusion energy",
        mode="copilot",
        model="gpt-4o",
    )
    print(f"\n{response.text}\n")


if __name__ == "__main__":
    main()

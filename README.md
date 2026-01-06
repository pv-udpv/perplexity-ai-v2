# 🤖 Perplexity AI v2

> Comprehensive unofficial Perplexity AI API client with **full endpoint coverage**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![curl-cffi](https://img.shields.io/badge/http-curl--cffi-green.svg)](https://github.com/yifeikong/curl_cffi)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- 🔒 **Full API Coverage** - Все endpoints: search, threads, collections, account, pro features
- 🔥 **curl-cffi** - Обход Cloudflare protection с настоящим TLS fingerprinting
- 🌊 **SSE Streaming** - Real-time потоковые ответы
- 🧠 **Stealth Mode** - iOS Safari fingerprint, полная эмуляция браузера
- 📝 **Type-Safe** - Pydantic models для всех request/response
- ⚡ **Async Support** - Полная поддержка asyncio
- 🎯 **Pro Features** - Работа с Pro моделями, file uploads, research mode

## 📦 Installation

```bash
# Using uv (recommended)
uv pip install perplexity-ai-v2

# Using pip
pip install perplexity-ai-v2
```

## 🚀 Quick Start

### Basic Search

```python
import perplexity_ai as pplx

client = pplx.Client()

# Simple query
response = client.ask(
    "Кто сейчас президент России?",
    mode="concise",
    sources=["web"]
)
print(response.text)
print(f"Sources: {len(response.sources)}")
```

### Streaming Response

```python
for chunk in client.ask(
    "Explain quantum computing in simple terms",
    mode="copilot",
    stream=True
):
    print(chunk.text, end="", flush=True)
```

### Pro Model with Authentication

```python
from perplexity_ai.auth import PerplexityAuth

auth = PerplexityAuth.from_cookies({
    "__Secure-next-auth.session-token": "your-token-here",
    "cf_clearance": "your-cf-clearance"
})

client = pplx.Client(auth=auth)

response = client.ask(
    "Deep analysis of quantum entanglement",
    mode="research",
    model="claude37sonnetthinking"
)
```

### File Upload

```python
with open("document.pdf", "rb") as f:
    response = client.ask(
        "Summarize this document",
        files={"document.pdf": f.read()},
        mode="copilot"
    )
```

### Thread Management

```python
# List all threads
threads = client.threads.list()

# Get specific thread
thread = client.threads.get(thread_uuid)

# Follow-up query in thread
response = client.ask(
    "Tell me more about that",
    follow_up=previous_response
)

# Delete thread
client.threads.delete(thread_uuid)
```

## 📚 Documentation

- [🔥 API Endpoints](docs/api_endpoints.md) - Полный список endpoints
- [🔐 Authentication](docs/authentication.md) - Как получить и использовать токены
- [🧠 Stealth Techniques](docs/stealth_techniques.md) - Как обходятся защиты
- [📊 Examples](examples/) - Примеры использования

## 🔧 Architecture

```
src/perplexity_ai/
├── client.py           # Main sync client
├── async_client.py     # Async client
├── session.py          # Session with curl-cffi
├── auth.py             # Authentication
├── endpoints/
│   ├── ask.py          # /perplexity_ask
│   ├── threads.py      # Thread management
│   ├── collections.py  # Collections/Spaces
│   ├── account.py      # Account endpoints
│   └── pro.py          # Pro features
├── models/
│   ├── request.py      # Request Pydantic models
│   ├── response.py     # Response models
│   └── sse.py          # SSE event models
├── stealth/
│   ├── headers.py      # Header generation
│   ├── fingerprint.py  # Device fingerprinting
│   └── cookies.py      # Cookie management
└── utils/
    ├── sse_parser.py   # SSE stream parser
    └── uuid_gen.py     # UUID generators
```

## 🎯 Supported Endpoints

### Core
- ✅ `/rest/sse/perplexity_ask` - Main search with SSE streaming
- ✅ `/threads` - Thread listing
- ✅ `/threads/{uuid}` - Thread get/update/delete
- ✅ `/collections` - Collections management
- ✅ `/collections/{uuid}` - Collection operations

### Account
- ✅ `/auth/signin` - Authentication
- ✅ `/auth/signout` - Logout
- ✅ `/user/profile` - User profile
- ✅ `/user/subscription` - Subscription status

### Pro Features
- ✅ Research mode
- ✅ File uploads (PDF, images)
- ✅ Canvas/Studio mode
- ✅ Image generation
- ✅ Multiple Pro models (Claude, GPT-4, o3-mini, r1)

## 🔒 Why curl-cffi?

Perplexity использует Cloudflare с HTTP-only cookies и TLS fingerprinting. Обычные HTTP клиенты (`requests`, `httpx`, `aiohttp`) **не работают**.

`curl-cffi` - это Python bindings к libcurl с поддержкой:
- ✅ HTTP/2 fingerprinting
- ✅ TLS fingerprinting (JA3)
- ✅ Browser impersonation
- ✅ Cloudflare bypass

## 🧠 Stealth Features

### iOS Safari Emulation
```python
User-Agent: Ask/2.250911.0/16709 (iOS; iPhone; 18.7.0)
X-Client-Name: Perplexity-iOS
X-Device-ID: ios:{generated-uuid}
```

### Automatic Cookie Management
- NextAuth session tokens
- Cloudflare clearance
- Session persistence
- Auto-refresh on expiry

### SSE Stream Handling
- Proper event-stream parsing
- Reconnection support
- Cursor-based pagination
- Progress tracking

## 📊 Development

```bash
# Clone repo
git clone https://github.com/pv-udpv/perplexity-ai-v2.git
cd perplexity-ai-v2

# Create venv with uv
uv venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy src

# Linting
ruff check src
```

## 📝 License

MIT License - see [LICENSE](LICENSE) for details

## ⚠️ Disclaimer

Этот проект является **неофициальным** и не аффилирован с Perplexity AI. Используйте на свой риск.

## 🚀 Inspiration

Основано на исследовании [helallao/perplexity-ai](https://github.com/helallao/perplexity-ai) с полным покрытием API.

## 💬 Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

---

Made with ❤️ by [@pv-udpv](https://github.com/pv-udpv)

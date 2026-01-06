# 📚 Examples

Примеры использования Perplexity AI v2 client.

## Basic Usage

### 🔍 Simple Search

```bash
python examples/basic_search.py
```

Показывает:
- Простой запрос
- Follow-up вопросы
- Разные source types

### 🌊 Streaming

```bash
python examples/streaming.py
```

Потоковый ответ word-by-word.

### 🔒 Pro Models

```bash
# Set your credentials
export PPLX_SESSION_TOKEN="your-session-token"
export PPLX_CF_CLEARANCE="your-cf-clearance"

python examples/pro_model.py
```

Использование Pro моделей:
- Claude 3.7 Sonnet Thinking
- GPT-4o
- o3-mini
- r1

## Getting Credentials

1. Откройте [perplexity.ai](https://www.perplexity.ai) и войдите
2. Откройте DevTools (`F12` или `Ctrl+Shift+I`)
3. Перейдите в `Application` > `Cookies` > `https://www.perplexity.ai`
4. Скопируйте:
   - `__Secure-next-auth.session-token`
   - `cf_clearance`

### Using .env file

Create `.env` file:

```env
PPLX_SESSION_TOKEN=your-session-token-here
PPLX_CF_CLEARANCE=your-cf-clearance-here
```

Load in code:

```python
import os
from dotenv import load_dotenv
import perplexity_ai as pplx

load_dotenv()

auth = pplx.PerplexityAuth(
    session_token=os.getenv("PPLX_SESSION_TOKEN"),
    cf_clearance=os.getenv("PPLX_CF_CLEARANCE"),
)

client = pplx.Client(auth=auth)
```

## More Examples Coming Soon

- 📎 Thread management
- 📁 File uploads
- 📚 Collections/Spaces
- 🧑‍💼 Account management

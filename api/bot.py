```python
from fastapi import FastAPI, Request
from urllib.parse import urlencode
import requests
import time
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

app = FastAPI()


def make_google_ai_url(query: str) -> str:
    params = {
        "q": query,
        "sourceid": "chrome",
        "ie": "UTF-8",
        "amc": "1",
        "udm": "50",
        "aep": "42",
        "cud": "0",
        "qsubts": str(int(time.time() * 1000)),
        "source": "chrome.crn.rb",
    }

    return "https://www.google.com/search?" + urlencode(params)


@app.post("/api/bot")
async def telegram_webhook(request: Request):
    data = await request.json()

    inline_query = data.get("inline_query")

    if inline_query:
        query = inline_query["query"]
        inline_query_id = inline_query["id"]

        url = make_google_ai_url(query)

        results = [
            {
                "type": "article",
                "id": "1",
                "title": f"Google AI: {query}",
                "description": "Send Google AI search link",
                "input_message_content": {
                    "message_text": url
                }
            }
        ]

        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/answerInlineQuery",
            json={
                "inline_query_id": inline_query_id,
                "results": results,
                "cache_time": 1,
            },
        )

    return {"ok": True}
```

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

    # =========================
    # /start command
    # =========================

    message = data.get("message")

    if message:
        text = message.get("text", "")

        if text == "/start":
            chat_id = message["chat"]["id"]

            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": (
                        "Привет.\n\n"
                        "Этот бот создает Google AI search ссылки.\n\n"
                        "Использование:\n"
                        "@твойбот любой вопрос\n\n"
                        "Пример:\n"
                        "@твойбот почему небо голубое?"
                    ),
                },
            )

    # =========================
    # Inline mode
    # =========================

    inline_query = data.get("inline_query")

    if inline_query:
        query = inline_query["query"]
        inline_query_id = inline_query["id"]

        url = make_google_ai_url(query)

        markdown_link = f"[{query}]({url})"

        results = [
            {
                "type": "article",
                "id": "1",
                "title": query,
                "description": "Google AI Search",
                "input_message_content": {
                    "message_text": markdown_link,
                    "parse_mode": "Markdown"
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
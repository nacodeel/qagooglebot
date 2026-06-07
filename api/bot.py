from fastapi import FastAPI, Request
from urllib.parse import urlencode
import requests
import time
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

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


def ask_gemini(query: str) -> str:
    response = requests.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemma-4-31b-it:generateContent",
        params={
            "key": GEMINI_API_KEY
        },
        json={
            "contents": [
                {
                    "parts": [
                        {
                            "text": query
                        }
                    ]
                }
            ],
            "tools": [
                {
                    "google_search": {}
                }
            ]
        },
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        return "Не удалось получить ответ."


@app.post("/api/bot")
async def telegram_webhook(request: Request):
    data = await request.json()

    # =========================
    # /start
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
                        "Этот бот отвечает через Gemini AI "
                        "с поиском в интернете.\n\n"
                        "Использование:\n"
                        "@qagooglebot любой вопрос\n\n"
                        "Пример:\n"
                        "@qagooglebot почему небо голубое?"
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

        ai_answer = ask_gemini(query)

        url = make_google_ai_url(query)

        message_text = (
            f"{ai_answer}\n\n"
            f"🔎 Google AI Search:\n"
            f"[{query}]({url})"
        )

        results = [
            {
                "type": "article",
                "id": "1",
                "title": query,
                "description": ai_answer[:100],
                "input_message_content": {
                    "message_text": message_text,
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
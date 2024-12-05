import httpx
from fastapi import HTTPException
from asyncio import to_thread
from openai import OpenAI, OpenAIError, RateLimitError
from .logger import log_message
from ..config import settings

client_openai = OpenAI(api_key=settings.OPENAI_API_KEY)
http_client = httpx.AsyncClient()

async def fetch_data(url: str, params: dict = None):
    try:
        response = await http_client.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as exc:
        handle_http_error(exc)
    except Exception as exc:
        handle_generic_error(exc)


def handle_http_error(exc: httpx.HTTPStatusError):
    log_message(f"HTTP error occurred: {exc}")
    raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


def handle_generic_error(exc: Exception):
    log_message(f"An unexpected error occurred: {exc}")
    raise HTTPException(status_code=500, detail=str(exc))


async def get_openai_response(prompt: str, max_tokens: int, temperature: float):
    retry_count = 0
    max_retries = 3
    while retry_count < max_retries:
        try:
            response = await to_thread(
                client_openai.chat.completions.create,
                model=settings.GPT_MODEL,
                messages=[
                    {"role": "system", "content": "You are a professional sports analyst."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )

            response_message = response.choices[0].message.content.strip()
            return response_message
        except RateLimitError:
            retry_count += 1
            wait_time = 2 ** retry_count
            time.sleep(wait_time)
        except OpenAIError as exc:
            handle_http_error(exc)
        except Exception as exc:
            handle_generic_error(exc)


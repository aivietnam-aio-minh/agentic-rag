import os
import time

import anthropic
import openai
from google import genai
from google.genai import errors as genai_errors
from google.genai import types as genai_types

from app.llm.prompts import RAG_SYSTEM_PROMPT
from dotenv import load_dotenv

load_dotenv()
GEMINI_MODEL_NAME = "gemini-2.5-flash"
ANTHROPIC_MODEL_NAME = "claude-sonnet-4-6"
OPENAI_MODEL_NAME = "gpt-4o-mini"
TEMPERATURE = 0.2

MAX_RETRIES = 3
RETRY_DELAYS_SECONDS = [15, 30, 45]
LLM_API_ERRORS = (
    anthropic.RateLimitError,
    anthropic.APIConnectionError,
    anthropic.APIStatusError,
    genai_errors.APIError,
    openai.RateLimitError,
    openai.APIConnectionError,
    openai.APIStatusError,
)


def _generate_gemini(system_prompt: str, question: str) -> str:
    """Gọi Gemini qua google-genai, đọc GEMINI_API_KEY từ env."""
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    response = client.models.generate_content(
        model=GEMINI_MODEL_NAME,
        contents=question,
        config=genai_types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=TEMPERATURE,
        ),
    )
    return response.text or ""


def _generate_anthropic(system_prompt: str, question: str) -> str:
    """Gọi Claude qua SDK anthropic, đọc ANTHROPIC_API_KEY từ env."""
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    response = client.messages.create(
        model=ANTHROPIC_MODEL_NAME,
        max_tokens=1024,
        temperature=TEMPERATURE,
        system=system_prompt,
        messages=[{"role": "user", "content": question}],
    )
    return next((block.text for block in response.content if block.type == "text"), "")


def _generate_openai(system_prompt: str, question: str) -> str:
    """Gọi OpenAI qua SDK openai, đọc OPENAI_API_KEY từ env."""
    from openai import OpenAI

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model=OPENAI_MODEL_NAME,
        temperature=TEMPERATURE,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
    )
    return response.choices[0].message.content or ""


def _is_rate_limit_error(error: Exception) -> bool:
    """Rate limit (429) là lỗi tạm thời đáng retry; các lỗi API khác thì không."""
    if isinstance(error, (anthropic.RateLimitError, openai.RateLimitError)):
        return True
    return isinstance(error, genai_errors.APIError) and error.code == 429


def generate_answer(context: str, question: str) -> str:
    """Sinh câu trả lời RAG; provider (gemini/anthropic) chọn qua env LLM_PROVIDER, mặc định gemini.

    Lỗi rate limit (429) được retry tối đa MAX_RETRIES lần, chờ tăng dần theo
    RETRY_DELAYS_SECONDS giữa các lần thử. Hết lượt retry, hoặc gặp lỗi API khác
    không phải rate limit, exception được raise lại cho tầng gọi — không trả về
    chuỗi mô tả lỗi để tránh bị nhầm thành câu trả lời hợp lệ (ví dụ khi eval).
    """
    provider = os.environ.get("LLM_PROVIDER", "gemini")
    system_prompt = RAG_SYSTEM_PROMPT.format(context=context)

    for attempt in range(MAX_RETRIES + 1):
        try:
            if provider == "anthropic":
                return _generate_anthropic(system_prompt, question)
            if provider == "openai":
                return _generate_openai(system_prompt, question)
            return _generate_gemini(system_prompt, question)
        except LLM_API_ERRORS as e:
            if not _is_rate_limit_error(e) or attempt == MAX_RETRIES:
                raise
            time.sleep(RETRY_DELAYS_SECONDS[attempt])


def call_llm_with_tools(messages: list[dict], tools: list[dict]) -> object:
    """Gọi OpenAI chat.completions với tool-use, trả message thô (.content, .tool_calls) cho agent tự đọc.

    Chỉ hỗ trợ provider "openai" ở bước này. Retry 429 giống generate_answer();
    lỗi không retry được thì raise để agent/loop.py tự dừng vòng lặp, KHÔNG nuốt
    lỗi thành chuỗi giả (bài học từ bug "nuốt lỗi thành answer giả").
    """
    from openai import OpenAI

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    for attempt in range(MAX_RETRIES + 1):
        try:
            response = client.chat.completions.create(
                model=OPENAI_MODEL_NAME,
                temperature=TEMPERATURE,
                messages=messages,
                tools=tools,
            )
            return response.choices[0].message
        except LLM_API_ERRORS as e:
            if not _is_rate_limit_error(e) or attempt == MAX_RETRIES:
                raise
            time.sleep(RETRY_DELAYS_SECONDS[attempt])

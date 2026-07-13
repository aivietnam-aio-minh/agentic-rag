import os

import anthropic
from google import genai
from google.genai import errors as genai_errors
from google.genai import types as genai_types

from app.llm.prompts import RAG_SYSTEM_PROMPT
from dotenv import load_dotenv

load_dotenv()  
GEMINI_MODEL_NAME = "gemini-2.5-flash"
ANTHROPIC_MODEL_NAME = "claude-sonnet-4-6"
TEMPERATURE = 0.2


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


def generate_answer(context: str, question: str) -> str:
    """Sinh câu trả lời RAG; provider (gemini/anthropic) chọn qua env LLM_PROVIDER, mặc định gemini."""
    provider = os.environ.get("LLM_PROVIDER", "gemini")
    system_prompt = RAG_SYSTEM_PROMPT.format(context=context)

    try:
        if provider == "anthropic":
            return _generate_anthropic(system_prompt, question)
        return _generate_gemini(system_prompt, question)
    except anthropic.RateLimitError:
        return "Hệ thống đang quá tải (rate limit), vui lòng thử lại sau ít phút."
    except anthropic.APIConnectionError:
        return "Không thể kết nối tới dịch vụ LLM Anthropic, vui lòng kiểm tra kết nối mạng."
    except anthropic.APIStatusError as e:
        return f"Dịch vụ LLM Anthropic trả về lỗi ({e.status_code}), vui lòng thử lại sau."
    except genai_errors.APIError as e:
        return f"Dịch vụ LLM Gemini trả về lỗi ({e.code}), vui lòng thử lại sau."

import json

from app.agent.tools import calculator, search_docs
from app.llm.client import call_llm_with_tools
from app.retrieval.vector_store import VectorStore

MAX_STEPS = 6  # SRS NFR-05: agent phải LUÔN dừng
TRACE_OUTPUT_LIMIT = 300  # cắt ngắn output trong trace cho dễ đọc

TOOLS_SPEC: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "search_docs",
            "description": (
                "Tra cứu nội dung trong bộ tài liệu PDF đã được index (tiếng Việt). "
                "Dùng tool này cho MỌI câu hỏi về nội dung tài liệu: khái niệm, định nghĩa, "
                "quy trình, con số, tên riêng, ai làm gì, nằm ở trang nào. "
                "Kết quả trả về là các đoạn văn bản kèm [tên file, số trang] để trích dẫn. "
                "Nếu chưa đủ thông tin, có thể gọi lại tool với truy vấn khác/cụ thể hơn."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "Truy vấn tìm kiếm bằng tiếng Việt, nên chứa từ khóa cụ thể "
                            "thay vì câu hỏi dài dòng. Ví dụ: 'cách chia nhỏ văn bản thành chunk'."
                        ),
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": (
                "Tính giá trị của một biểu thức số học. Dùng tool này khi cần cộng/trừ/nhân/chia, "
                "lũy thừa, căn bậc hai, tính phần trăm hoặc so sánh số liệu — KHÔNG tự nhẩm trong đầu "
                "vì dễ sai. Chỉ nhận biểu thức toán thuần túy, không nhận chữ hay đơn vị "
                "(phải đổi '15 triệu' thành '15000000' trước khi gọi)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": (
                            "Biểu thức toán học hợp lệ, chỉ gồm số và toán tử. "
                            "Ví dụ: '15000000 * 1.2', '(100 + 50) / 3', 'sqrt(16)'."
                        ),
                    }
                },
                "required": ["expression"],
            },
        },
    },
]


def _assistant_message_to_dict(message: object) -> dict:
    """Chuyển message object của SDK về dict đúng format OpenAI để append lại vào history."""
    return {
        "role": "assistant",
        "content": message.content,
        "tool_calls": [
            {
                "id": tool_call.id,
                "type": "function",
                "function": {
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments,
                },
            }
            for tool_call in message.tool_calls
        ],
    }


def _run_tool(name: str, arguments: dict, vector_store: VectorStore) -> str:
    """Gọi đúng tool theo tên, trả chuỗi kết quả (tool tự bắt lỗi bên trong, không raise)."""
    if name == "search_docs":
        return search_docs(arguments.get("query", ""), vector_store, top_k=5)
    if name == "calculator":
        return calculator(arguments.get("expression", ""))
    return f"Lỗi: tool {name!r} không tồn tại."


def run(question: str, vector_store: VectorStore) -> dict:
    """Chạy vòng lặp agent: LLM tự chọn tool, thực thi, lặp lại tối đa MAX_STEPS bước.

    Trả về {"answer": str, "trace": list[dict], "steps": int}. Vòng lặp luôn dừng:
    hoặc LLM trả lời không cần tool nữa, hoặc chạm MAX_STEPS (SRS NFR-05), hoặc
    lỗi API ở tầng request (đã bắt để không làm sập request).
    """
    messages: list[dict] = [{"role": "user", "content": question}]
    trace: list[dict] = []

    for step in range(1, MAX_STEPS + 1):
        # Ranh giới request-level: tool bên trong đã tự bắt lỗi và trả chuỗi, còn lỗi
        # gọi LLM (hết retry 429, API die...) thì dừng hẳn vòng lặp, không để crash.
        try:
            message = call_llm_with_tools(messages, TOOLS_SPEC)
        except Exception:  # noqa: BLE001 - không để lỗi API làm sập request (CLAUDE.md)
            return {"answer": "Xin lỗi, có lỗi khi xử lý câu hỏi.", "trace": trace, "steps": step}

        if not message.tool_calls:
            return {"answer": message.content, "trace": trace, "steps": step}

        messages.append(_assistant_message_to_dict(message))

        for tool_call in message.tool_calls:
            name = tool_call.function.name
            # LLM đôi khi sinh JSON hỏng — parse riêng để 1 tool_call lỗi không giết cả loop.
            try:
                arguments = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                arguments = {}
                tool_output = (
                    f"Lỗi: tham số gửi cho tool {name!r} không phải JSON hợp lệ "
                    f"({tool_call.function.arguments!r}). Hãy gọi lại với JSON đúng định dạng."
                )
            else:
                tool_output = _run_tool(name, arguments, vector_store)

            messages.append(
                {"role": "tool", "tool_call_id": tool_call.id, "content": tool_output}
            )
            trace.append(
                {
                    "step": step,
                    "tool": name,
                    "input": arguments,
                    "output": tool_output[:TRACE_OUTPUT_LIMIT],
                }
            )

    return {
        "answer": "Xin lỗi, câu hỏi này cần nhiều bước xử lý hơn khả năng hiện tại.",
        "trace": trace,
        "steps": MAX_STEPS,
    }

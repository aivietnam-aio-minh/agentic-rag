# Báo cáo eval RAGAS

## Điểm trung bình chung

| Chỉ số | Điểm trung bình | Số câu tính được |
|---|---|---|
| faithfulness | 0.832 | 64/64 |
| answer_relevancy | 0.611 | 64/64 |

## Điểm trung bình theo loại câu hỏi (`type`)

| type | faithfulness | answer_relevancy | số câu |
|---|---|---|---|
| simple | 0.907 | 0.742 | 46 |
| multi_hop | 0.900 | 0.532 | 5 |
| needs_calc | 0.667 | 0.523 | 3 |
| out_of_scope | 0.500 | 0.128 | 6 |
| ambiguous | 0.500 | 0.000 | 4 |

## Ghi chú so sánh: Baseline (vector_only) vs Hybrid + Rerank

- Điểm trung bình chung gần như không đổi (faithfulness 0.829→0.832,
  answer_relevancy 0.599→0.611), nhưng ẩn sau đó là biến động mạnh và
  trái chiều theo nhóm `type`:
  - Nhóm `simple` (46/64 câu, đa số) CẢI THIỆN rõ: faithfulness
    0.841→0.907, answer_relevancy 0.726→0.742.
  - Nhóm `out_of_scope`, `ambiguous`, `needs_calc` (18/64 câu) GIẢM
    faithfulness. Điều tra cho thấy 2 nguyên nhân khác nhau:
    (1) Faithfulness của câu trả lời từ chối ("Tài liệu không đề cập")
    phụ thuộc vào context retrieval đi kèm, không chỉ vào bản thân câu
    trả lời — cùng 1 answer có thể chấm faithfulness 0.0 hoặc 1.0 tùy
    context có "trông giống" chủ đề câu hỏi hay không. Đổi retrieval
    (baseline→hybrid) làm thay đổi context, nên điểm dao động dù answer
    logic không đổi.
    (2) PHÁT HIỆN THẬT: với câu hỏi mang tính liệt kê/tổng hợp cấu trúc
    toàn tài liệu (vd. "đề tài chính là gì", "Phần VI có bao nhiêu kỹ
    thuật"), rerank cross-encoder có xu hướng chọn nhầm các chunk nội
    dung chi tiết chung chung thay vì phần thực sự trả lời câu hỏi —
    dẫn tới từ chối sai (false "không đề cập"). Đây là giới hạn thiết
    kế đã biết, nằm ngoài phạm vi SRS (hệ thống định vị "tra cứu",
    không phải "tóm tắt/liệt kê cấu trúc"), không sửa trong giai đoạn
    này.
  - Mẫu 3 nhóm nhỏ (18/64 câu) khá nhỏ, một vài câu đổi kết quả có
    thể làm điểm trung bình nhóm dao động mạnh — cần thận trọng khi
    diễn giải, không kết luận "hybrid tệ hơn" chỉ từ đây.
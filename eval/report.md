# Báo cáo eval RAGAS

## Điểm trung bình chung

| Chỉ số | Điểm trung bình | Số câu tính được |
|---|---|---|
| faithfulness | 0.829 | 64/64 |
| answer_relevancy | 0.599 | 64/64 |

## Điểm trung bình theo loại câu hỏi (`type`)

| type | faithfulness | answer_relevancy | số câu |
|---|---|---|---|
| simple | 0.841 | 0.726 | 46 |
| multi_hop | 0.830 | 0.722 | 5 |
| needs_calc | 0.833 | 0.231 | 3 |
| out_of_scope | 0.786 | 0.100 | 6 |
| ambiguous | 0.750 | 0.000 | 4 |

## Ghi chú diễn giải số liệu

- Nhóm `out_of_scope` và `ambiguous` đều có answer_relevancy rất thấp
  (0.0–0.15) dù faithfulness cao (~0.75–1.0). Đây KHÔNG phải lỗi hệ
  thống: các câu này được thiết kế để hệ thống trả lời "tài liệu không
  đề cập" (đúng FR-04 — ưu tiên từ chối hơn bịa đặt). Answer_relevancy
  đo bằng cách sinh ngược câu hỏi từ answer rồi so cosine similarity;
  với answer là câu từ chối chung chung, không có nội dung riêng để
  đoán đúng câu hỏi gốc, nên điểm luôn thấp bất kể chất lượng từ chối
  tốt hay không. Với 2 nhóm này, chỉ số đáng tin để đánh giá là
  faithfulness, không phải answer_relevancy.

- 33/64 câu sinh bằng Gemini 2.5 Flash, 31/64 câu sinh bằng gpt-4o-mini
  (do Gemini free tier cạn quota 20 request/ngày giữa quá trình
  generate). Giám khảo chấm điểm: gpt-4o-mini (faithfulness,
  answer_relevancy) + FastEmbed multilingual-MiniLM (embedding, local).
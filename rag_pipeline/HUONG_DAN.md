# Pipeline RAG — Bước 2: Cơ sở tri thức & tìm kiếm ngữ nghĩa

## Cài đặt
```bash
pip install -r requirements.txt
```

## Bố trí thư mục
Đặt thư mục `rag_pipeline/` cạnh `Data_CTU_restructured/` (hoặc dùng `--data-dir`):
```
project/
├── Data_CTU_restructured/
└── rag_pipeline/        <- chạy lệnh từ đây, dùng --data-dir ../Data_CTU_restructured
```

## Chạy
```bash
# 1) Xem thử cách chia đoạn (chưa tốn thời gian embed) -> mở chunks_preview.jsonl kiểm tra
python build_index.py --data-dir ../Data_CTU_restructured --dry-run

# 2) Dựng cơ sở tri thức (lần đầu tải bge-m3 ~2GB)
python build_index.py --data-dir ../Data_CTU_restructured

# 3) Tìm thử
python search.py "học phí học kỳ 1 đóng khi nào?" -k 5
python search.py "ky tuc xa" --topic ktx
python search.py                      # chế độ hỏi-đáp tương tác
```
Máy yếu / không có GPU: dùng model nhẹ hơn
`--model intfloat/multilingual-e5-base` (hoặc `set CTU_EMBED_MODEL=...`).

## Các tệp
| Tệp | Vai trò |
|---|---|
| `config.py` | Đường dẫn, model, kích thước chunk, ngưỡng tìm kiếm |
| `chunker.py` | Chia Markdown theo heading; giữ nguyên bảng; gắn dòng ngữ cảnh `[Tên văn bản (số hiệu) › Điều]` |
| `faq_parser.py` | Đọc FAQ (nhãn Q/A, heading, hoặc bảng) — mỗi cặp = 1 chunk |
| `metadata.py` | Ghép file processed với `.meta.json` của file raw |
| `embedder.py` | bge-m3 / e5 (và `dummy` để test offline) |
| `build_index.py` | Dựng ChromaDB |
| `check_glued_words.py` | Quét chữ tiếng Việt bị dính ("biệtmột") trong các file sẽ được đưa vào chỉ mục |
| `search.py` | Tìm lai (ngữ nghĩa + BM25), lọc chủ đề, cờ hết hạn/cần kiểm tra lại, `format_context()` cho LLM |

## Quy ước phân loại file
| Vị trí / tên file | Được xử lý thế nào |
|---|---|
| `faq/faq_*.md`, `faq/FAQ-*.md` | FAQ: mỗi cặp Hỏi-Đáp = 1 chunk (nhận `### FAQ-xxx-001` + `**❓ Câu hỏi:**` / `**💬 Trả lời:**`) |
| `processed/<chủ đề>/FAQ_*.md` | FAQ (chủ đề = tên thư mục), định dạng `**1. Câu hỏi?**` + `Trả lời: ...` cũng được nhận |
| `processed/<chủ đề>/*.md` khác | Tài liệu thường, chia đoạn theo heading |
| `faq/` nhưng tên **không** bắt đầu bằng "faq" (vd `bao_cao_khao_sat.md`) | **Bỏ qua** (không đưa vào cơ sở tri thức) |

Chủ đề FAQ lấy từ tên file (`faq_hoc_phi.md` → `hoc_phi`). Nếu tên file không khớp tên thư mục
trong `processed/`, khai báo ánh xạ ở `FAQ_TOPIC_ALIASES` trong `config.py`.
Khi chạy, script kiểm tra số mục `### FAQ-xxx` với số cặp đọc được và cảnh báo nếu lệch.

## Ghép metadata (quan trọng)
Script ghép file trong `processed/` với `.meta.json` theo thứ tự:
1. `Data_CTU_restructured/processed_meta_map.json` (tùy chọn, ánh xạ thủ công):
   `{"processed/hoc_phi/abc.md": "QD_hoc_phi_2026.pdf"}`
2. Tên file trùng/gần trùng file raw
3. Số hiệu văn bản (`so_hieu`) xuất hiện ở đầu nội dung
4. Thư mục chỉ có 1 file raw + 1 file processed

Đọc phần **CẢNH BÁO** khi chạy `build_index.py` để biết file nào chưa có metadata.
Nên thêm front matter hoặc file ánh xạ cho các file đó.

## Sau khi chạy xong
Tích `[x]` bước 5 trong README ("Index vào vector database").
Bước tiếp theo: nối `KnowledgeBase.search()` + `format_context()` vào LLM để sinh câu trả lời.

# -*- coding: utf-8 -*-
"""
Tải hàng loạt TOÀN BỘ file nguồn gốc mà chatbot K52 Buddy đang dùng,
dựa theo danh sách ID trong field "list_files" của API cấu hình bot
(GET https://aibot.vnpttiengiang.vn/api/bots?id=...).

Endpoint tải file: GET /api/files/download/{file_id}
-> trả về file thật, kèm tên file gốc trong header Content-Disposition.

CÁCH DÙNG:
1. Lấy TOKEN mới nhất từ DevTools (Headers > Authorization: Bearer ...)
   vì token JWT có hạn dùng ngắn.
2. Dán token vào biến TOKEN bên dưới.
3. Chạy: python download_source_files.py
   -> Toàn bộ file sẽ được tải về thư mục OUTPUT_DIR, đặt đúng tên gốc.

LƯU Ý ĐẠO ĐỨC/PHÁP LÝ:
- Chỉ dùng để thu thập dữ liệu tham khảo phục vụ niên luận/đồ án học thuật.
- Có nghỉ (sleep) giữa các lần tải để tránh làm quá tải server.
- Nếu 1 vài file lỗi (403/404/token hết hạn), script sẽ báo rõ, không dừng
  toàn bộ tiến trình.
"""

import os
import re
import time
import requests

# ====== CẤU HÌNH - SỬA THEO THỰC TẾ ======

# Dán Bearer token MỚI NHẤT lấy từ DevTools > Network > Headers > Authorization
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMGNkZDFkNTktMTI1Yi00OTNlLTk3NDctYjJjMDlhYWY3ZmQ4IiwicGVybWlzc2lvbnMiOlsiRklMRV9NQU5BR0VSIiwiQk9UX1RFTVBMQVRFX01BTkFHRVIiLCJCT1RfTUFOQUdFUiJdLCJ0eXBlIjoiaW50ZWdyYXRpb24ifQ.Qr3PrU-QHHRZJKey_-t3wBltxiOoVsvIDyuvGGhmNws"

BASE_URL = "https://aibot.vnpttiengiang.vn/api/files/download/"

# Toàn bộ 127 ID lấy từ field "list_files" trong response GET /api/bots?id=...
FILE_IDS = [
    "eb45d858-372f-464f-89bd-1ea3f4b7a78b",
    "882b22fe-de43-4491-bd12-343fcf26d526",
    "9f70fc3d-b5d0-49d8-96a7-4208a5dc06ca",
    "ec792d6d-9d00-437f-b1e6-b4807cb94972",
    "95f3302b-1fa0-4824-aa48-30ddc8a2bcc3",
    "e1d53286-cfce-4e90-ba2c-83b4d9f44c4f",
    "6bd4a549-927e-4f34-8795-ff9b609a13f5",
    "604eb68b-4efd-471a-87ee-4c40a79cf08c",
    "c22abb3a-04fc-44ae-8440-23be65016160",
    "3f0eec45-ea29-4e52-a30b-de1cd8da3295",
    "f0b4da5b-f3b4-4eec-98f3-0c5e9748cb1e",
    "bd0c13bf-5e98-441d-90f6-f480e42b679d",
    "34cbe961-4dc0-41f2-ba41-f81681b54f30",
    "0cdf9c8a-1913-4475-b7de-d4ee5495f98a",
    "6103b770-4977-4ce8-81f7-04909515a710",
    "39571a25-c71e-40b8-8c1c-d058c99c51a3",
    "7cd99b74-2fef-4bd2-b551-8ef1950f6f97",
    "077fdb94-0e6e-40ad-b0b7-989a43fc4da3",
    "425cc74e-ab7f-4cb7-bbe3-ce690bbcb00f",
    "64b739ad-85d1-4801-aac1-e8a3584adea1",
    "7a4affd3-39c9-4cd9-a58c-7185825971e0",
    "780e553d-ca9c-464d-925b-e229bbf8f142",
    "7bc7c9e3-e3d3-40cb-a287-8cf30de9df9d",
    "66113676-589a-439c-812a-c06ebf0dece8",
    "ada8407c-6436-40e9-a275-7b10b80f4094",
    "02f1c493-19dd-4610-a969-cdae49f0b065",
    "ac9f2b53-0b1b-4785-980d-c33cef75f691",
    "76e06d1a-ac63-4ed7-96a8-f618e9cfb88b",
    "1fa87eb1-f227-406f-a4b2-615345c69953",
    "4855741e-8c6d-4ad0-a2dd-1de1e70cae2e",
    "dda9497b-3a68-44da-93f6-98318cebcb2d",
    "94e57a4f-0a16-4a40-b080-d166f4c04377",
    "99d976d4-a021-474b-97ef-83e3b6f719b2",
    "efe87a93-195f-4d6c-b9ed-0a437f3b881a",
    "b43025a9-2477-41e8-bb81-7508084e9a02",
    "8d9bfa07-511e-4447-a51d-915a1a964c42",
    "7fc92530-b847-4222-bc81-1e36052b73c8",
    "86102c10-3df2-41af-a86a-365ce5be0f09",
    "d0f6f31e-c47c-429e-90d5-60c312321015",
    "b2cb6988-a987-4585-8647-4c360a1451f5",
    "a740e434-f0ea-46a3-abc5-dc84de6b7008",
    "e1fcfcee-a629-4045-9329-af313461b22c",
    "3170b171-80aa-4247-b439-28a7e0035bef",
    "9b2c4bb7-358a-47b6-b673-4f2202415165",
    "bb4585aa-ecca-42eb-b671-543c8f40f39b",
    "f5cdd18e-4c45-4846-adbf-1e09054670ab",
    "ccd0ef94-a7ff-4aa7-830b-d915b13ee7e5",
    "b0321a2b-171d-4349-a9c0-525aab540a0e",
    "5e1b2d25-fb2c-4313-9bab-7595e20dedfa",
    "a9b89fbf-7028-444a-b37a-f532156ecf6c",
    "5a225079-36bf-4c03-9e85-6b0ac3f36148",
    "087c3b12-5ff1-49b7-8444-5b9d92cdb00b",
    "368e8e63-6e5c-48b3-b887-558c5d9c1966",
    "9d2a2cf9-0405-44ce-8ea3-4c23ef52014c",
    "348ff0bc-d2c1-4bf1-868a-0aa6b8b4d7df",
    "6e253ccc-d004-4137-b78d-8bfd8cb389e5",
    "9dc928cf-efd9-4820-a434-33023068e77e",
    "42e6f1a4-c7c7-4265-9e36-32b1c826f88a",
    "e72459c2-5635-40a9-a6b3-3298f1dd0abc",
    "3e177d80-d8a5-45db-bb23-628b96bba98a",
    "046e7c81-80a7-4cd8-9a3d-840ed4578257",
    "e47ab04c-282c-4f36-b072-9aa3111f0000",
    "38a3a102-9a09-4b5d-8d43-82402295bd05",
    "7ee61d88-dcd8-41a5-a5e1-2da2c134ac57",
    "6ca5387b-7628-4b1b-946c-18951ef50dda",
    "9714024d-ea62-42e0-8501-4fa3f98adbb2",
    "decdecf1-90af-488d-9b90-35208b81baab",
    "8ab13ae5-c76d-4029-b448-acaf995e9804",
    "d42033bb-a0ae-4701-9262-e0b03671323e",
    "0b085689-0417-4ec9-a51d-ca683e16b453",
    "0daa1436-5b2d-4551-87d1-a4dbde73b2be",
    "44d1aef4-0cc5-4308-939f-092798ce86fe",
    "097a290c-5f8a-4145-95bc-8997f84f477d",
    "6b5558ab-5c1a-4458-b53a-acf7439edbf2",
    "81f86d22-fb6d-4eb2-b554-297db1bc35de",
    "a66779a9-0b77-45ec-8a28-4e7724fc7346",
    "2907b471-f6c2-46f8-8cdc-93b9730d89f0",
    "4eed361e-cc5c-4561-a8fa-5a57536c8aaa",
    "ff07d28e-7705-4c3e-bc02-58cba903a0b5",
    "41867892-a04c-4807-b375-c9cfa73490b7",
    "cf1eb61b-5ec8-4f3c-8ec1-4b8bfe1cfff3",
    "e300f4da-a6a9-4f94-be8d-eb939ee35bdd",
    "dada490f-204c-443e-99c9-81a889b7ad54",
    "50610a8a-81b9-4884-af65-3e4cc122c7cb",
    "af83f395-addd-4c1e-99f3-60785cdb0f9a",
    "55a04564-3cd6-4143-b500-95808294df9f",
    "92e32825-39a2-4c52-af0a-b32a49f353e4",
    "f0659ccf-ea63-4f3d-a53d-68a36fcbbd2d",
    "81d72a6c-d05e-4a3e-8b34-57330a2dfe7d",
    "84cca84e-7e53-4880-ad1a-db8dd3bf189a",
    "41f712c2-5bb7-4847-8c00-049e55221daf",
    "ce6f9e87-52fc-47c2-bccc-6e8a0634dd76",
    "e4054760-b50b-4612-883a-a6c8026f42a0",
    "155a2579-9490-4334-8cf0-3103ea136f64",
    "d1c4d6bf-7432-49c9-b65e-a556f593c1c2",
    "d1f6f8f5-229c-4a8b-b8db-e5aeef6b0e6e",
    "e9a21e5f-aea4-44b1-a2ac-756418ccd8f0",
    "4d80f6dc-5aa1-4d63-95c7-ee8f6ea704c2",
    "32c83ba1-b8e6-44f4-989e-3064dd83265f",
    "7edfea58-ca00-4465-89e6-3cdbd212c995",
    "02a61464-4c70-42ab-936a-4312e26015a0",
    "e8d4d0f4-c088-4e41-9ef7-cc3cec8441fd",
    "d87798f0-4b87-4a62-889a-54b6e4667e67",
    "2ae5d476-f7f6-4d86-b141-a39ea17ddd7d",
    "1da9260e-e50c-4860-8735-ee7245ff5b15",
    "fa65935d-7772-4998-8562-96de0de6cdf2",
    "47b34e80-7fee-468e-a42f-e301b2cf8fea",
    "669ef825-5fa6-4ea7-bee2-b30cefe6f15c",
    "f0cc3179-22f2-4d0c-9c3a-3a6fac45290d",
    "dd04eb93-1a4c-4e61-a398-538883fab7ab",
    "0fcc35b1-ca97-4057-8659-f4bfac748300",
    "df96c47b-de41-4793-94bd-0dab5987d6bc",
    "6a062662-2667-473c-8978-572cbecdc37f",
    "effafc9c-70c1-4d43-82df-8c78d28facf2",
    "8a3c2255-552f-4e75-87fd-5367115314ec",
    "9d42e802-2561-4e32-bd73-cb0f43d49259",
    "44643ef4-7f58-46d0-8d73-26f23c9e5049",
    "631bbe14-4e90-417c-97b5-b173af33e1cc",
    "9da21fc5-265b-4d76-9760-6a3051f147c7",
    "f6ef6c6d-8d28-4a03-8b52-55c350f18119",
    "6ec686a9-391a-47b4-9e92-a5a3c4abd5a6",
    "2fab6ba2-45b2-436d-bff6-29f1bd19cd06",
    "84753fd2-178e-44f1-b2ad-a8f10845785b",
    "d2e26d0e-f342-428c-8523-89d687ec66e4",
    "95d093d0-62a7-45ae-91a5-c617caec82c5",
    "e6db393a-5c16-47ca-be7a-f5164687f115",
    "c3ccba2f-897f-48e1-8a42-29b3918b32cf",
    "36a1da21-8be5-45c7-9a3b-075ef84a032b",
    "aec76007-3da0-4aa0-be11-c33c142c92aa",
    "9f50e100-06f3-448b-9171-ea55a556dca9",
    "ef62b8fb-6dae-4028-8a28-3ad2a1d3989d",
    "7d8c9844-4aca-40f2-aa31-51325cb70850",
    "b401786b-9bfd-4f89-9eaf-d4534356d5de",
    "e5b3fbf6-7433-42e2-bd62-0de30b6f8080",
    "7c329240-6b29-431b-bc90-2675e56bcec4",
    "5495612e-bd18-4e9b-bda6-8c88767dbfa4",
    "ae2315a2-92f9-4dd7-b6a2-b9f553e6c506",
]

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloaded_files")
DELAY_SECONDS = 1.5  # nghỉ giữa mỗi lần tải, tránh làm quá tải server


def extract_filename(content_disposition: str, fallback: str) -> str:
    """Lấy tên file thật từ header Content-Disposition, có xử lý
    cả 2 dạng: filename="..." và filename*=UTF-8''... (đã encode)."""
    if not content_disposition:
        return fallback

    # Ưu tiên filename*=UTF-8''... (chuẩn, giữ đúng dấu tiếng Việt)
    match_utf8 = re.search(r"filename\*=UTF-8''([^;]+)", content_disposition)
    if match_utf8:
        from urllib.parse import unquote
        return unquote(match_utf8.group(1))

    # Fallback: filename="..."
    match_plain = re.search(r'filename="([^"]+)"', content_disposition)
    if match_plain:
        return match_plain.group(1)

    return fallback


def main():
    if TOKEN == "DAN_TOKEN_MOI_VAO_DAY":
        print("!! Bạn chưa dán TOKEN. Mở DevTools > Network > chọn 1 request bất kỳ")
        print("   tới aibot.vnpttiengiang.vn > Headers > copy giá trị sau 'Bearer '")
        print("   rồi dán vào biến TOKEN trong script.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/json, text/plain, */*",
    }

    success, failed = [], []

    for i, file_id in enumerate(FILE_IDS, 1):
        url = BASE_URL + file_id
        print(f"[{i}/{len(FILE_IDS)}] Đang tải {file_id} ...", end=" ")
        try:
            resp = requests.get(url, headers=headers, timeout=30)
            if resp.status_code == 200:
                fname = extract_filename(
                    resp.headers.get("Content-Disposition", ""),
                    fallback=f"{file_id}.bin",
                )
                # Làm sạch tên file (bỏ ký tự không hợp lệ trên Windows)
                fname = re.sub(r'[<>:"/\\|?*]', "_", fname)
                dest_path = os.path.join(OUTPUT_DIR, fname)

                with open(dest_path, "wb") as f:
                    f.write(resp.content)

                print(f"OK -> {fname}")
                success.append(fname)
            elif resp.status_code == 401:
                print("LỖI 401 - Token hết hạn hoặc không hợp lệ. DỪNG lại.")
                print("-> Lấy token mới từ DevTools rồi chạy lại.")
                break
            else:
                print(f"LỖI {resp.status_code}")
                failed.append((file_id, resp.status_code))
        except Exception as e:
            print(f"LỖI ngoại lệ: {e}")
            failed.append((file_id, str(e)))

        time.sleep(DELAY_SECONDS)

    print(f"\n=== KẾT QUẢ ===")
    print(f"Tải thành công: {len(success)}/{len(FILE_IDS)}")
    if failed:
        print(f"Thất bại: {len(failed)}")
        for fid, err in failed:
            print(f"  - {fid}: {err}")
    print(f"\nFile đã lưu tại: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

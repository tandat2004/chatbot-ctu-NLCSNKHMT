"""Nạp metadata từ raw/**/*.meta.json và ghép với file trong processed/."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from textutil import norm_key, parse_date

META_FIELDS = [
    "so_hieu", "tieu_de", "source_url", "cap_ban_hanh",
    "hieu_luc_tu", "hieu_luc_den", "hoc_ky_ap_dung", "kiem_tra_lai_vao",
]


def split_front_matter(text: str) -> tuple[dict[str, str], str]:
    """Tách YAML front matter đơn giản (key: value) nếu file processed có."""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        return {}, text
    meta: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip("\"'")
    return meta, text[m.end():]


def sanitize(meta: dict[str, Any]) -> dict[str, Any]:
    """ChromaDB chỉ nhận str/int/float/bool: đổi None -> '' và list/dict -> JSON."""
    out: dict[str, Any] = {}
    for k, v in meta.items():
        if v is None:
            out[k] = ""
        elif isinstance(v, (str, int, float, bool)):
            out[k] = v
        else:
            out[k] = json.dumps(v, ensure_ascii=False)
    return out


class RawMetaIndex:
    """Chỉ mục các file *.meta.json trong raw/."""

    def __init__(self, raw_dir: Path):
        self.items: list[tuple[str, set[str], dict]] = []  # (thư mục, các key tên file, dữ liệu)
        self.warnings: list[str] = []
        raw_dir = Path(raw_dir)
        if not raw_dir.exists():
            self.warnings.append(f"Không thấy thư mục raw: {raw_dir}")
            return
        for p in sorted(raw_dir.rglob("*.meta.json")):
            try:
                data = json.loads(p.read_text(encoding="utf-8-sig"))
            except Exception as e:  # noqa: BLE001
                self.warnings.append(f"Không đọc được {p.name}: {e}")
                continue
            keys = {norm_key(p.name[: -len(".meta.json")])}
            if data.get("filename"):
                keys.add(norm_key(Path(data["filename"]).stem))
            self.items.append((p.parent.name, keys, data))

    @staticmethod
    def _match(keys: set[str], target: str) -> bool:
        for k in keys:
            if not k:
                continue
            if k == target:
                return True
            if min(len(k), len(target)) >= 6 and (k in target or target in k):
                return True
        return False

    def find(self, folder: str, stem: str, n_processed_in_folder: int = 1,
             body_head: str = "", override: str = "") -> tuple[dict, str]:
        """Tìm metadata cho file processed `stem` trong thư mục chủ đề `folder`.

        Thứ tự ưu tiên:
          0. `override`: tên file raw khai trong processed_meta_map.json
          1. tên file trùng/gần trùng (cùng thư mục, rồi mọi thư mục)
          2. số hiệu văn bản (`so_hieu`) xuất hiện ở đầu nội dung file processed
          3. thư mục có đúng 1 file raw và 1 file processed
        Trả về (metadata, trạng_thái): 'override' | 'matched' | 'so_hieu' | 'topic-single' | 'none'.
        """
        if override:
            target = norm_key(Path(override).name.replace(".meta.json", "").rsplit(".", 1)[0]
                              if "." in Path(override).name else override)
            for _, keys, data in self.items:
                if self._match(keys, target):
                    return data, "override"
        target = norm_key(stem)
        for same_folder in (True, False):
            for f, keys, data in self.items:
                if same_folder and f != folder:
                    continue
                if self._match(keys, target):
                    return data, "matched"
        head = norm_key(body_head)
        for _, _, data in self.items:
            sh = norm_key(str(data.get("so_hieu") or ""))
            if len(sh) >= 6 and sh in head:
                return data, "so_hieu"
        in_folder = [d for f, _, d in self.items if f == folder]
        if len(in_folder) == 1 and n_processed_in_folder == 1:
            return in_folder[0], "topic-single"
        return {}, "none"

    def earliest_review_date(self, folder: str) -> str:
        """Ngày `kiem_tra_lai_vao` sớm nhất trong chủ đề (dùng cho chunk FAQ)."""
        dates = [
            (parse_date(d.get("kiem_tra_lai_vao")), d.get("kiem_tra_lai_vao"))
            for f, _, d in self.items if f == folder
        ]
        dates = [x for x in dates if x[0]]
        return min(dates)[1] if dates else ""

    def topic_hoc_ky(self, folder: str) -> str:
        vals = sorted({d.get("hoc_ky_ap_dung") for f, _, d in self.items
                       if f == folder and d.get("hoc_ky_ap_dung")})
        return " | ".join(vals)

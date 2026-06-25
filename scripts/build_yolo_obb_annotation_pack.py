from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

ORIGINAL_GT = ROOT / "local_data" / "ground_truth" / "rotation_ground_truth.json"
AUGMENTED_GT = ROOT / "local_data" / "ground_truth" / "rotation_ground_truth_augmented_90.json"
ORIGINAL_IMAGES = ROOT / "local_data" / "experiment_samples" / "all" / "png"
AUGMENTED_IMAGES = ROOT / "local_data" / "experiment_samples" / "augmented_90" / "png"
DEFAULT_OUTPUT = ROOT / "local_data" / "yolo_obb_annotation_pack"

FOCUS_SAMPLES = {
    "sample_009",
    "sample_010",
    "sample_042",
    "aug90_002_from_sample_010",
    "aug90_016_from_sample_042",
}


def load_json(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def find_image(image_dir: Path, sample: str) -> Path:
    matches = sorted(image_dir.glob(f"*{sample}.png"))
    if not matches:
        raise FileNotFoundError(f"No PNG found for sample {sample} in {image_dir}")
    if len(matches) > 1:
        raise ValueError(f"Multiple PNG files found for sample {sample}: {matches}")
    return matches[0]


def source_number(record: dict) -> int:
    source = record.get("source_sample") or record["sample"]
    try:
        return int(source.rsplit("_", 1)[1])
    except (IndexError, ValueError) as exc:
        raise ValueError(f"Cannot parse source sample number from {source}") from exc


def suggested_split(record: dict) -> str:
    sample = record["sample"]
    if sample in FOCUS_SAMPLES:
        return "test_focus"

    num = source_number(record)
    if num in {9, 10, 42}:
        return "test_focus"

    bucket = num % 10
    if bucket in {8, 9}:
        return "val"
    if bucket == 0:
        return "test_focus"
    return "train"


def image_path_for(record: dict, dataset: str) -> Path:
    if dataset == "original":
        return find_image(ORIGINAL_IMAGES, record["sample"])
    return find_image(AUGMENTED_IMAGES, record["sample"])


def build_records() -> list[dict]:
    records: list[dict] = []

    for dataset, gt_path in (
        ("original", ORIGINAL_GT),
        ("augmented_90", AUGMENTED_GT),
    ):
        for record in load_json(gt_path):
            image_path = image_path_for(record, dataset)
            records.append(
                {
                    "dataset": dataset,
                    "sample": record["sample"],
                    "source_sample": record.get("source_sample", record["sample"]),
                    "image_path": str(image_path.relative_to(ROOT)),
                    "title_block_position": record["title_block_position"],
                    "precise_title_block_position": record.get("precise_title_block_position", ""),
                    "rotation_degrees": record["rotation_degrees"],
                    "source_level": record.get("source_level", ""),
                    "suggested_split": suggested_split(record),
                    "annotation_status": "pending",
                    "label_class": "title_block",
                    "notes": "",
                }
            )

    return sorted(records, key=lambda r: (r["suggested_split"], r["dataset"], r["sample"]))


def write_csv(path: Path, records: list[dict]) -> None:
    fieldnames = [
        "dataset",
        "sample",
        "source_sample",
        "image_path",
        "title_block_position",
        "precise_title_block_position",
        "rotation_degrees",
        "source_level",
        "suggested_split",
        "annotation_status",
        "label_class",
        "notes",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def write_labeling_guide(path: Path) -> None:
    path.write_text(
        """# YOLO/OBB 标题栏标注准备包

## 目的

本目录用于准备本地 YOLO/OBB `title_block` 检测实验。图纸图片仍保留在 `local_data/experiment_samples/`，本包只保存清单和标注说明。

## 标注类别

```text
0 title_block
```

## 标注规则

- 只标注完整标题栏外框。
- 若标题栏与明细表相连，只框标题栏主体。
- 若标题栏在右下方，按真实标题栏外边界标注。
- 若图纸有多个类似表格，只标注符合标题栏字段结构的区域。
- 若标题栏被裁切，按可见区域估计最小旋转框，并在备注中写 `cropped`。

## OBB 标签格式

Ultralytics OBB 标签使用：

```text
class_index x1 y1 x2 y2 x3 y3 x4 y4
```

坐标为归一化图像坐标。正式训练前，先用 2 到 3 张样例做加载和可视化检查。

## 文件

- `annotation_manifest.csv`：人工标注工作清单。
- `annotation_manifest.json`：同内容 JSON 版本，便于脚本读取。
- `classes.txt`：类别名。
- `pack_summary.json`：样本数量和建议拆分统计。
""",
        encoding="utf-8",
    )


def summarize(records: list[dict]) -> dict:
    by_dataset: dict[str, int] = {}
    by_split: dict[str, int] = {}
    by_position: dict[str, int] = {}

    for record in records:
        by_dataset[record["dataset"]] = by_dataset.get(record["dataset"], 0) + 1
        by_split[record["suggested_split"]] = by_split.get(record["suggested_split"], 0) + 1
        by_position[record["title_block_position"]] = by_position.get(record["title_block_position"], 0) + 1

    return {
        "total": len(records),
        "by_dataset": by_dataset,
        "by_split": by_split,
        "by_title_block_position": by_position,
        "focus_samples": sorted(FOCUS_SAMPLES),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a local YOLO/OBB annotation pack.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    records = build_records()
    summary = summarize(records)

    write_csv(output_dir / "annotation_manifest.csv", records)
    (output_dir / "annotation_manifest.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_dir / "classes.txt").write_text("title_block\n", encoding="utf-8")
    (output_dir / "pack_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_labeling_guide(output_dir / "labeling_guide.md")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

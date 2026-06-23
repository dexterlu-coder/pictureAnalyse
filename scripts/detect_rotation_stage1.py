from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR = ROOT / "local_data" / "previews" / "rotation_check"
OUTPUT_DIR = ROOT / "outputs" / "rotation-detection" / "stage1"
DEBUG_DIR = OUTPUT_DIR / "debug"

ROTATION_BY_SIDE = {
    "bottom": 0,
    "left": 90,
    "top": 180,
    "right": 270,
}

CORRECTION_BY_SIDE = {
    "bottom": 0,
    "left": 270,
    "top": 180,
    "right": 90,
}

SIDE_LABEL_ZH = {
    "bottom": "下方或右下方",
    "left": "左侧",
    "top": "上方或左上方",
    "right": "右侧或右上方",
}


@dataclass
class SideScore:
    side: str
    score: float
    line_density: float
    intersection_density: float
    component_density: float
    bbox: list[int]


@dataclass
class DetectionResult:
    file: str
    title_block_side: str
    title_block_position: str
    clockwise_rotation_degrees: int
    correction_clockwise_degrees: int
    confidence: float
    needs_review: bool
    debug_image: str
    side_scores: list[dict]


def read_image(path: Path) -> np.ndarray:
    data = np.fromfile(str(path), dtype=np.uint8)
    image = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Cannot read image: {path}")
    return image


def write_image(path: Path, image: np.ndarray) -> None:
    ok, encoded = cv2.imencode(path.suffix, image)
    if not ok:
        raise ValueError(f"Cannot encode image: {path}")
    encoded.tofile(str(path))


def extract_line_masks(image: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    binary = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        41,
        9,
    )

    height, width = binary.shape
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (max(25, width // 45), 1))
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, max(25, height // 45)))

    horizontal = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel, iterations=1)
    vertical = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vertical_kernel, iterations=1)
    line_mask = cv2.bitwise_or(horizontal, vertical)
    return horizontal, vertical, line_mask


def side_regions(width: int, height: int) -> dict[str, tuple[int, int, int, int]]:
    band_x = int(width * 0.34)
    band_y = int(height * 0.34)
    return {
        "top": (0, 0, width, band_y),
        "bottom": (0, height - band_y, width, height),
        "left": (0, 0, band_x, height),
        "right": (width - band_x, 0, width, height),
    }


def score_region(
    side: str,
    bbox: tuple[int, int, int, int],
    horizontal: np.ndarray,
    vertical: np.ndarray,
    line_mask: np.ndarray,
) -> SideScore:
    x1, y1, x2, y2 = bbox
    area = max(1, (x2 - x1) * (y2 - y1))
    region_lines = line_mask[y1:y2, x1:x2]
    region_intersections = cv2.bitwise_and(horizontal[y1:y2, x1:x2], vertical[y1:y2, x1:x2])

    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(region_lines, 8)
    useful_components = 0
    for idx in range(1, num_labels):
        _, _, comp_w, comp_h, comp_area = stats[idx]
        if comp_area >= 60 and (comp_w >= 20 or comp_h >= 20):
            useful_components += 1

    line_density = float(np.count_nonzero(region_lines) / area)
    intersection_density = float(np.count_nonzero(region_intersections) / area)
    component_density = float(useful_components / max(1, area / 10000))

    # Title blocks are dense grids: many long lines plus many line crossings.
    score = (line_density * 100.0) + (intersection_density * 1500.0) + component_density
    return SideScore(
        side=side,
        score=round(score, 6),
        line_density=round(line_density, 6),
        intersection_density=round(intersection_density, 6),
        component_density=round(component_density, 6),
        bbox=[x1, y1, x2, y2],
    )


def confidence_from_scores(scores: list[SideScore], chosen: SideScore) -> float:
    ordered = sorted(scores, key=lambda item: item.score, reverse=True)
    if len(ordered) < 2 or chosen.score <= 0:
        return 0.0
    if chosen.side == ordered[0].side:
        margin = ordered[0].score - ordered[1].score
        confidence = margin / ordered[0].score
    else:
        confidence = 0.5 * (chosen.score / ordered[0].score)
    return round(max(0.0, min(1.0, confidence)), 4)


def choose_title_block_side(scores: list[SideScore]) -> SideScore:
    by_side = {score.side: score for score in scores}
    chosen = scores[0]

    # Assembly drawings can contain a large BOM near the top. If the top band
    # wins only because of that table while the right side has a dense grid-like
    # title block, prefer the right side.
    right = by_side.get("right")
    if (
        chosen.side == "top"
        and right is not None
        and right.score >= chosen.score * 0.60
        and right.component_density >= 0.25
    ):
        return right

    return chosen


def draw_debug(image: np.ndarray, scores: list[SideScore], chosen: SideScore) -> np.ndarray:
    debug = image.copy()
    for score in scores:
        x1, y1, x2, y2 = score.bbox
        color = (0, 180, 255)
        thickness = 3
        if score.side == chosen.side:
            color = (0, 255, 0)
            thickness = 6
        cv2.rectangle(debug, (x1, y1), (x2 - 1, y2 - 1), color, thickness)
        label = f"{score.side}: {score.score:.2f}"
        cv2.putText(debug, label, (x1 + 20, y1 + 45), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
    return debug


def detect_one(path: Path) -> DetectionResult:
    image = read_image(path)
    height, width = image.shape[:2]
    horizontal, vertical, line_mask = extract_line_masks(image)

    regions = side_regions(width, height)
    scores = [
        score_region(side, bbox, horizontal, vertical, line_mask)
        for side, bbox in regions.items()
    ]
    scores.sort(key=lambda item: item.score, reverse=True)
    chosen = choose_title_block_side(scores)
    confidence = confidence_from_scores(scores, chosen)
    needs_review = confidence < 0.18

    debug_path = DEBUG_DIR / f"{path.stem}_debug.png"
    write_image(debug_path, draw_debug(image, scores, chosen))

    return DetectionResult(
        file=path.name,
        title_block_side=chosen.side,
        title_block_position=SIDE_LABEL_ZH[chosen.side],
        clockwise_rotation_degrees=ROTATION_BY_SIDE[chosen.side],
        correction_clockwise_degrees=CORRECTION_BY_SIDE[chosen.side],
        confidence=confidence,
        needs_review=needs_review,
        debug_image=str(debug_path.relative_to(ROOT)),
        side_scores=[asdict(score) for score in scores],
    )


def write_results(results: list[DetectionResult]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DEBUG_DIR.mkdir(parents=True, exist_ok=True)

    json_path = OUTPUT_DIR / "results.json"
    json_path.write_text(
        json.dumps([asdict(result) for result in results], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    csv_path = OUTPUT_DIR / "results.csv"
    with csv_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "file",
                "title_block_side",
                "title_block_position",
                "clockwise_rotation_degrees",
                "correction_clockwise_degrees",
                "confidence",
                "needs_review",
                "debug_image",
            ],
        )
        writer.writeheader()
        for result in results:
            row = asdict(result)
            row.pop("side_scores")
            writer.writerow(row)


def main() -> None:
    if not INPUT_DIR.exists():
        raise SystemExit(f"Input directory does not exist: {INPUT_DIR}")

    DEBUG_DIR.mkdir(parents=True, exist_ok=True)
    images = sorted(INPUT_DIR.glob("*.png"))[:5]
    if not images:
        raise SystemExit(f"No PNG files found in: {INPUT_DIR}")

    results = [detect_one(path) for path in images]
    write_results(results)

    for result in results:
        print(
            f"{result.file}: {result.title_block_side} -> "
            f"{result.clockwise_rotation_degrees} deg, confidence={result.confidence}"
        )


if __name__ == "__main__":
    main()

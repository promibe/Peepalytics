import json
from difflib import SequenceMatcher
from typing import List


def normalize(val):
    """Convert to lowercase and remove commas, extra spaces."""
    if val is None:
        return ""
    return str(val).strip().lower().replace(",", "")


def fuzzy_match(a: str, b: str, threshold: float = 0.95) -> bool:
    return SequenceMatcher(None, normalize(a), normalize(b)).ratio() >= threshold


def extract_gt_fields(gt_path: str) -> List[str]:
    with open(gt_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    fields = []
    fields.append(data.get("masked_account_number", ""))
    fields.append(data.get("start_date", ""))
    fields.append(data.get("end_date", ""))

    for tx in data.get("transactions", []):
        fields.append(tx.get("date", ""))
        fields.append(tx.get("description", ""))
        for k in ["money_out", "money_in", "borrowings"]:
            val = tx.get(k)
            if val is not None:
                fields.append(f"{val:.2f}")
    return fields


def extract_predicted_text(pred_path: str) -> List[str]:
    with open(pred_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return [entry[1][0] for entry in data if entry and entry[1][0].strip()]


def evaluate(gt_path: str, pred_path: str):
    gt_fields = extract_gt_fields(gt_path)
    pred_fields = extract_predicted_text(pred_path)

    matched = 0
    matched_pred_indices = set()
    matched_gt_indices = set()

    for i, gt in enumerate(gt_fields):
        for j, pred in enumerate(pred_fields):
            if j in matched_pred_indices:
                continue
            if fuzzy_match(gt, pred):
                matched += 1
                matched_gt_indices.add(i)
                matched_pred_indices.add(j)
                break

    precision = matched / len(pred_fields) if pred_fields else 0.0
    recall = matched / len(gt_fields) if gt_fields else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0

    print("\nOCR Quality Evaluation")
    print("----------------------------")
    print(f"Matched fields   : {matched}")
    print(f"Predicted fields : {len(pred_fields)}")
    print(f"Ground truth     : {len(gt_fields)}")
    print(f"Precision        : {precision:.4f}")
    print(f"Recall           : {recall:.4f}")
    print(f"F1 Score         : {f1:.4f}")


# === Runing with file paths ===
evaluate(
    gt_path= r"C:\Users\DELL\OneDrive\Desktop\ZTH COHORT 4.0\Data Science\Peepalytics\data\json_file.json",
    pred_path=r"C:\Users\DELL\OneDrive\Desktop\ZTH COHORT 4.0\Data Science\Peepalytics\data\ocr\page_2_paddleocr.json"
)

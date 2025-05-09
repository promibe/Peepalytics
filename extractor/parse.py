#parse.py

import re
from datetime import datetime
import pandas as pd


def parser(page_ocr):
    """
    Parse OCR results to extract masked account number and transaction details.

    Args:
        page_ocr (list): OCR output for pages; index 0 for account page, index 1 for transactions.

    Returns:
        dict: {
            "masked_account_number": str,
            "start_date": str,
            "end_date": str,
            "transactions": list of dicts
        }
    """
    def try_parse_float(s):
        try:
            return float(s.replace(",", "").replace("$", ""))
        except:
            return None

    def merge_number_parts(texts):
        merged = []
        i = 0
        while i < len(texts):
            if (i + 1 < len(texts)
                    and re.match(r"^\d{1,3}$", texts[i])
                    and re.match(r"^\d{3}\.\d{2}$", texts[i+1])):
                merged.append(f"{texts[i]},{texts[i+1]}")
                i += 2
            else:
                merged.append(texts[i])
                i += 1
        return merged

    # Extract masked account number from first page
    account_number = None
    for box, (text, _) in page_ocr[0]:
        txt = text.lower()
        if "account number" in txt:
            account_number = ''.join(filter(str.isdigit, txt))
            break

    if account_number:
        masked_account = (
            '*' * (len(account_number) - 3) + account_number[-3:]
            if len(account_number) > 3
            else '*' * (len(account_number) - 1) + account_number[-1:]
        )
    else:
        masked_account = None

    # Collect words with positions from second page
    words = []
    for box, (text, _) in page_ocr[1]:
        y_center = (box[0][1] + box[2][1]) / 2
        words.append({"text": text.strip(), "y": y_center, "x": box[0][0]})

    words.sort(key=lambda w: w['y'])

    # Group words into rows
    grouped_rows = []
    current_row = []
    threshold = 10
    last_y = None
    for w in words:
        if last_y is None or abs(w['y'] - last_y) < threshold:
            current_row.append(w)
        else:
            grouped_rows.append(current_row)
            current_row = [w]
        last_y = w['y']
    if current_row:
        grouped_rows.append(current_row)

    # Parse transactions from rows
    transactions = []
    for row in grouped_rows:
        row = sorted(row, key=lambda w: w['x'])
        texts = merge_number_parts([w['text'] for w in row])

        # Skip non-transaction rows
        if any(t.lower() in ["close", "date", "total", "interest", "charges"] for t in texts):
            continue

        # Extract numeric fields
        nums = [try_parse_float(t) for t in texts if try_parse_float(t) is not None]
        if not nums:
            continue

        # Assign money_out, money_in, borrowings
        money_out = money_in = borrowings = None
        if len(nums) >= 3:
            money_out, money_in, borrowings = nums[-3:]
        elif len(nums) == 2:
            money_out, borrowings = nums
        else:
            borrowings = nums[0]

        # Parse date and description
        formatted_date = None
        try:
            dt = datetime.strptime(texts[0], "%d %b %Y")
            formatted_date = dt.strftime("%d-%m-%Y")
            description = " ".join(texts[1:-len(nums)] if len(nums) else texts[1:]).strip()
        except:
            description = " ".join(texts).strip()

        if formatted_date:
            transactions.append({
                "date": formatted_date,
                "description": description,
                "money_out": money_out,
                "money_in": money_in,
                "borrowings": borrowings
            })

    # Determine statement period
    dates = [datetime.strptime(t['date'], "%d-%m-%Y") for t in transactions]
    start_date = min(dates).strftime("%d-%m-%Y") if dates else None
    end_date = max(dates).strftime("%d-%m-%Y") if dates else None

    bank_statement = {
        "masked_account_number": masked_account,
        "start_date": start_date,
        "end_date": end_date,
        "transactions": transactions
    }

    return

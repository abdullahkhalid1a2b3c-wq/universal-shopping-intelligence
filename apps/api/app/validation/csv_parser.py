"""CSV parsing and validation utilities for size charts."""

import csv
import io
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel

from app.validation.size_chart import run_size_chart_sanity_checks, SanityCheckResult

# Expected CSV columns for size chart template
TEMPLATE_COLUMNS = [
    "size_label",
    "chest",
    "waist",
    "hip",
    "shoulder",
    "sleeve",
    "length",
    "inseam",
    "thigh",
]


class ParsedSizeChartCSV(BaseModel):
    """Result of parsing size chart CSV."""

    success: bool
    rows: List[Dict[str, Any]] = []
    columns_detected: List[str] = []
    errors: List[str] = []
    warnings: List[str] = []
    total_sizes: int = 0


def generate_size_chart_csv_template(category: Optional[str] = None) -> str:
    """Generate a clean CSV template string for retailer size chart entry."""
    output = io.StringIO()
    writer = csv.writer(output)

    if category in ("trouser", "jeans"):
        cols = ["size_label", "waist", "hip", "inseam", "thigh", "rise", "length"]
        sample_rows = [
            ["30", "76", "94", "78", "56", "25", "102"],
            ["32", "81", "99", "79", "58", "26", "103"],
            ["34", "86", "104", "80", "60", "27", "104"],
            ["36", "91", "109", "80", "62", "28", "105"],
        ]
    else:
        cols = ["size_label", "chest", "waist", "hip", "shoulder", "sleeve", "length"]
        sample_rows = [
            ["S", "96", "82", "98", "43", "61", "70"],
            ["M", "102", "88", "104", "45", "62", "72"],
            ["L", "108", "94", "110", "47", "63", "74"],
            ["XL", "114", "100", "116", "49", "64", "76"],
        ]

    writer.writerow(cols)
    for r in sample_rows:
        writer.writerow(r)
    return output.getvalue()


def parse_size_chart_csv(
    csv_content: str,
    unit_source: str = "cm",
    measured_as: str = "circumference",
    category: Optional[str] = None,
    gender_category: Optional[str] = None,
) -> ParsedSizeChartCSV:
    """Parse and validate CSV data for size charts.

    Supports:
    - Comma, semicolon, or tab delimited CSVs.
    - Automatic unit conversion from inches to cm when unit_source is 'in'.
    - Case-insensitive header matching.
    - Line-by-line validation and reporting of malformed lines.
    - Post-parse sanity checks.
    """
    errors: List[str] = []
    warnings: List[str] = []

    content = csv_content.strip()
    if not content:
        return ParsedSizeChartCSV(
            success=False,
            errors=["Uploaded CSV file is empty."],
        )

    # Sniff delimiter
    first_line = content.splitlines()[0]
    delimiter = ","
    if "\t" in first_line:
        delimiter = "\t"
    elif ";" in first_line and "," not in first_line:
        delimiter = ";"

    reader = csv.reader(io.StringIO(content), delimiter=delimiter)
    try:
        header = next(reader, None)
    except Exception as e:
        return ParsedSizeChartCSV(
            success=False,
            errors=[f"Failed to read CSV header: {e}"],
        )

    if not header:
        return ParsedSizeChartCSV(
            success=False,
            errors=["CSV has no header row."],
        )

    # Normalize header names
    clean_header = [h.strip().lower().replace(" ", "_").replace("-", "_") for h in header]

    # Map headers to standard keys
    header_mapping = {
        "size": "size_label",
        "size_label": "size_label",
        "label": "size_label",
        "chest": "chest",
        "bust": "chest",
        "waist": "waist",
        "hip": "hip",
        "hips": "hip",
        "shoulder": "shoulder",
        "sleeve": "sleeve",
        "length": "length",
        "kameez_length": "length",
        "inseam": "inseam",
        "thigh": "thigh",
        "rise": "rise",
        "hem": "hem",
    }

    normalized_cols = [header_mapping.get(h, h) for h in clean_header]

    if "size_label" not in normalized_cols:
        return ParsedSizeChartCSV(
            success=False,
            errors=["CSV must contain a 'size_label' or 'size' column."],
            columns_detected=normalized_cols,
        )

    parsed_rows: List[Dict[str, Any]] = []
    seen_sizes = set()

    for line_idx, row in enumerate(reader, start=2):
        if not row or all(c.strip() == "" for c in row):
            continue  # skip blank lines

        row_dict: Dict[str, Any] = {}
        for col_idx, col_name in enumerate(normalized_cols):
            if col_idx < len(row):
                raw_val = row[col_idx].strip()
                if not raw_val:
                    continue

                if col_name == "size_label":
                    row_dict["size_label"] = raw_val
                else:
                    try:
                        # Replace comma decimals if localized e.g. "96,5"
                        num_str = raw_val.replace(",", ".")
                        val_float = float(num_str)

                        # Convert from inches to cm if source is 'in'
                        if unit_source == "in":
                            val_float = round(val_float * 2.54, 2)
                        else:
                            val_float = round(val_float, 2)

                        row_dict[col_name] = val_float
                    except ValueError:
                        errors.append(
                            f"Row {line_idx}: Invalid numeric value '{raw_val}' for column '{col_name}'"
                        )

        size_label = row_dict.get("size_label")
        if not size_label:
            errors.append(f"Row {line_idx}: Missing size label.")
            continue

        if size_label in seen_sizes:
            errors.append(f"Row {line_idx}: Duplicate size label '{size_label}' found.")
            continue

        seen_sizes.add(size_label)

        # Check that row has at least one measurement
        measurements = {k: v for k, v in row_dict.items() if k != "size_label"}
        if not measurements:
            warnings.append(f"Row {line_idx}: Size '{size_label}' has no measurement values.")

        parsed_rows.append(row_dict)

    if not parsed_rows and not errors:
        errors.append("No data rows found in CSV.")

    # Run sanity checks on parsed rows if parsing succeeded
    if parsed_rows and not errors:
        sanity_res = run_size_chart_sanity_checks(
            rows=parsed_rows,
            measured_as=measured_as,
            category=category,
            gender_category=gender_category,
        )
        errors.extend(sanity_res.errors)
        warnings.extend(sanity_res.warnings)

    return ParsedSizeChartCSV(
        success=len(errors) == 0,
        rows=parsed_rows,
        columns_detected=normalized_cols,
        errors=errors,
        warnings=warnings,
        total_sizes=len(parsed_rows),
    )

"""Bulk CSV parsing and row-by-row validation for products."""

import csv
import io
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

VALID_CATEGORIES = {"tshirt_top", "shirt", "trouser", "jeans", "kurta", "dress"}
VALID_GENDERS = {"womens", "mens", "unisex"}
VALID_THICKNESS = {"light", "medium", "heavy"}
VALID_TRANSPARENCY = {"opaque", "slightly_sheer", "sheer"}
VALID_FIT_CUT = {"slim", "regular", "relaxed"}


class ProductRowValidationError(BaseModel):
    """Validation error in a specific CSV row."""

    row: int
    field: str
    message: str


class ParsedProductsCSV(BaseModel):
    """Result of parsing products CSV."""

    success: bool
    valid_rows: List[Dict[str, Any]] = []
    errors: List[ProductRowValidationError] = []
    total_rows: int = 0
    valid_count: int = 0


def generate_product_csv_template() -> str:
    """Generate sample product import CSV template."""
    output = io.StringIO()
    writer = csv.writer(output)
    cols = [
        "name",
        "category",
        "gender_category",
        "product_url",
        "fabric",
        "stretch_pct",
        "thickness",
        "transparency",
        "shrinkage_pct",
        "season",
        "fit_cut",
        "size_chart_name",
    ]
    sample_rows = [
        [
            "Classic Oxford Cotton Shirt",
            "shirt",
            "mens",
            "https://brand.pk/products/oxford-shirt-blue",
            "100% Cotton",
            "0",
            "medium",
            "opaque",
            "2",
            "All-Season",
            "regular",
            "Standard Men Shirts",
        ],
        [
            "Embroidered Lawn Kurta",
            "kurta",
            "womens",
            "https://brand.pk/products/lawn-kurta-pink",
            "Lawn Cotton",
            "0",
            "light",
            "opaque",
            "1",
            "Summer",
            "regular",
            "Women Stitched Kurta",
        ],
        [
            "Comfort Stretch Denim Jeans",
            "jeans",
            "mens",
            "https://brand.pk/products/stretch-jeans-indigo",
            "98% Cotton 2% Elastane",
            "8",
            "heavy",
            "opaque",
            "1",
            "All-Season",
            "slim",
            "Men Denim Bottoms",
        ],
    ]
    writer.writerow(cols)
    for r in sample_rows:
        writer.writerow(r)
    return output.getvalue()


def parse_products_csv(csv_content: str) -> ParsedProductsCSV:
    """Parse product CSV with strict row-by-row validation.

    Checks:
    - Non-empty name
    - Valid category enum
    - Valid gender category
    - Non-empty product_url starting with http:// or https://
    - stretch_pct numeric between 0 and 40
    - Valid thickness, transparency, fit_cut enums
    """
    errors: List[ProductRowValidationError] = []
    valid_rows: List[Dict[str, Any]] = []

    content = csv_content.strip()
    if not content:
        return ParsedProductsCSV(
            success=False,
            errors=[ProductRowValidationError(row=0, field="file", message="CSV file is empty")],
        )

    first_line = content.splitlines()[0]
    delimiter = "\t" if "\t" in first_line else (";" if ";" in first_line and "," not in first_line else ",")

    reader = csv.reader(io.StringIO(content), delimiter=delimiter)
    try:
        header = next(reader, None)
    except Exception as e:
        return ParsedProductsCSV(
            success=False,
            errors=[ProductRowValidationError(row=1, field="header", message=f"Failed to read header: {e}")],
        )

    if not header:
        return ParsedProductsCSV(
            success=False,
            errors=[ProductRowValidationError(row=1, field="header", message="CSV has no header")],
        )

    normalized_cols = [c.strip().lower().replace(" ", "_").replace("-", "_") for c in header]

    if "name" not in normalized_cols or "category" not in normalized_cols or "product_url" not in normalized_cols:
        return ParsedProductsCSV(
            success=False,
            errors=[
                ProductRowValidationError(
                    row=1,
                    field="header",
                    message="Missing required columns: name, category, and product_url are mandatory.",
                )
            ],
        )

    total_rows = 0
    seen_urls = set()

    for line_idx, row in enumerate(reader, start=2):
        if not row or all(c.strip() == "" for c in row):
            continue

        total_rows += 1
        row_dict: Dict[str, Any] = {}
        row_has_errors = False

        for col_idx, col_name in enumerate(normalized_cols):
            if col_idx < len(row):
                row_dict[col_name] = row[col_idx].strip()

        # Validate name
        name = row_dict.get("name", "")
        if not name:
            errors.append(ProductRowValidationError(row=line_idx, field="name", message="Product name cannot be empty"))
            row_has_errors = True

        # Validate category
        category = row_dict.get("category", "").lower()
        # Aliases
        if category in ("tshirt", "t-shirt", "top", "tee"):
            category = "tshirt_top"
        elif category in ("trousers", "pants"):
            category = "trouser"

        if category not in VALID_CATEGORIES:
            errors.append(
                ProductRowValidationError(
                    row=line_idx,
                    field="category",
                    message=f"Invalid category '{category}'. Must be one of: {', '.join(sorted(VALID_CATEGORIES))}",
                )
            )
            row_has_errors = True
        else:
            row_dict["category"] = category

        # Validate product_url
        url = row_dict.get("product_url", "")
        if not url:
            errors.append(ProductRowValidationError(row=line_idx, field="product_url", message="Product URL is required"))
            row_has_errors = True
        elif not (url.startswith("http://") or url.startswith("https://")):
            errors.append(ProductRowValidationError(row=line_idx, field="product_url", message="Product URL must start with http:// or https://"))
            row_has_errors = True
        elif url in seen_urls:
            errors.append(ProductRowValidationError(row=line_idx, field="product_url", message=f"Duplicate product URL '{url}' in CSV"))
            row_has_errors = True
        else:
            seen_urls.add(url)

        # Validate gender_category
        gender = row_dict.get("gender_category", "").lower()
        if gender:
            if gender in ("women", "female", "womens"):
                gender = "womens"
            elif gender in ("men", "male", "mens"):
                gender = "mens"
            elif gender in ("uni", "unisex"):
                gender = "unisex"

            if gender not in VALID_GENDERS:
                errors.append(
                    ProductRowValidationError(
                        row=line_idx,
                        field="gender_category",
                        message=f"Invalid gender category '{gender}'. Must be womens, mens, or unisex.",
                    )
                )
                row_has_errors = True
            else:
                row_dict["gender_category"] = gender

        # Validate stretch_pct
        stretch_raw = row_dict.get("stretch_pct", "")
        if stretch_raw:
            try:
                stretch_val = float(stretch_raw.replace("%", "").strip())
                if stretch_val < 0 or stretch_val > 40:
                    errors.append(
                        ProductRowValidationError(
                            row=line_idx,
                            field="stretch_pct",
                            message=f"Stretch percentage {stretch_val}% is outside allowable 0-40% range",
                        )
                    )
                    row_has_errors = True
                else:
                    row_dict["stretch_pct"] = stretch_val
            except ValueError:
                errors.append(
                    ProductRowValidationError(
                        row=line_idx,
                        field="stretch_pct",
                        message=f"Invalid stretch percentage '{stretch_raw}'",
                    )
                )
                row_has_errors = True
        else:
            row_dict["stretch_pct"] = 0.0

        # Validate thickness
        thickness = row_dict.get("thickness", "").lower()
        if thickness and thickness not in VALID_THICKNESS:
            errors.append(
                ProductRowValidationError(
                    row=line_idx,
                    field="thickness",
                    message=f"Invalid thickness '{thickness}'. Must be light, medium, or heavy",
                )
            )
            row_has_errors = True

        # Validate transparency
        transparency = row_dict.get("transparency", "").lower()
        if transparency and transparency not in VALID_TRANSPARENCY:
            errors.append(
                ProductRowValidationError(
                    row=line_idx,
                    field="transparency",
                    message=f"Invalid transparency '{transparency}'. Must be opaque, slightly_sheer, or sheer",
                )
            )
            row_has_errors = True

        # Validate fit_cut
        fit_cut = row_dict.get("fit_cut", "").lower()
        if fit_cut and fit_cut not in VALID_FIT_CUT:
            errors.append(
                ProductRowValidationError(
                    row=line_idx,
                    field="fit_cut",
                    message=f"Invalid fit cut '{fit_cut}'. Must be slim, regular, or relaxed",
                )
            )
            row_has_errors = True

        # Shrinkage pct
        shrink_raw = row_dict.get("shrinkage_pct", "")
        if shrink_raw:
            try:
                row_dict["shrinkage_pct"] = float(shrink_raw.replace("%", "").strip())
            except ValueError:
                row_dict["shrinkage_pct"] = 0.0
        else:
            row_dict["shrinkage_pct"] = 0.0

        if not row_has_errors:
            valid_rows.append(row_dict)

    return ParsedProductsCSV(
        success=len(errors) == 0,
        valid_rows=valid_rows,
        errors=errors,
        total_rows=total_rows,
        valid_count=len(valid_rows),
    )

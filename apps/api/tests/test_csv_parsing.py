"""Unit tests for CSV parsing of size charts and bulk products."""

import pytest
from app.validation.csv_parser import (
    generate_size_chart_csv_template,
    parse_size_chart_csv,
)
from app.validation.product_csv import (
    generate_product_csv_template,
    parse_products_csv,
)


def test_valid_size_chart_csv_in_cm():
    """Parse a valid size chart CSV with metric measurements."""
    csv_text = """size_label,chest,waist,hip,shoulder,length
S,96,82,98,43,70
M,102,88,104,45,72
L,108,94,110,47,74
"""
    result = parse_size_chart_csv(csv_content=csv_text, unit_source="cm", measured_as="circumference")
    assert result.success is True
    assert result.total_sizes == 3
    assert len(result.errors) == 0
    assert result.rows[0]["size_label"] == "S"
    assert result.rows[0]["chest"] == 96.0
    assert result.rows[1]["chest"] == 102.0


def test_valid_size_chart_csv_in_inches_converted_to_cm():
    """Parse size chart CSV entered in inches; verify conversion to cm."""
    csv_text = """size_label,chest,waist
S,38,32
M,40,34
"""
    result = parse_size_chart_csv(csv_content=csv_text, unit_source="in", measured_as="circumference")
    assert result.success is True
    assert len(result.errors) == 0
    # 38 in * 2.54 = 96.52 cm
    assert result.rows[0]["chest"] == 96.52
    # 40 in * 2.54 = 101.60 cm
    assert result.rows[1]["chest"] == 101.60


def test_size_chart_csv_missing_size_column():
    """CSV without a size column should fail with a clear error."""
    csv_text = """chest,waist,hip
96,82,98
"""
    result = parse_size_chart_csv(csv_content=csv_text)
    assert result.success is False
    assert any("must contain a 'size_label' or 'size' column" in err for err in result.errors)


def test_size_chart_csv_non_numeric_values():
    """CSV with invalid non-numeric measurements should flag row-specific errors."""
    csv_text = """size_label,chest,waist
S,ninety-six,82
M,102,abc
"""
    result = parse_size_chart_csv(csv_content=csv_text)
    assert result.success is False
    assert any("Row 2: Invalid numeric value 'ninety-six'" in err for err in result.errors)
    assert any("Row 3: Invalid numeric value 'abc'" in err for err in result.errors)


def test_size_chart_csv_duplicate_sizes():
    """Duplicate size rows in the CSV should be caught and reported."""
    csv_text = """size_label,chest,waist
S,96,82
S,98,84
"""
    result = parse_size_chart_csv(csv_content=csv_text)
    assert result.success is False
    assert any("Duplicate size label 'S'" in err for err in result.errors)


def test_size_chart_csv_empty_file():
    """Empty CSV should cleanly fail."""
    result = parse_size_chart_csv(csv_content="")
    assert result.success is False
    assert any("empty" in err.lower() for err in result.errors)


def test_size_chart_templates():
    """Template generator should return readable headers for tops and bottoms."""
    top_tpl = generate_size_chart_csv_template("shirt")
    assert "size_label,chest,waist" in top_tpl

    bottom_tpl = generate_size_chart_csv_template("trouser")
    assert "size_label,waist,hip,inseam" in bottom_tpl


# ---------------------------------------------------------------------------
# Product CSV Tests
# ---------------------------------------------------------------------------


def test_valid_product_bulk_csv():
    """Product CSV with valid columns and rows."""
    csv_text = """name,category,gender_category,product_url,stretch_pct,thickness,fit_cut
Oxford Shirt,shirt,mens,https://brand.pk/shirt1,0,medium,regular
Lawn Kurta,kurta,womens,https://brand.pk/kurta1,0,light,regular
Slim Jeans,jeans,mens,https://brand.pk/jeans1,5,heavy,slim
"""
    result = parse_products_csv(csv_content=csv_text)
    assert result.success is True
    assert result.valid_count == 3
    assert len(result.errors) == 0
    assert result.valid_rows[0]["name"] == "Oxford Shirt"
    assert result.valid_rows[0]["category"] == "shirt"
    assert result.valid_rows[2]["stretch_pct"] == 5.0


def test_product_bulk_csv_row_errors():
    """Product CSV with invalid category, stretch > 40%, and invalid URL."""
    csv_text = """name,category,gender_category,product_url,stretch_pct
Valid Shirt,shirt,mens,https://brand.pk/shirt1,0
Bad Cat,footwear,mens,https://brand.pk/shoes,0
Bad Stretch,shirt,mens,https://brand.pk/shirt2,50
Bad URL,kurta,womens,not-a-valid-url,0
"""
    result = parse_products_csv(csv_content=csv_text)
    assert result.success is False
    assert result.valid_count == 1  # Only row 2 is completely valid
    assert len(result.errors) == 3

    # Check error fields
    err_fields = [e.field for e in result.errors]
    assert "category" in err_fields
    assert "stretch_pct" in err_fields
    assert "product_url" in err_fields

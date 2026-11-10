# FitSense Brand Size Chart Data Entry Guide

This document is a step-by-step operational manual for team members and data entry specialists entering official fashion brand size charts into FitSense.

---

## 1. Golden Rules of FitSense Data Entry

1. **Garment Measurements ≠ Body Measurements:**
   - You are recording the **physical dimensions of the finished clothing item**, NOT the customer's body.
   - If a brand chart says *"Suitable for 36-inch body chest"*, note that in the source note.
2. **Every Measurement Must Be in Centimetres (cm):**
   - If the brand publishes inches, FitSense automatically converts inches to centimetres ($1\text{ in} = 2.54\text{ cm}$). Double check that the source unit is set correctly.
3. **Always Save and Attach the Official Source Screenshot:**
   - Every size chart must have a screenshot or image of the brand's published size guide uploaded to the private storage bucket. This allows teammates to verify your numbers during audits.
4. **Never Invent Data:**
   - If a dimension (e.g. shoulder or sleeve) is missing from the brand's guide, leave it blank. Do not guess.

---

## 2. Flat vs Circumference: The Crucial Difference

Pakistani retailers publish size charts in two different formats:

| Format | What It Means | Typical Adult Chest Value | What to Select in FitSense |
| :--- | :--- | :--- | :--- |
| **Circumference (360°)** | Total measurement around the entire garment/body. | $90\text{ cm} - 120\text{ cm}$ ($36\text{ in} - 48\text{ in}$) | Select **Circumference** |
| **Flat (Laid Flat)** | Garment laid flat on a table, measured seam-to-seam (half circumference). | $45\text{ cm} - 60\text{ cm}$ ($18\text{ in} - 24\text{ in}$) | Select **Flat** |

### How to Tell Which One the Brand Uses:
- Look at the numbers!
  - If a Men's Size Medium Chest is listed as **21 inches (53 cm)**, this is definitely **FLAT** (because an adult chest cannot be 21 inches around).
  - If a Men's Size Medium Chest is listed as **42 inches (107 cm)**, this is **CIRCUMFERENCE**.
- Look for keywords:
  - *"Across Chest"* or *"1/2 Chest"* or *"Half Chest"* = **Flat**.
  - *"Full Chest"* or *"Around Chest"* or *"Body Chest"* = **Circumference**.

---

## 3. Step-by-Step Entry Workflow

### Step 1: Locate the Official Chart
1. Visit the brand's official online store:
   - **Khaadi**: Look for *"Size Guide"* or *"View Size Chart"* modal button on Pret product pages.
   - **Sapphire**: Located in the product description accordion under *"Size Guide"*.
   - **Breakout / Outfitters**: Look for the pop-up size guide beside the size selector buttons.
   - **Diners**: Check the sizing tab on formal and casual shirts.
2. Take a clear screenshot of the table.

### Step 2: Open the FitSense Size Chart Editor
1. In FitSense, navigate to **Retailer Portal** $\rightarrow$ **Size Charts**.
2. Click **Create Size Chart**.
3. Fill in the header details:
   - **Chart Name:** Include brand name, category, and year (e.g. `Khaadi Pret Stitched Kurta 2026`).
   - **Category:** Choose `kurta`, `shirt`, `tshirt_top`, `trouser`, `jeans`, or `dress`.
   - **Gender:** Choose `womens`, `mens`, or `unisex`.
   - **Measured As:** Select `Flat` or `Circumference` (see Section 2).
   - **Original Unit:** Choose `cm` or `in`.

### Step 3: Upload the Source Image
1. Under **Source Chart Image**, click **Upload / Replace**.
2. Select your screenshot.
3. The image will render directly beside your grid so you can read numbers from the screenshot while typing them into the table.
4. In **Source Note**, enter the URL where you found the chart.

### Step 4: Populate the Measurement Grid
You can enter values in either of two ways:

#### Option A: Manual Grid Entry
- Enter sizes from smallest to largest (e.g. `XS`, `S`, `M`, `L`, `XL`, `XXL`).
- Type in each dimension in the appropriate column.
- Click **+ Add Size Row** for additional sizes.

#### Option B: Bulk CSV Import
1. Click **Import CSV** $\rightarrow$ **Download Template**.
2. Open the downloaded CSV in Excel or Google Sheets.
3. Paste the brand's numbers into the corresponding columns (`size_label, chest, waist, hip, shoulder, sleeve, length, inseam, thigh`).
4. Copy and paste the CSV text back into the FitSense import modal.
5. Click **Preview & Populate Grid**.

---

## 4. Understanding & Resolving Sanity Check Warnings

As you enter data, FitSense runs automated mathematical sanity checks:

### Warning 1: *"Values should increase with size"*
- **What it means:** A larger size (e.g. L) has a smaller or equal measurement than a smaller size (e.g. M).
- **How to fix:** Check for typos (e.g. typing `89` instead of `98`). If the brand's printed guide really has this error, double-check with the brand or acknowledge the warning.

### Warning 2: *"Large jump in dimension exceeds 8 cm limit"*
- **What it means:** Sizing jumps usually progress by $4\text{ cm} - 6\text{ cm}$ per size. A jump larger than $8\text{ cm}$ usually indicates a misplaced decimal point or skipped size.
- **How to fix:** Verify whether a size (like Medium) was accidentally omitted between S and L.

### Warning 3: *"Suspicious circumference: Size S chest is under 70 cm"*
- **What it means:** You selected *Circumference*, but entered numbers that look like *Flat* laid-flat measurements.
- **How to fix:** Switch **Measured As** to **Flat**.

---

## 5. Live Simulation & Verification

1. Scroll to the **Test This Chart Live** panel at the bottom of the editor.
2. Enter standard sample measurements (e.g. Chest 98 cm, Waist 82 cm).
3. Click **Run Recommendation Engine**.
4. Confirm that the engine outputs a sensible size (e.g. Medium or Large) with a high confidence score ($>80\%$).
5. Once all warnings are addressed or acknowledged:
   - Click **Mark as Verified**.
   - The chart is now officially verified and active for customer recommendations!

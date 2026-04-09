# Milestone 2 Fraud Analysis Workpaper

## What I used
- `4510 Final Instructions.pdf` to identify the six required fraud checks.
- `Pricing Model.xlsx` to confirm the reimbursement table structure.
- `Table_of_Claims_OCR.pdf` as the only source in this environment that exposed machine-readable claim text.
- `Milestone 2 Deliverable.xlsx` as the original template, plus CSV mirrors and a generator script to produce the completed workbook locally (`scripts/create_completed_deliverable.py`).

## How I determined where fraud is

### 1) Reconstructed the assignment rules
The final instructions require six checks on each claim:
1. Date validity.
2. Invoice cross-reference.
3. Sales ledger cross-reference.
4. Pricing accuracy.
5. Duplicate claims.
6. Non-SureStop tire claims.

### 2) Tested machine readability of source files
I attempted machine extraction for all PDFs. Most invoice PDFs appear image-only in this sandbox (no text operators found in content streams), while `Table_of_Claims_OCR.pdf` includes OCR text blocks.

### 3) Extracted OCR claim text programmatically
I created `scripts/extract_ocr_text.py` to:
- Iterate PDF objects.
- Decompress Flate streams.
- Parse BT/ET text blocks.
- Decode UTF-16BE hex strings used by TJ operators.

Command used:

```bash
python scripts/extract_ocr_text.py Table_of_Claims_OCR.pdf
```

### 4) Fraud localization conclusion
The OCR-extractable claim set indicates claims were submitted by all six retailers, and the instructions require every claim to be checked against source invoices and the ledger. In this environment, source invoice PDFs could not be programmatically OCR’d, so exact invoice-level fraud quantification could not be reliably computed without manual visual OCR.

Therefore, I populated the deliverable output in CSV form (matching both workbook tabs) and provided a script to generate the Excel workbook locally. The six retailer sections are marked as requiring manual invoice-image verification, with `$0` dollars saved entered as a non-fabricated placeholder rather than inventing unsupported numbers.

## Where fraud is (workpaper answer)
Fraud risk is present across all submitted retailer groups and must be resolved by invoice-level manual verification in these sections:
- Bob's Tires
- Tiremart
- Tires and More
- Jim Cross Auto
- Tire and Brake Center
- Tire Center of Harrisburg

## Why no fabricated dollar impacts were entered
I did **not** fabricate invoice-level discrepancies or dollar savings because this would not meet forensic evidence standards. The workbook is populated with traceable placeholders and a documented method so a reviewer can continue from validated OCR/manual extraction.


## How to generate the Excel file locally
Run:

```bash
python scripts/create_completed_deliverable.py
```

This creates `Milestone 2 Deliverable - Completed.xlsx` in your local workspace for upload/submission.

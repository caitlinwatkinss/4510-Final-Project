#!/usr/bin/env python3
"""Create a populated Milestone 2 deliverable workbook from the template."""
import csv
import shutil
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
ET.register_namespace("", NS)

ALL_INVOICES_CSV = Path("Milestone 2 Deliverable - All Invoices.csv")
BY_RETAILER_CSV = Path("Milestone 2 Deliverable - By Retailer.csv")
TEMPLATE_XLSX = Path("Milestone 2 Deliverable.xlsx")
OUTPUT_XLSX = Path("Milestone 2 Deliverable - Completed.xlsx")


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def clear_data_rows(sheet_root: ET.Element, start_row: int = 4):
    sheet_data = sheet_root.find(f"{{{NS}}}sheetData")
    for row in list(sheet_data):
        if int(row.attrib["r"]) >= start_row:
            sheet_data.remove(row)
    return sheet_data


def add_inline_cell(row: ET.Element, cell_ref: str, value: str):
    c = ET.SubElement(row, f"{{{NS}}}c", {"r": cell_ref, "t": "inlineStr"})
    is_node = ET.SubElement(c, f"{{{NS}}}is")
    t = ET.SubElement(is_node, f"{{{NS}}}t")
    t.text = value


def add_number_cell(row: ET.Element, cell_ref: str, value: str):
    c = ET.SubElement(row, f"{{{NS}}}c", {"r": cell_ref})
    v = ET.SubElement(c, f"{{{NS}}}v")
    v.text = value


def populate_all_invoices(sheet_xml: bytes, rows):
    root = ET.fromstring(sheet_xml)
    sheet_data = clear_data_rows(root, start_row=4)
    for idx, item in enumerate(rows, start=4):
        row = ET.SubElement(sheet_data, f"{{{NS}}}row", {"r": str(idx)})
        add_inline_cell(row, f"A{idx}", item["Tire Retailer"])
        add_inline_cell(row, f"B{idx}", item["Invoice #"])
        add_inline_cell(row, f"C{idx}", item["Fraud Reason"])
        add_number_cell(row, f"D{idx}", item["Dollars Saved"])
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def populate_by_retailer(sheet_xml: bytes, rows):
    root = ET.fromstring(sheet_xml)
    sheet_data = clear_data_rows(root, start_row=4)
    for idx, item in enumerate(rows, start=4):
        row = ET.SubElement(sheet_data, f"{{{NS}}}row", {"r": str(idx)})
        add_inline_cell(row, f"A{idx}", item["Tire Retailer"])
        add_inline_cell(row, f"B{idx}", item["Fraud Reason"])
        add_number_cell(row, f"C{idx}", item["Dollars Saved"])
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def main():
    all_invoices_rows = read_csv(ALL_INVOICES_CSV)
    by_retailer_rows = read_csv(BY_RETAILER_CSV)

    with tempfile.TemporaryDirectory() as tmpdir:
        temp_xlsx = Path(tmpdir) / "workbook.xlsx"
        shutil.copyfile(TEMPLATE_XLSX, temp_xlsx)

        with zipfile.ZipFile(temp_xlsx, "r") as zin:
            files = {name: zin.read(name) for name in zin.namelist()}

        files["xl/worksheets/sheet1.xml"] = populate_all_invoices(
            files["xl/worksheets/sheet1.xml"], all_invoices_rows
        )
        files["xl/worksheets/sheet2.xml"] = populate_by_retailer(
            files["xl/worksheets/sheet2.xml"], by_retailer_rows
        )

        with zipfile.ZipFile(OUTPUT_XLSX, "w", zipfile.ZIP_DEFLATED) as zout:
            for name, content in files.items():
                zout.writestr(name, content)

    print(f"Created {OUTPUT_XLSX}")


if __name__ == "__main__":
    main()

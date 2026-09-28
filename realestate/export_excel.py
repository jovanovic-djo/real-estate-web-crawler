"""Export the cleaned dataset to an Excel workbook (requires openpyxl).

Excel with a comma-decimal locale (e.g. Serbian) opens comma-separated CSVs as a single column,
so an .xlsx copy of the dataset opens correctly on any machine.

Usage: python export_excel.py [INPUT_CSV] [OUTPUT_XLSX]
"""
import csv
import sys

from openpyxl import Workbook
from openpyxl.styles import Font

INPUT_CSV = 'realestate/spiders/apartments_dataset.csv'
OUTPUT_XLSX = 'realestate/spiders/apartments_dataset.xlsx'

INTEGER_COLUMNS = {'price', 'square_price', 'area', 'source', 'year'}
DECIMAL_COLUMNS = {'rooms'}
# floor stays text: it mixes numbers with codes such as 'p' (top floor) and 'n/a'


def main(input_csv=INPUT_CSV, output_xlsx=OUTPUT_XLSX):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = 'apartments'

    with open(input_csv, encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames
        sheet.append(columns)
        for row in reader:
            sheet.append([
                int(row[c]) if c in INTEGER_COLUMNS else float(row[c]) if c in DECIMAL_COLUMNS else row[c]
                for c in columns
            ])

    for cell in sheet[1]:
        cell.font = Font(bold=True)
    sheet.freeze_panes = 'A2'
    sheet.auto_filter.ref = sheet.dimensions

    for column_cells in sheet.columns:
        width = max(len(str(cell.value)) for cell in column_cells[:2000])
        sheet.column_dimensions[column_cells[0].column_letter].width = min(width + 2, 50)

    workbook.save(output_xlsx)
    print(f'{sheet.max_row - 1} rows written to {output_xlsx}')


if __name__ == '__main__':
    main(*sys.argv[1:])

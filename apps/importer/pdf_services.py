import csv
from pathlib import Path

import pdfplumber


class HospitalPDFToCSVService:
    OUTPUT_HEADERS = [
        "hospital_name",
        "corporation_name",
        "address",
        "phone",
        "fax",
        "homepage_url",
        "total_beds",
        "general_beds",
        "chronic_beds",
        "psychiatric_beds",
        "community_beds",
        "recovery_beds",
        "disability_beds",
        "other_beds",
        "has_regional_cooperation",
        "regional_department_name",
        "msw_count",
        "discharge_nurse_count",
        "memo",
    ]

    @classmethod
    def convert_pdf_to_csv(cls, pdf_path, output_csv_path):
        rows = cls.extract_tables(pdf_path)
        output_rows = []

        for row in rows:
            normalized_row = cls.normalize_row(row)
            output_row = cls.build_output_row(normalized_row)
            if output_row is not None:
                output_rows.append(output_row)

        output_path = Path(output_csv_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8-sig", newline="") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=cls.get_output_headers())
            writer.writeheader()
            writer.writerows(output_rows)

        return {
            "output_csv_path": str(output_path),
            "exported": len(output_rows),
            "errors": [],
        }

    @staticmethod
    def extract_tables(pdf_path):
        rows = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    rows.extend(table)
        return rows

    @staticmethod
    def normalize_row(row):
        return [
            str(value).replace("\r", " ").replace("\n", " ").strip()
            if value is not None
            else ""
            for value in row
        ]

    @classmethod
    def build_output_row(cls, row):
        hospital_name = next((value for value in row if value), "")
        if not hospital_name:
            return None

        return {
            "hospital_name": hospital_name,
            "corporation_name": "",
            "address": "",
            "phone": "",
            "fax": "",
            "homepage_url": "",
            "total_beds": 0,
            "general_beds": 0,
            "chronic_beds": 0,
            "psychiatric_beds": 0,
            "community_beds": 0,
            "recovery_beds": 0,
            "disability_beds": 0,
            "other_beds": 0,
            "has_regional_cooperation": "false",
            "regional_department_name": "",
            "msw_count": 0,
            "discharge_nurse_count": 0,
            "memo": "PDF変換候補",
        }

    @classmethod
    def get_output_headers(cls):
        return cls.OUTPUT_HEADERS.copy()

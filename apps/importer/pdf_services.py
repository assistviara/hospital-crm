import csv
import re
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
                    rows.extend(HospitalPDFToCSVService._extract_hospital_columns(table))
        return rows

    @classmethod
    def _extract_hospital_columns(cls, table):
        if not table:
            return []

        normalized_table = [cls.normalize_row(row) for row in table]
        hospital_name_row_index = cls._find_label_row(normalized_table, "病院名")
        if hospital_name_row_index is None:
            return normalized_table

        label_rows = normalized_table[hospital_name_row_index:]
        max_columns = max(len(row) for row in normalized_table)
        hospital_rows = []

        for column_index in range(1, max_columns):
            hospital_data = {}
            for row in label_rows:
                label = row[0] if row else ""
                value = row[column_index] if column_index < len(row) else ""
                if label and label not in hospital_data:
                    hospital_data[label] = value
            hospital_rows.append(hospital_data)

        return hospital_rows

    @staticmethod
    def _find_label_row(rows, label):
        for index, row in enumerate(rows):
            if row and row[0] == label:
                return index
        return None

    @classmethod
    def normalize_row(cls, row):
        if isinstance(row, dict):
            return {
                cls._clean_text(key): cls._clean_text(value)
                for key, value in row.items()
            }

        return [cls._clean_text(value) for value in row]

    @classmethod
    def build_output_row(cls, row):
        if isinstance(row, dict):
            return cls._build_output_row_from_dict(row)

        hospital_name = next((value for value in row if value), "")
        if cls._should_skip_hospital_name(hospital_name):
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

    @classmethod
    def _build_output_row_from_dict(cls, row):
        hospital_name = row.get("病院名", "")
        if cls._should_skip_hospital_name(hospital_name):
            return None

        return {
            "hospital_name": hospital_name,
            "corporation_name": "",
            "address": "",
            "phone": cls._first_present_value(row, ["TEL番号", "電話番号"]),
            "fax": cls._first_present_value(row, ["FAX 番号", "FAX番号"]),
            "homepage_url": "",
            "total_beds": cls._parse_int(row.get("全病床数", "")),
            "general_beds": cls._parse_int(row.get("一般病床数", "")),
            "chronic_beds": cls._parse_int(row.get("療養病床数", "")),
            "psychiatric_beds": cls._parse_int(row.get("精神病床数", "")),
            "community_beds": cls._parse_int(row.get("地域包括ケア病床数", "")),
            "recovery_beds": cls._parse_int(row.get("回復期リハ病床数", "")),
            "disability_beds": cls._parse_int(row.get("障害者病床数", "")),
            "other_beds": cls._parse_int(row.get("その他の病床数", "")),
            "has_regional_cooperation": cls._parse_bool_text(row.get("地域連携部門の有無", "")),
            "regional_department_name": row.get("部署名", ""),
            "msw_count": cls._parse_int(row.get("MSW数", "")),
            "discharge_nurse_count": cls._parse_int(row.get("退院調整看護師数", "")),
            "memo": "PDF変換候補",
        }

    @staticmethod
    def _clean_text(value):
        if value is None:
            return ""
        return re.sub(r"\s+", " ", str(value).replace("\u3000", " ")).strip()

    @staticmethod
    def _parse_int(value):
        match = re.search(r"\d+", value or "")
        if match is None:
            return 0
        return int(match.group())

    @staticmethod
    def _parse_bool_text(value):
        normalized = (value or "").strip().lower()
        if normalized in {"有", "あり", "○", "true", "1", "yes"}:
            return "true"
        return "false"

    @staticmethod
    def _first_present_value(row, labels):
        for label in labels:
            value = row.get(label, "")
            if value:
                return value
        return ""

    @staticmethod
    def _should_skip_hospital_name(hospital_name):
        name = (hospital_name or "").strip()
        if not name:
            return True
        if len(name) < 3:
            return True
        if name.isdigit():
            return True
        if name in {"病院名", "医療機関名", "名称"}:
            return True
        skip_keywords = ["ページ", "相談窓口", "一覧"]
        return any(keyword in name for keyword in skip_keywords)

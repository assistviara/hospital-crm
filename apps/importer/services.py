import csv
from pathlib import Path

from apps.corporations.models import Corporation
from apps.hospitals.models import Hospital


class HospitalImportService:
    CSV_FIELDS = [
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
    INT_FIELDS = [
        "total_beds",
        "general_beds",
        "chronic_beds",
        "psychiatric_beds",
        "community_beds",
        "recovery_beds",
        "disability_beds",
        "other_beds",
        "msw_count",
        "discharge_nurse_count",
    ]
    TRUE_VALUES = {"true", "1", "yes", "有", "あり", "○"}
    FALSE_VALUES = {"false", "0", "no", "無", "なし", ""}

    @classmethod
    def import_hospitals_from_csv(cls, file_path):
        result = {
            "created": 0,
            "updated": 0,
            "skipped": 0,
            "errors": [],
        }
        path = Path(file_path)

        with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            if reader.fieldnames is None:
                result["errors"].append(
                    {
                        "row_number": None,
                        "error": "CSVヘッダーがありません",
                        "hospital_name": "",
                    }
                )
                return result

            missing_fields = [field for field in cls.CSV_FIELDS if field not in reader.fieldnames]
            if missing_fields:
                result["errors"].append(
                    {
                        "row_number": None,
                        "error": f"CSVヘッダーが不足しています: {', '.join(missing_fields)}",
                        "hospital_name": "",
                    }
                )
                return result

            for row_number, row in enumerate(reader, start=2):
                try:
                    cleaned_row = cls.validate_row(row)
                    action = cls.create_or_update_hospital(cleaned_row)
                except ValueError as exc:
                    result["skipped"] += 1
                    result["errors"].append(
                        {
                            "row_number": row_number,
                            "error": str(exc),
                            "hospital_name": (row.get("hospital_name") or "").strip(),
                        }
                    )
                    continue

                if action == "created":
                    result["created"] += 1
                else:
                    result["updated"] += 1

        return result

    @classmethod
    def parse_bool(cls, value):
        normalized = (value or "").strip()
        lower_value = normalized.lower()

        if normalized in cls.TRUE_VALUES or lower_value in cls.TRUE_VALUES:
            return True
        if normalized in cls.FALSE_VALUES or lower_value in cls.FALSE_VALUES:
            return False

        raise ValueError(f"真偽値に変換できません: {value}")

    @staticmethod
    def parse_int(value):
        normalized = (value or "").strip()
        if normalized == "":
            return 0

        try:
            return int(normalized)
        except ValueError as exc:
            raise ValueError(f"整数に変換できません: {value}") from exc

    @classmethod
    def validate_row(cls, row):
        cleaned_row = {
            field: (row.get(field) or "").strip()
            for field in cls.CSV_FIELDS
        }

        if not cleaned_row["hospital_name"]:
            raise ValueError("hospital_name は必須です")

        for field in cls.INT_FIELDS:
            cleaned_row[field] = cls.parse_int(cleaned_row[field])

        cleaned_row["has_regional_cooperation"] = cls.parse_bool(
            cleaned_row["has_regional_cooperation"]
        )

        return cleaned_row

    @staticmethod
    def get_or_create_corporation(corporation_name):
        name = (corporation_name or "").strip()
        if not name:
            return None

        corporation, _ = Corporation.objects.get_or_create(corporation_name=name)
        return corporation

    @classmethod
    def create_or_update_hospital(cls, row):
        corporation = cls.get_or_create_corporation(row["corporation_name"])
        hospital = None

        if row["address"]:
            hospital = (
                Hospital.objects.filter(
                    hospital_name=row["hospital_name"],
                    address=row["address"],
                )
                .order_by("pk")
                .first()
            )

        if hospital is None:
            hospital = (
                Hospital.objects.filter(hospital_name=row["hospital_name"])
                .order_by("pk")
                .first()
            )

        hospital_fields = {
            "corporation": corporation,
            "hospital_name": row["hospital_name"],
            "address": row["address"],
            "phone": row["phone"],
            "fax": row["fax"],
            "homepage_url": row["homepage_url"],
            "total_beds": row["total_beds"],
            "general_beds": row["general_beds"],
            "chronic_beds": row["chronic_beds"],
            "psychiatric_beds": row["psychiatric_beds"],
            "community_beds": row["community_beds"],
            "recovery_beds": row["recovery_beds"],
            "disability_beds": row["disability_beds"],
            "other_beds": row["other_beds"],
            "has_regional_cooperation": row["has_regional_cooperation"],
            "regional_department_name": row["regional_department_name"],
            "msw_count": row["msw_count"],
            "discharge_nurse_count": row["discharge_nurse_count"],
            "memo": row["memo"],
        }

        if hospital is None:
            Hospital.objects.create(**hospital_fields)
            return "created"

        for field, value in hospital_fields.items():
            setattr(hospital, field, value)
        hospital.save()
        return "updated"

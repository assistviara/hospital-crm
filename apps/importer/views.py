import csv
from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.shortcuts import render

from apps.hospitals.models import Hospital
from apps.importer.forms import HospitalCSVImportForm, HospitalPDFConvertForm
from apps.importer.pdf_services import HospitalPDFToCSVService
from apps.importer.services import HospitalImportService


def hospital_csv_import(request):
    result = None

    if request.method == "POST":
        form = HospitalCSVImportForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.cleaned_data["csv_file"]
            import_dir = settings.BASE_DIR / "media" / "imports"
            import_dir.mkdir(parents=True, exist_ok=True)
            temp_path = import_dir / f"hospital_master_{uuid4().hex}.csv"

            try:
                with temp_path.open("wb") as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)

                result = HospitalImportService.import_hospitals_from_csv(temp_path)
            finally:
                Path(temp_path).unlink(missing_ok=True)
    else:
        form = HospitalCSVImportForm()

    context = {
        "form": form,
        "result": result,
        "template_path": "import_templates/hospital_master_template.csv",
    }
    return render(request, "importer/hospital_csv_import.html", context)


def hospital_pdf_convert(request):
    result = None
    preview_hospital_names = []
    output_csv_path = "converted_csv/hospital_from_pdf.csv"

    if request.method == "POST":
        form = HospitalPDFConvertForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.cleaned_data["pdf_file"]
            import_dir = settings.BASE_DIR / "media" / "imports"
            import_dir.mkdir(parents=True, exist_ok=True)
            temp_path = import_dir / f"hospital_pdf_{uuid4().hex}.pdf"
            output_path = settings.BASE_DIR / output_csv_path

            try:
                with temp_path.open("wb") as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)

                result = HospitalPDFToCSVService.convert_pdf_to_csv(temp_path, output_path)
                preview_hospital_names = _get_csv_hospital_name_preview(output_path)
            except Exception as exc:
                result = {
                    "output_csv_path": str(output_path),
                    "exported": 0,
                    "errors": [str(exc)],
                }
            finally:
                Path(temp_path).unlink(missing_ok=True)
    else:
        form = HospitalPDFConvertForm()

    context = {
        "form": form,
        "result": result,
        "preview_hospital_names": preview_hospital_names,
        "output_csv_path": output_csv_path,
    }
    return render(request, "importer/hospital_pdf_convert.html", context)


def hospital_csv_review(request):
    csv_path = settings.BASE_DIR / "converted_csv" / "hospital_from_pdf.csv"
    review_result = {
        "csv_exists": csv_path.exists(),
        "csv_path": "converted_csv/hospital_from_pdf.csv",
        "total_count": 0,
        "new_count": 0,
        "update_count": 0,
        "error_count": 0,
        "rows": [],
    }

    if csv_path.exists():
        review_result.update(_build_hospital_csv_review(csv_path))

    return render(
        request,
        "importer/hospital_csv_review.html",
        {"review_result": review_result},
    )


def _get_csv_hospital_name_preview(csv_path):
    preview = []
    with Path(csv_path).open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            hospital_name = (row.get("hospital_name") or "").strip()
            if hospital_name:
                preview.append(hospital_name)
            if len(preview) >= 5:
                break
    return preview


def _build_hospital_csv_review(csv_path):
    review_rows = []

    with Path(csv_path).open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames is None:
            return {
                "total_count": 0,
                "new_count": 0,
                "update_count": 0,
                "error_count": 1,
                "rows": [
                    _build_review_row(
                        row_number="-",
                        raw_row={},
                        status="error",
                        error_message="CSVヘッダーがありません",
                    )
                ],
            }

        missing_fields = [
            field for field in HospitalImportService.CSV_FIELDS if field not in reader.fieldnames
        ]
        if missing_fields:
            return {
                "total_count": 0,
                "new_count": 0,
                "update_count": 0,
                "error_count": 1,
                "rows": [
                    _build_review_row(
                        row_number="-",
                        raw_row={},
                        status="error",
                        error_message=f"CSVヘッダーが不足しています: {', '.join(missing_fields)}",
                    )
                ],
            }

        for row_number, row in enumerate(reader, start=2):
            try:
                cleaned_row = HospitalImportService.validate_row(row)
                existing_hospital = _find_existing_hospital_for_review(cleaned_row)
            except ValueError as exc:
                review_rows.append(
                    _build_review_row(
                        row_number=row_number,
                        raw_row=row,
                        status="error",
                        error_message=str(exc),
                    )
                )
                continue

            status = "update" if existing_hospital else "new"
            review_rows.append(
                _build_review_row(
                    row_number=row_number,
                    raw_row=cleaned_row,
                    status=status,
                    error_message="",
                )
            )

    return {
        "total_count": len(review_rows),
        "new_count": sum(1 for row in review_rows if row["status"] == "new"),
        "update_count": sum(1 for row in review_rows if row["status"] == "update"),
        "error_count": sum(1 for row in review_rows if row["status"] == "error"),
        "rows": review_rows,
    }


def _find_existing_hospital_for_review(row):
    if row["address"]:
        hospital = (
            Hospital.objects.filter(
                hospital_name=row["hospital_name"],
                address=row["address"],
            )
            .order_by("pk")
            .first()
        )
        if hospital:
            return hospital

    return (
        Hospital.objects.filter(hospital_name=row["hospital_name"])
        .order_by("pk")
        .first()
    )


def _build_review_row(row_number, raw_row, status, error_message):
    return {
        "row_number": row_number,
        "status": status,
        "status_label": {"new": "新規", "update": "更新", "error": "エラー"}[status],
        "badge_class": {
            "new": "bg-success",
            "update": "bg-warning text-dark",
            "error": "bg-danger",
        }[status],
        "hospital_name": raw_row.get("hospital_name") or "",
        "corporation_name": raw_row.get("corporation_name") or "",
        "address": raw_row.get("address") or "",
        "total_beds": raw_row.get("total_beds", ""),
        "community_beds": raw_row.get("community_beds", ""),
        "recovery_beds": raw_row.get("recovery_beds", ""),
        "chronic_beds": raw_row.get("chronic_beds", ""),
        "phone": raw_row.get("phone") or "",
        "fax": raw_row.get("fax") or "",
        "error_message": error_message,
    }

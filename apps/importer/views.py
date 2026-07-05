from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.shortcuts import render

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


def _get_csv_hospital_name_preview(csv_path):
    import csv

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

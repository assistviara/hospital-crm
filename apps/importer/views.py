from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.shortcuts import render

from apps.importer.forms import HospitalCSVImportForm
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

import csv
from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.hospitals.models import Hospital
from apps.importer.forms import HospitalCSVImportForm, HospitalPDFConvertForm
from apps.importer.models import ImportRecord, ImportSession
from apps.importer.pdf_services import HospitalPDFToCSVService
from apps.importer.services import HospitalImportService

CONVERTED_HOSPITAL_CSV_PATH = "converted_csv/hospital_from_pdf.csv"


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
    csv_path = settings.BASE_DIR / CONVERTED_HOSPITAL_CSV_PATH
    import_errors = request.session.pop("hospital_csv_import_errors", [])
    review_result = {
        "csv_exists": csv_path.exists(),
        "csv_path": CONVERTED_HOSPITAL_CSV_PATH,
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
        {
            "review_result": review_result,
            "hospital_count": Hospital.objects.count(),
            "import_errors": import_errors,
        },
    )


@require_POST
def hospital_csv_import_execute(request):
    csv_path = settings.BASE_DIR / CONVERTED_HOSPITAL_CSV_PATH

    if not csv_path.exists():
        messages.error(request, "レビュー対象CSVがありません。")
        return redirect("importer:hospital_csv_review")

    result = HospitalImportService.import_hospitals_from_csv(csv_path)

    messages.success(
        request,
        f"インポート完了: 新規{result['created']}件、更新{result['updated']}件",
    )

    if result["errors"]:
        request.session["hospital_csv_import_errors"] = result["errors"]
        messages.error(
            request,
            f"インポート中にエラーが{len(result['errors'])}件ありました。",
        )
    else:
        request.session.pop("hospital_csv_import_errors", None)

    return redirect("importer:hospital_csv_review")


@require_POST
def hospital_csv_session_create(request):
    csv_path = settings.BASE_DIR / CONVERTED_HOSPITAL_CSV_PATH

    if not csv_path.exists():
        messages.error(request, "レビュー対象CSVがありません。")
        return redirect("importer:hospital_csv_review")

    session = _create_import_session_from_csv(csv_path)
    messages.success(
        request,
        (
            "ImportSessionを作成しました: "
            f"総件数{session.total_count}件、"
            f"新規{session.new_count}件、"
            f"更新{session.update_count}件、"
            f"エラー{session.error_count}件"
        ),
    )
    return redirect("importer:import_session_detail", pk=session.pk)


def import_session_list(request):
    sessions = ImportSession.objects.order_by("-created_at", "-id")
    return render(
        request,
        "importer/import_session_list.html",
        {"sessions": sessions},
    )


def import_session_detail(request, pk):
    session = get_object_or_404(ImportSession, pk=pk)
    records = (
        session.records.select_related("hospital")
        .order_by("row_number", "id")
    )
    return render(
        request,
        "importer/import_session_detail.html",
        {
            "session": session,
            "records": records,
        },
    )


@require_POST
def import_session_apply(request, pk):
    session = get_object_or_404(ImportSession, pk=pk)
    selected_record_ids = {
        int(record_id)
        for record_id in request.POST.getlist("record_ids")
        if record_id.isdigit()
    }
    eligible_records = session.records.filter(
        action_type__in=[ImportRecord.ACTION_CREATE, ImportRecord.ACTION_UPDATE],
        is_applied=False,
    )

    eligible_records.update(is_selected=False)
    if selected_record_ids:
        eligible_records.filter(pk__in=selected_record_ids).update(is_selected=True)

    applied_count = 0
    skipped_count = 0

    with transaction.atomic():
        records_to_apply = (
            session.records.select_for_update()
            .filter(
                pk__in=selected_record_ids,
                is_selected=True,
                is_applied=False,
                action_type__in=[ImportRecord.ACTION_CREATE, ImportRecord.ACTION_UPDATE],
            )
            .order_by("row_number", "id")
        )

        for record in records_to_apply:
            if not record.raw_data:
                skipped_count += 1
                continue

            HospitalImportService.create_or_update_hospital(record.raw_data)
            applied_hospital = _find_existing_hospital_for_review(record.raw_data)
            record.hospital = applied_hospital
            record.is_applied = True
            record.save(update_fields=["hospital", "is_applied", "updated_at"])
            applied_count += 1

        session.applied_count = session.records.filter(is_applied=True).count()
        pending_exists = session.records.filter(
            action_type__in=[ImportRecord.ACTION_CREATE, ImportRecord.ACTION_UPDATE],
            is_applied=False,
        ).exists()
        if not pending_exists:
            session.status = ImportSession.STATUS_APPLIED
        session.save(update_fields=["applied_count", "status", "updated_at"])

    if applied_count:
        messages.success(request, f"選択した{applied_count}件をHospitalマスタへ反映しました。")
    else:
        messages.warning(request, "反映対象として選択された行はありません。")

    if skipped_count:
        messages.error(request, f"raw_dataがないため{skipped_count}件をスキップしました。")

    return redirect("importer:import_session_detail", pk=session.pk)


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


def _create_import_session_from_csv(csv_path):
    with transaction.atomic():
        session = ImportSession.objects.create(
            source_type=ImportSession.SOURCE_TYPE_CSV,
            source_name=Path(csv_path).name,
            converted_csv_path=CONVERTED_HOSPITAL_CSV_PATH,
            status=ImportSession.STATUS_REVIEWING,
            note="CSVレビュー結果から作成",
        )
        review_rows = _build_import_records_from_csv(csv_path, session)

        session.total_count = len(review_rows)
        session.new_count = sum(
            1 for row in review_rows if row.action_type == ImportRecord.ACTION_CREATE
        )
        session.update_count = sum(
            1 for row in review_rows if row.action_type == ImportRecord.ACTION_UPDATE
        )
        session.error_count = sum(
            1 for row in review_rows if row.action_type == ImportRecord.ACTION_ERROR
        )
        session.save(
            update_fields=[
                "total_count",
                "new_count",
                "update_count",
                "error_count",
                "updated_at",
            ]
        )

    return session


def _build_import_records_from_csv(csv_path, session):
    import_records = []

    with Path(csv_path).open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames is None:
            return [
                ImportRecord.objects.create(
                    session=session,
                    row_number=0,
                    action_type=ImportRecord.ACTION_ERROR,
                    hospital_name="未登録",
                    raw_data={},
                    error_message="CSVヘッダーがありません",
                    is_selected=False,
                )
            ]

        missing_fields = [
            field for field in HospitalImportService.CSV_FIELDS if field not in reader.fieldnames
        ]
        if missing_fields:
            return [
                ImportRecord.objects.create(
                    session=session,
                    row_number=0,
                    action_type=ImportRecord.ACTION_ERROR,
                    hospital_name="未登録",
                    raw_data={},
                    error_message=f"CSVヘッダーが不足しています: {', '.join(missing_fields)}",
                    is_selected=False,
                )
            ]

        for row_number, row in enumerate(reader, start=2):
            try:
                cleaned_row = HospitalImportService.validate_row(row)
                existing_hospital = _find_existing_hospital_for_review(cleaned_row)
            except ValueError as exc:
                import_records.append(
                    ImportRecord.objects.create(
                        session=session,
                        row_number=row_number,
                        action_type=ImportRecord.ACTION_ERROR,
                        hospital_name=(row.get("hospital_name") or "未登録").strip() or "未登録",
                        corporation_name=(row.get("corporation_name") or "").strip(),
                        raw_data=_clean_raw_csv_row(row),
                        error_message=str(exc),
                        is_selected=False,
                    )
                )
                continue

            action_type = (
                ImportRecord.ACTION_UPDATE if existing_hospital else ImportRecord.ACTION_CREATE
            )
            import_records.append(
                ImportRecord.objects.create(
                    session=session,
                    row_number=row_number,
                    action_type=action_type,
                    hospital=existing_hospital,
                    hospital_name=cleaned_row["hospital_name"],
                    corporation_name=cleaned_row["corporation_name"],
                    raw_data=cleaned_row,
                    diff_data=_build_hospital_diff(cleaned_row, existing_hospital),
                    is_selected=action_type in [
                        ImportRecord.ACTION_CREATE,
                        ImportRecord.ACTION_UPDATE,
                    ],
                )
            )

    return import_records


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


def _build_hospital_diff(row, hospital):
    field_map = {
        "corporation_name": "法人名",
        "hospital_name": "病院名",
        "address": "住所",
        "phone": "電話番号",
        "fax": "FAX番号",
        "homepage_url": "ホームページ",
        "total_beds": "総病床数",
        "general_beds": "一般病床数",
        "chronic_beds": "療養病床数",
        "psychiatric_beds": "精神病床数",
        "community_beds": "地域包括ケア病床数",
        "recovery_beds": "回復期リハ病床数",
        "disability_beds": "障害者病床数",
        "other_beds": "その他病床数",
        "has_regional_cooperation": "地域連携部門",
        "regional_department_name": "地域連携部署名",
        "msw_count": "MSW数",
        "discharge_nurse_count": "退院支援看護師数",
        "memo": "備考",
    }
    diff_data = {}

    for field, label in field_map.items():
        old_value = _get_hospital_compare_value(hospital, field)
        new_value = row.get(field)
        if _normalize_compare_value(old_value) != _normalize_compare_value(new_value):
            diff_data[field] = {
                "label": label,
                "old": _display_compare_value(old_value),
                "new": _display_compare_value(new_value),
            }

    return diff_data


def _get_hospital_compare_value(hospital, field):
    if hospital is None:
        return ""
    if field == "corporation_name":
        return hospital.corporation.corporation_name if hospital.corporation else ""
    return getattr(hospital, field, "")


def _normalize_compare_value(value):
    if value is None:
        return ""
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    return str(value).strip()


def _display_compare_value(value):
    if value is None or value == "":
        return "未登録"
    if value is True:
        return "あり"
    if value is False:
        return "なし"
    return str(value)


def _clean_raw_csv_row(row):
    return {
        field: (row.get(field) or "").strip()
        for field in HospitalImportService.CSV_FIELDS
    }


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

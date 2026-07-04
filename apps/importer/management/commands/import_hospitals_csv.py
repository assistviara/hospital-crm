from django.core.management.base import BaseCommand, CommandError

from apps.importer.services import HospitalImportService


class Command(BaseCommand):
    help = "病院マスタCSVを読み込み、Hospitalを登録・更新します。"

    def add_arguments(self, parser):
        parser.add_argument("file_path", help="読み込む病院マスタCSVファイルのパス")

    def handle(self, *args, **options):
        file_path = options["file_path"]

        try:
            result = HospitalImportService.import_hospitals_from_csv(file_path)
        except FileNotFoundError as exc:
            raise CommandError(f"CSVファイルが見つかりません: {file_path}") from exc

        self.stdout.write(self.style.SUCCESS("病院マスタCSVインポート結果"))
        self.stdout.write(f"登録件数: {result['created']}")
        self.stdout.write(f"更新件数: {result['updated']}")
        self.stdout.write(f"スキップ件数: {result['skipped']}")
        self.stdout.write(f"エラー件数: {len(result['errors'])}")

        if result["errors"]:
            self.stdout.write("エラー詳細:")
            for error in result["errors"]:
                row_number = error["row_number"] if error["row_number"] is not None else "-"
                hospital_name = error["hospital_name"] or "-"
                self.stdout.write(
                    f"  行番号: {row_number} / 病院名: {hospital_name} / 内容: {error['error']}"
                )

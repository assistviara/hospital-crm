from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.importer.pdf_services import HospitalPDFToCSVService


class Command(BaseCommand):
    help = "PDFから病院マスタCSV候補を作成します。DB登録は行いません。"

    def add_arguments(self, parser):
        parser.add_argument("pdf_path", help="変換元PDFファイルのパス")
        parser.add_argument("output_csv_path", help="出力CSVファイルのパス")

    def handle(self, *args, **options):
        pdf_path = Path(options["pdf_path"])
        output_csv_path = Path(options["output_csv_path"])

        if not pdf_path.exists():
            raise CommandError(f"PDFファイルが見つかりません: {pdf_path}")

        try:
            result = HospitalPDFToCSVService.convert_pdf_to_csv(
                pdf_path,
                output_csv_path,
            )
        except Exception as exc:
            raise CommandError(f"PDF変換に失敗しました: {exc}") from exc

        self.stdout.write(self.style.SUCCESS("PDFから病院マスタCSVへの変換結果"))
        self.stdout.write(f"出力先: {result['output_csv_path']}")
        self.stdout.write(f"出力件数: {result['exported']}")
        self.stdout.write(f"エラー件数: {len(result['errors'])}")

        if result["errors"]:
            self.stdout.write("エラー詳細:")
            for error in result["errors"]:
                self.stdout.write(f"  {error}")

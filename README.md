# Hospital CRM

Hospital CRM は、病院・法人・営業活動・営業分析を管理する Django アプリケーションです。

## テストデータ復元方法

マイグレーション適用後、以下のコマンドでサンプルデータを復元できます。

```powershell
.\.venv\Scripts\python.exe manage.py loaddata fixtures/sample_data.json
```

既存データがある環境では主キーの重複に注意してください。

## 病院マスタCSVインポート

テンプレート:

```text
import_templates/hospital_master_template.csv
```

実行:

```powershell
.\.venv\Scripts\python.exe manage.py import_hospitals_csv import_templates/hospital_master_template.csv
```

CSVは UTF-8 または UTF-8 BOM付きで保存してください。同名の法人がない場合は自動作成され、病院は `hospital_name + address`、次に `hospital_name` で既存データを判定して登録・更新します。

## Web画面からの病院マスタCSVインポート

URL:

```text
http://127.0.0.1:8001/importer/hospitals/csv/
```

テンプレート:

```text
import_templates/hospital_master_template.csv
```

## PDFから病院マスタCSVへの変換

PDFを直接DB登録するのではなく、まずCSVへ変換する。

```powershell
.\.venv\Scripts\python.exe manage.py convert_hospital_pdf_to_csv pdf_sources/sample.pdf converted_csv/hospital_from_pdf.csv
```

変換元PDFは `pdf_sources/`、変換後CSVは `converted_csv/` に配置します。これらのディレクトリ内の実データはGit管理対象外です。

# Hospital CRM

Hospital & Regional Collaboration Management

居宅介護支援事業所における病院営業・地域連携活動を支援するDjangoアプリケーション。

## Version

0.1

## Version 0.1 status

Released / 基盤機能完成

## 主な機能

- 病院マスタ管理
- 法人マスタ管理
- 営業履歴管理
- 紹介実績管理
- 営業分析
- PDF→CSV変換
- CSVレビュー
- ImportSession
- 差分確認
- 選択更新

## ドキュメント

docs/ 以下に設計書を配置。

主要ドキュメント:

- 00_開発規約.md
- 01_システム概要.md
- 02_システム構成.md
- 03_ER図.md
- 03.5_Djangoモデル設計.md
- 04_病院マスタ.md
- 05_法人マスタ.md
- 06_営業履歴.md
- 07_営業分析.md
- 08_AI設計.md
- 09_画面設計.md
- 10_インポート設計.md
- 11_運用設計.md
- 16_RELEASE_NOTE_v0.1.md
- 17_Version0.2運用設計.md
- 18_弱シグナル設計.md
- 19_実装ロードマップ.md

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

## 実PDFからCSVへの変換例

```powershell
.\.venv\Scripts\python.exe manage.py convert_hospital_pdf_to_csv ".\病院相談窓口一覧（令和8年6月改訂）.pdf" converted_csv/hospital_from_pdf.csv
```

## Web画面からのPDF→CSV変換

URL:

```text
http://127.0.0.1:8001/importer/hospitals/pdf/
```

流れ:

1. PDFをアップロード
2. CSVへ変換
3. `converted_csv/hospital_from_pdf.csv` を確認
4. 必要に応じて修正
5. CSVインポート画面から取り込む

## CSVインポート前レビュー

変換済みCSVをDB登録前に確認する。

URL:

```text
http://127.0.0.1:8001/importer/hospitals/csv/review/
```

対象CSV:

```text
converted_csv/hospital_from_pdf.csv
```

## Hospital CRM利用手順

PDFから病院マスタを登録する基本の流れ:

1. PDFをアップロード
2. CSVへ変換
3. CSVレビュー画面で登録予定・更新予定・エラーを確認
4. 「Hospitalマスタへ取り込む」でHospital登録

## インポート履歴・差分管理

ImportSession:
1回のインポート作業を管理する。

ImportRecord:
1病院ごとのインポート候補行を管理する。

一覧画面:

```text
http://127.0.0.1:8001/importer/sessions/
```

ImportSessionを使う運用手順:

1. PDFアップロード
2. CSV変換
3. CSVレビュー
4. ImportSession作成
5. ImportSession詳細画面で差分確認
6. 反映する行を選択
7. 選択更新でHospitalマスタへ反映

## 通常画面からの登録・編集・削除

Hospital CRMでは、Django Adminを使わずに以下を通常画面から管理できる。

- 病院
- 法人
- 担当者
- 訪問記録
- 紹介記録

削除は物理削除ではなく、`is_active=False` による論理削除とする。

# Hospital CRM Version 0.1 リリースノート

- リリース日: 2026-07-05
- バージョン: 0.1
- システム名: Hospital CRM
- 正式名称: Hospital & Regional Collaboration Management

## 概要

Hospital CRM Version 0.1 は、居宅介護支援事業所における病院営業・地域連携活動を支援するための基盤バージョンである。

病院情報、法人情報、営業履歴、紹介実績を管理し、PDFから病院マスタを構築できる仕組みを実装した。

## 実装済み機能

- 病院マスタ管理
- 法人マスタ管理
- 担当者管理
- 営業履歴管理
- 紹介実績管理
- 営業分析
- AnalyticsService
- 営業ランク表示
- ダッシュボード
- Bootstrap画面
- PDFアップロード
- PDF→CSV変換
- CSVレビュー
- CSVインポート
- ImportSession
- ImportRecord
- 差分確認
- 選択更新
- fixtureによるテストデータ共有

## Version 0.1 の到達点

PDFから病院マスタを作成し、レビュー・差分確認・選択更新を経てHospitalマスタへ反映できる。

## Version 0.1 の対象外

- 本格的なAI営業支援
- 弱シグナル自動分析
- PostgreSQL移行
- 複数ユーザー権限設計の詳細化
- API連携
- 本番クラウド運用

## 次期バージョン予定

Version 0.2 では、運用設計・差分管理・更新履歴・弱シグナル設計を強化する。

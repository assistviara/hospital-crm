# Hospital CRM

Hospital CRM は、病院・法人・営業活動・営業分析を管理する Django アプリケーションです。

## テストデータ復元方法

マイグレーション適用後、以下のコマンドでサンプルデータを復元できます。

```powershell
.\.venv\Scripts\python.exe manage.py loaddata fixtures/sample_data.json
```

既存データがある環境では主キーの重複に注意してください。

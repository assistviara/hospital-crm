from pathlib import Path

from django import forms


class HospitalCSVImportForm(forms.Form):
    csv_file = forms.FileField(label="CSVファイル")

    def clean_csv_file(self):
        csv_file = self.cleaned_data["csv_file"]

        if Path(csv_file.name).suffix.lower() != ".csv":
            raise forms.ValidationError("CSVファイルを選択してください。")

        if csv_file.size == 0:
            raise forms.ValidationError("空のCSVファイルはアップロードできません。")

        return csv_file

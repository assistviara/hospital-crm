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


class HospitalPDFConvertForm(forms.Form):
    pdf_file = forms.FileField(label="PDFファイル")

    def clean_pdf_file(self):
        pdf_file = self.cleaned_data["pdf_file"]

        if Path(pdf_file.name).suffix.lower() != ".pdf":
            raise forms.ValidationError("PDFファイルを選択してください。")

        if pdf_file.size == 0:
            raise forms.ValidationError("空のPDFファイルはアップロードできません。")

        return pdf_file

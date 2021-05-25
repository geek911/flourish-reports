from django import forms

from ..models import ExportFile

class ExportFileForm(forms.ModelForm):
    class Meta:
        model = ExportFile
        fields = '__all__'
from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit


class RecruitmentReportForm(forms.Form):

    start_date = forms.DateField(
        required=True, label='Start date')
    end_date = forms.DateField(
        required=True, label='End date')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'recruitment_report'
        self.helper.form_action = 'flourish_reports:home_url'
        self.helper.form_class = 'form-inline'
        self.helper.layout = Layout(
            'start_date',
            'end_date',
            Submit('submit', u'generate report', css_class="btn btn-sm btn-default"),
        )

from django import forms
from django.apps import apps as django_apps
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit


class RecruitmentReportForm(forms.Form):

    username = forms.ChoiceField(
        required=True, label='Username',
        widget=forms.Select())

    start_date = forms.DateField(
        required=True, label='Start date',
        widget=forms.TextInput(attrs={'type': 'date'}))
    end_date = forms.DateField(
        required=True, label='End date',
        widget=forms.TextInput(attrs={'type': 'date'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].choices = self.assign_users
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.form_id = 'recruitment_report'
        self.helper.form_action = 'flourish_reports:recruitment_report_url'
        self.helper.form_class = 'form-inline'
        self.helper.field_template = 'bootstrap3/layout/inline_field.html'
        self.helper.layout = Layout(
            'username',
            'start_date',
            'end_date',
            Submit('submit', u'filter report', css_class="btn btn-sm btn-default"),
            Submit('rdownload_report', u'download report', css_class="btn btn-sm btn-default"),
        )

    @property
    def assign_users(self):
        """Reurn a list of users that can be assigned an issue.
        """
        assignable_users_choices = (('-----', 'All'),)
        user = django_apps.get_model('auth.user')
        app_config = django_apps.get_app_config('flourish_reports')
        assignable_users_group = app_config.assignable_users_group
        try:
            Group.objects.get(name=assignable_users_group)
        except Group.DoesNotExist:
            Group.objects.create(name=assignable_users_group)
        assignable_users = user.objects.filter(
            groups__name=assignable_users_group)
        extra_choices = ()
        if app_config.extra_assignee_choices:
            for _, value in app_config.extra_assignee_choices.items():
                extra_choices += (value[0],)
        for assignable_user in assignable_users:
            username = assignable_user.username
            if not assignable_user.first_name:
                raise ValidationError(
                    f"The user {username} needs to set their first name.")
            if not assignable_user.last_name:
                raise ValidationError(
                    f"The user {username} needs to set their last name.")
            full_name = (f'{assignable_user.first_name} '
                         f'{assignable_user.last_name}')
            assignable_users_choices += ((username, full_name),)
        if extra_choices:
            assignable_users_choices += extra_choices
        return assignable_users_choices



class PrevStudyRecruitmentReportForm(forms.Form):

    prev_study = forms.ChoiceField(
        required=True, label='Prev Study',
        widget=forms.Select())

    start_date = forms.DateField(
        required=True, label='Start date',
        widget=forms.TextInput(attrs={'type': 'date'}))
    end_date = forms.DateField(
        required=True, label='End date',
        widget=forms.TextInput(attrs={'type': 'date'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['prev_study'].choices = self.prev_studies
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.form_id = 'recruitment_report'
        self.helper.form_action = 'flourish_reports:recruitment_report_url'
        self.helper.form_class = 'form-inline'
        self.helper.field_template = 'bootstrap3/layout/inline_field.html'
        self.helper.layout = Layout(
            'prev_study',
            'start_date',
            'end_date',
            Submit('submit', u'filter report', css_class="btn btn-sm btn-default"),
            Submit('rdownload_report', u'download report', css_class="btn btn-sm btn-default"),
        )

    @property
    def prev_studies(self):
        """Reurn a list of users that can be assigned an issue.
        """
        assignable_users_choices = (
            ('-----', 'All'),
            ('mashi', 'Mashi'),
            ('mmabana', 'Mma Bana'),
            ('mpepu', 'Mpepu'),
            ('tshipidi', 'Tshipidi'),
            ('tshilo dikotla', 'Tshilo Dikotla'),)
        return assignable_users_choices

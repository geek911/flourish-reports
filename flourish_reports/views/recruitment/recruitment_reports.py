from django.shortcuts import render
from django_pandas.io import read_frame
import pandas as pd

from django.contrib.auth.decorators import login_required
from django.urls.base import reverse
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from edc_base.view_mixins import EdcBaseViewMixin
from edc_navbar import NavbarViewMixin

from flourish_follow.models import LogEntry
from ...forms import PrevStudyRecruitmentReportForm, RecruitmentReportForm
from ...models import ExportFile
from ..view_mixins import DownloadReportMixin
from .user_recruitment_report_mixin import UserRecruitmentReportMixin
from .prev_study_recruitment_report import PrevStudyRecruitmentReportMixin
from django.contrib.auth.mixins import LoginRequiredMixin


class RecruitmentReportView(
    DownloadReportMixin, UserRecruitmentReportMixin,
    PrevStudyRecruitmentReportMixin, EdcBaseViewMixin,
    NavbarViewMixin, TemplateView, FormView, LoginRequiredMixin):
    form_class = RecruitmentReportForm
    template_name = 'flourish_reports/recruitment_reports.html'
    navbar_name = 'flourish_reports'
    navbar_selected_item = 'flourish_reports'

    def get_success_url(self):
        return reverse('flourish_reports:recruitment_report_url')

    def form_valid(self, form):
        prev_study_form = PrevStudyRecruitmentReportForm()
        if form.is_valid():
            username = form.data['username']
            start_date = form.data['start_date']
            end_date = form.data['end_date']

            recruitment = self.recruitment(
                username=username,
                start_date=start_date, end_date=end_date)
            totals = [['Totals'] + recruitment[0]]
            data = recruitment[1] + totals
            if 'rdownload_report' in self.request.POST:
                report_data = self.recruitment(username=username, start_date=start_date, end_date=end_date)
                report_data = report_data[1] + [['Totals'] + report_data[0]]
                columns = [
                    'Staff Member',
                    'Total Contacted',
                    'Total Successful Calls',
                    'Total Unsuccessful Calls',
                    'Total Participants Accepting',
                    'Conversion',
                    'Conversion %',
                ]
                self.download_data(
                    description='Recruitment Productivity Report',
                    start_date=start_date, end_date=end_date,
                    report_type='recruitment_productivity_reports',
                    df=pd.DataFrame(report_data, columns=columns))
            recruitment_downloads = ExportFile.objects.filter(
                description='recruitment_productivity_reports').order_by('uploaded_at')
            study_downloads = ExportFile.objects.filter(
                description='study_productivity_reports').order_by('uploaded_at')

            context = self.get_context_data(**self.kwargs)
            context.update(
                recruitment_downloads=recruitment_downloads,
                study_downloads=study_downloads,
                form=form,
                prev_study_form=prev_study_form,
                recruitment=recruitment)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recruitment_downloads = ExportFile.objects.filter(
            description='recruitment_productivity_reports').order_by('uploaded_at')
        study_downloads = ExportFile.objects.filter(
            description='study_productivity_reports').order_by('uploaded_at')
        # Recruitment report
        recruitment = self.recruitment()

        prev_study_form = PrevStudyRecruitmentReportForm()
        prev_study_report = self.prev_report_data()
        if self.request.method == 'POST':
            prev_study_form = PrevStudyRecruitmentReportForm(self.request.POST)
            if prev_study_form.is_valid():
                prev_study = prev_study_form.data['prev_study']
                start_date = prev_study_form.data['start_date']
                end_date = prev_study_form.data['end_date']
                prev_study_report = self.prev_report_data(
                    prev_study=prev_study,
                    start_date=start_date,
                    end_date=end_date)
                if 'rdownload_report' in self.request.POST:

                    columns = [
                        'Previous Study',
                        'Attempts',
                        'Pending',
                        'Unable To Reach',
                        'Decline/Uninterested',
                        'Thinking',
                        'Consented',
                    ]

                    self.download_data(
                        description='Study Productivity Report',
                        start_date=start_date, end_date=end_date,
                        report_type='study_productivity_reports',
                        df=pd.DataFrame(prev_study_report, columns=columns))
        context.update(
            recruitment_downloads=recruitment_downloads,
            study_downloads=study_downloads,
            recruitment=recruitment,
            prev_study_report=prev_study_report,
            prev_study_form=prev_study_form)
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

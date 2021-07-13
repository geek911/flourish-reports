from django.apps import apps as django_apps
from django_pandas.io import read_frame
from django.utils.safestring import mark_safe

import pandas as pd

from django.contrib.auth.decorators import login_required
from django.urls.base import reverse
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from edc_base.view_mixins import EdcBaseViewMixin
from edc_navbar import NavbarViewMixin

from ...forms import MissingCRFReportForm
from ...models import ExportFile

from ..view_mixins import DownloadReportMixin


class MissingCRFsReportView(
        DownloadReportMixin,
        EdcBaseViewMixin, NavbarViewMixin,
        TemplateView, FormView):

    form_class = MissingCRFReportForm
    template_name = 'flourish_reports/missing_crfs_report.html'
    navbar_name = 'flourish_reports'
    navbar_selected_item = 'missing_crfs_reports'
    registered_subject_cls = django_apps.get_model('edc_registration.registeredsubject')

    def subject_crfs_missing(self, start_date=None, end_date=None):
        crfmetadata = django_apps.get_model('edc_metadata.crfmetadata')
        if start_date and end_date:
            registered_identifiers = self.registered_subject_cls.objects.filter(
                created__date__gte=start_date,
                created__date__lte=end_date).values_list(
                    'subject_identifier', flat=True)
        else:
            registered_identifiers = self.registered_subject_cls.objects.all(
                ).values_list('subject_identifier', flat=True)
        required_crfs = crfmetadata.objects.filter(
            subject_identifier__in=registered_identifiers, entry_status='REQUIRED')
        data = [(qs.subject_identifier, qs.schedule_name, qs.visit_code,
                 qs.visit_code_sequence, qs.verbose_name) for qs in required_crfs]
        df = pd.DataFrame.from_records(
            data,
            columns=['Subject Identifier', 'Schedule Name', 'Visit Code', 'Timepoint', 'CRF name'])
        if not df.empty:
            grouped = df.groupby(['Subject Identifier', 'Schedule Name',
                                  'Visit Code', 'Timepoint'])
            return grouped['CRF name'].apply(
                lambda group_series: group_series.tolist()).reset_index()
        return df

    def get_success_url(self):
        return reverse('flourish_reports:missing_crfs_report_url')

    def form_valid(self, form):
        if form.is_valid():
            start_date = form.data['start_date']
            end_date = form.data['end_date']
            subject_crfs_missing = self.subject_crfs_missing(
                start_date=start_date,
                end_date=end_date)
            if 'rdownload_report' in self.request.POST:
                self.download_data(
                    description='Missing CRFs Report',
                    start_date=start_date, end_date=end_date,
                    report_type='missing_crfs_reports',
                    df=pd.DataFrame(subject_crfs_missing))

            subject_crfs_missing = self.df_to_html(subject_crfs_missing)

            context = self.get_context_data(**self.kwargs)
            context.update(
                subject_crfs_missing=mark_safe(subject_crfs_missing),
                form=form)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Report
        subject_crfs_missing = self.subject_crfs_missing()
        subject_crfs_missing = self.df_to_html(subject_crfs_missing)

        missing_crfs_file = ExportFile.objects.filter(
            description='Missing CRFs Report').latest('created')

        context.update(
            subject_crfs_missing=mark_safe(subject_crfs_missing),
            missing_crfs_file=missing_crfs_file)
        return context

    def df_to_html(self, df=None):
        groups_html = 'No missing CRFs'
        if not df.empty:
            groups_html = df.to_html()
            groups_html = groups_html.replace(
                '<table border="1" class="dataframe">',
                '<table id="missing-crfs" class="table table-striped table-bordered"'
                'cellspacing="0" width="100%">')
        return groups_html

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

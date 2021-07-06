from collections import Counter

from django_pandas.io import read_frame
from django.db.models import Q

import pandas as pd


from django.contrib.auth.decorators import login_required
from django.urls.base import reverse
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from edc_base.view_mixins import EdcBaseViewMixin
from edc_navbar import NavbarViewMixin

from ...forms import EnrolmentReportForm
from ...models import ExportFile

from ..view_mixins import DownloadReportMixin

from flourish_follow.models import LogEntry
from flourish_caregiver.models import CaregiverChildConsent    


class EnrolmentReportMixin:


    def cohort_report(self, start_date=None, end_date=None):
        """Return a total enrolment per cohort.
        """
        if start_date and end_date:
            consents = CaregiverChildConsent.objects.filter(
                created__date__gte=start_date,
                created__date__lte=end_date).values_list(
                    'cohort', flat=True)
        else:
            consents = CaregiverChildConsent.objects.all().values_list(
                    'cohort', flat=True)
        cohorts = Counter(consents)
        report = {}
        c_dict = {
            'cohort_a': 'Cohort A',
            'cohort_b': 'Cohort B',
            'cohort_c': 'Cohort C',
            'cohort_a_sec': 'Cohort A Secondary Aims',
            'cohort_b_sec': 'Cohort B Secondary Aims',
            'cohort_c_sec': 'Cohort C Secondary Aims',
            'cohort_pool': 'Cohort Pool'
            }
        for key, value in cohorts.items():
            new_key = c_dict[key]
            report[new_key] = value
        return sorted(report)

    def cohort_a(self, start_date=None, end_date=None):
        """Returns totals for cohort A.
        """
        cohort_a_dict = {
            'preg_woman': 1,
            'HEU': 3,
            'HUU': 1
            }
        return cohort_a_dict

    def cohort_b(self, start_date=None, end_date=None):
        """Returns totals for cohort A.
        """
        cohort_a_dict = {
            'EFV': 1,
            'DTG': 3,
            'HIV-Preg': 1
            }
        return cohort_a_dict

    def cohort_c(self, start_date=None, end_date=None):
        """Returns totals for cohort A.
        """
        cohort_a_dict = {
            'HUU': 1,
            'PI': 3,
            }
        return cohort_a_dict
    
    def sec_aims(self, start_date=None, end_date=None):
        """Returns totals for cohort A.
        """
        cohort_a_dict = {
            'WLHIV': 1,
            'HIV -': 1
            }
        return cohort_a_dict


class EnrolmentReportView(
        DownloadReportMixin, EnrolmentReportMixin,
        EdcBaseViewMixin, NavbarViewMixin,
        TemplateView, FormView):

    form_class = EnrolmentReportForm
    template_name = 'flourish_reports/enrolment_reports.html'
    navbar_name = 'flourish_reports'
    navbar_selected_item = 'enrolment_reports'

    def get_success_url(self):
        return reverse('flourish_reports:enrolment_report_url')

    def form_valid(self, form):
        if form.is_valid():
            start_date = form.data['start_date']
            end_date = form.data['end_date']
            data = []
            cohort_report = self.cohort_report(
                start_date=start_date,
                end_date=end_date)
            cohort_a = self.cohort_a(
                start_date=start_date,
                end_date=end_date)
            cohort_b = self.cohort_b(
                start_date=start_date,
                end_date=end_date)
            cohort_c = self.cohort_c(
                start_date=start_date,
                end_date=end_date)
            sec_aims = self.sec_aims(
                start_date=start_date,
                end_date=end_date)
            if 'rdownload_report' in self.request.POST:
                self.download_data(
                    description='Enrolment Report',
                    start_date=start_date, end_date=end_date,
                    report_type='enrolment_reports',
                    df=pd.DataFrame(data))
            enrolment_downloads = ExportFile.objects.filter(
                description='Enrolment Report').order_by('uploaded_at')
            context = self.get_context_data(**self.kwargs)
            context.update(
                enrolment_downloads=enrolment_downloads,
                cohort_report=cohort_report,
                cohort_a=cohort_a,
                cohort_b=cohort_b,
                cohort_c=cohort_c,
                sec_aims=sec_aims,
                form=form)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        enrolment_downloads = ExportFile.objects.filter(
            description='Enrolment Report').order_by('uploaded_at')
        
        # Enrolment report
        cohort_report = self.cohort_report()
        cohort_a = self.cohort_a()
        cohort_b = self.cohort_b()
        cohort_c = self.cohort_c()
        sec_aims = self.sec_aims()
        
        context.update(
            enrolment_downloads=enrolment_downloads,
            cohort_report=cohort_report,
            cohort_a=cohort_a,
            cohort_b=cohort_b,
            cohort_c=cohort_c,
            sec_aims=sec_aims)
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

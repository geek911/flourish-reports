from django.contrib.auth.decorators import login_required
from django.urls.base import reverse
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from edc_base.view_mixins import EdcBaseViewMixin
from edc_navbar import NavbarViewMixin
import pandas

from flourish_caregiver.models import *
from flourish_follow.models import LogEntry

from ...forms import EnrolmentReportForm
from ...models import ExportFile
from ..view_mixins import DownloadReportMixin
from .enrollment_report_mixin import EnrolmentReportMixin


class EnrolmentReportView(DownloadReportMixin, EnrolmentReportMixin,
                          EdcBaseViewMixin, NavbarViewMixin, TemplateView, FormView):
    form_class = EnrolmentReportForm
    template_name = 'flourish_reports/enrolment_reports.html'
    navbar_name = 'flourish_reports'
    navbar_selected_item = 'enrolment_reports'

    def get_success_url(self):
        return reverse('flourish_reports:enrolment_report_url')

    @property
    def cohort_category_pids(self):

        a_preg_df = pandas.DataFrame(
            set(self.cohort_a_category_pids.get('preg_woman_pids')),
            columns=['Cohort A: Preg Women (200)'])

        a_heu_df = pandas.DataFrame(
            set(self.cohort_a_category_pids.get('HEU_pids')),
            columns=['Cohort A: HEU (450)'])

        a_huu_df = pandas.DataFrame(
            set(self.cohort_a_category_pids.get('HUU_pids')),
            columns=['Cohort A: HUU (325)'])

        b_huu_df = pandas.DataFrame(
            set(list(self.cohort_b_category_pids.get('HUU'))),
            columns=['Cohort B: HUU (100)'])

        b_heu_df = pandas.DataFrame(
            set(list(self.cohort_b_category_pids.get('HEU 3-drug ART'))),
            columns=['Cohort B: HEU 3-drug ART (200)'])

        c_huu_df = pandas.DataFrame(
            set(list(self.cohort_c_category_pids.get('HUU'))),
            columns=['Cohort C: HUU (200)'])

        c_heu_df = pandas.DataFrame(
            set(list(self.cohort_c_category_pids.get('HEU 3-drug ART'))),
            columns=['Cohort C:  HEU 3-drug ART (100)'])

        sec_pos_preg_df = pandas.DataFrame(
            set(list(self.sec_aims_category_pids.get('WLHIV'))),
            columns=['Secondary Aims: Women Living With HIV'])

        sec_pos_neg_df = pandas.DataFrame(
            set(list(self.sec_aims_category_pids.get('HIV -'))),
            columns=['Secondary Aims: Women Living Without HIV'])

        frames = [a_preg_df, a_heu_df, a_huu_df,
                  b_huu_df, b_heu_df, c_huu_df, c_heu_df, sec_pos_preg_df,
                  sec_pos_neg_df]

        pids_df = pandas.concat(frames, axis=1)

        return pids_df

    def form_valid(self, form):

        if form.is_valid():

            start_date = form.data['start_date']
            end_date = form.data['end_date']

            cohort_report = self.all_cohort_report(
                start_date=start_date,
                end_date=end_date)

            df1 = pandas.DataFrame(list(cohort_report.items()),
                                   columns=['Cohort Enrollments', 'Qty'])

            cohort_a = self.cohort_a(
            )

            df2 = pandas.DataFrame(list(cohort_a.items()), columns=['Cohort A', 'Qty'])

            cohort_b = self.cohort_b(
                start_date=start_date,
                end_date=end_date)
            df3 = pandas.DataFrame(list(cohort_b.items()), columns=['Cohort B', 'Qty'])

            cohort_c = self.cohort_c(
                start_date=start_date,
                end_date=end_date)
            df4 = pandas.DataFrame(list(cohort_c.items()), columns=['Cohort C', 'Qty'])

            sec_aims = self.sec_aims(
                start_date=start_date,
                end_date=end_date)
            df5 = pandas.DataFrame(list(sec_aims.items()),
                                   columns=['Secondary Aims', 'Qty'])

            df = [df1, df2, df3, df4, df5]

            if 'rdownload_report' in self.request.POST:
                data = [
                    {"All Cohort Reports": cohort_report.values()},
                    {"Cohort A": [value for value in cohort_a.values()]},
                    {"Cohort B": [value for value in cohort_b.values()]},
                    {"Cohort C": [value for value in cohort_c.values()]},
                    {"Secondary Aims": [value for value in sec_aims.values()]},
                ]

                self.download_data(
                    description='Cohort Report',
                    start_date=start_date, end_date=end_date,
                    report_type='enrolment_reports',
                    df=df)

                self.download_data(
                    description='Cohort Report Cohort Breakdown',
                    start_date=start_date, end_date=end_date,
                    report_type='enrolment_reports',
                    df=self.cohort_category_pids)

            enrolment_downloads = ExportFile.objects.filter(
                description='enrolment_reports').order_by('uploaded_at')

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
            description='enrolment_reports').order_by('uploaded_at')

        # Enrolment report
        cohort_a = self.cohort_a
        cohort_b = self.cohort_b
        cohort_c = self.cohort_c
        sec_aims = self.sec_aims()

        context.update(
            enrolment_downloads=enrolment_downloads,
            cohort_report=self.all_cohort_report(),
            generate_enrolment_cohort_breakdown=self.generate_enrolment_cohort_breakdown,
            generate_current_cohort_breakdown=self.generate_current_cohort_breakdown,
            cohort_a=cohort_a,
            cohort_b=cohort_b,
            cohort_c=cohort_c,
            sec_aims=sec_aims, )
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

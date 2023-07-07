from django.contrib.auth.decorators import login_required
from django.urls.base import reverse
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from edc_base.view_mixins import EdcBaseViewMixin
from edc_navbar import NavbarViewMixin

from .enrollment_report_mixin import EnrolmentReportMixin
from ..view_mixins import DownloadReportMixin
from ...forms import EnrolmentReportForm
from ...models import ExportFile


class EnrolmentReportView(DownloadReportMixin, EnrolmentReportMixin,
                          EdcBaseViewMixin, NavbarViewMixin, TemplateView, FormView):
    form_class = EnrolmentReportForm
    template_name = 'flourish_reports/enrolment_reports.html'
    navbar_name = 'flourish_reports'
    navbar_selected_item = 'enrolment_reports'

    def get_success_url(self):
        return reverse('flourish_reports:enrolment_report_url')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        enrolment_downloads = ExportFile.objects.filter(
            description='enrolment_reports').order_by('uploaded_at')

        cohort_a = self.current_exposure_summary.get('Cohort A')
        cohort_b = self.current_exposure_summary.get('Cohort B')
        cohort_c = self.current_exposure_summary.get('Cohort C')

        context.update(
            enrolment_downloads=enrolment_downloads,
            cohort_report=self.all_cohort_report(),
            cohort_a=dict(cohort_a),
            cohort_b=dict(cohort_b),
            cohort_c=dict(cohort_c),
            enrolment_exposure_summary=self.enrolment_exposure_summary,
            current_exposure_summary=self.current_exposure_summary,
        )
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

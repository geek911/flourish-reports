from collections import defaultdict

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
        return

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_report = self.current_report
        enrollment_report = self.enrollment_report
        get_enrolment_total = self.get_enrolment_total
        get_sequence = self.get_sequence
        get_sequence = self.convert_to_regular_dict(get_sequence)
        context.update(
            current_report=current_report,
            enrollment_report=enrollment_report,
            get_enrolment_total=get_enrolment_total,
            get_sequence=get_sequence,
        )
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def convert_to_regular_dict(self, d):
        if isinstance(d, defaultdict):
            d = {k: self.convert_to_regular_dict(v) for k, v in d.items()}
        return d

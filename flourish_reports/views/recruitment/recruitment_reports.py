from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls.base import reverse
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from edc_base.view_mixins import EdcBaseViewMixin
from edc_navbar import NavbarViewMixin


from ...classes import RecruitmentReport


class RecruitmentReportView(EdcBaseViewMixin,
                            NavbarViewMixin, TemplateView, LoginRequiredMixin):

    template_name = 'flourish_reports/recruit/recruitment_reports.html'
    navbar_name = 'flourish_reports'
    navbar_selected_item = 'flourish_reports'

    def get_success_url(self):
        return reverse('flourish_reports:recruitment_report_url')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        reports = RecruitmentReport()

        context.update(
            prev_study_data=reports.caregiver_prev_study_dataset())
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

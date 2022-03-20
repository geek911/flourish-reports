from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls.base import reverse
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from edc_base.view_mixins import EdcBaseViewMixin
from edc_navbar import NavbarViewMixin

from ...classes import RecruitmentReport
from ...classes.recruitment_reports_classs import PieTotals


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

        reports.attemps_report_data()

        prev_study_data, pie = reports.caregiver_prev_study_dataset()

        attempts_prev_studies = [
            'Previous Study',
            'Total Study Participants',
            'Total Attempts',
            'Total not attempted']
        declined_data, total_decline = reports.declined()
        consented_data, total_consented = reports.consented()
        participants_not_reachable, total_participants_not_reachable = reports.participants_not_reachable()
        participants_to_call_again, total_participants_to_call_again = reports.participants_to_call_again()

        summary_pie = PieTotals(
            total_continued_contact=total_participants_to_call_again,
            total_consented=total_consented,
            total_unable_to_reach=total_participants_not_reachable,
            total_decline_uninterested=total_decline)
        attempts_data, total_attempts, not_attempted = reports.attemps_report_data()
        context.update(
            previous_studies=reports.previous_studies,
            prev_study_data=prev_study_data,
            locator_report=reports.locator_report(),
            pie_chart=pie,
            worklist_report=reports.worklist_report(),
            attempts_prev_studies=attempts_prev_studies,
            attempts_data=attempts_data,
            total_attempts=total_attempts,
            not_attempted=not_attempted,
            participants_to_call_again=participants_to_call_again,
            participants_not_reachable=participants_not_reachable,
            declined=declined_data,
            consented=consented_data,
            summary_pie=summary_pie
        )
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

# TODO test again


from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.view_mixins import ListboardFilterViewMixin, SearchFormViewMixin
from edc_dashboard.views import ListboardView
from edc_navbar import NavbarViewMixin
from ...model_wrappers import MaternalVisitModelWrapper
from edc_appointment.constants import COMPLETE_APPT

class MissingCrfReportView(EdcBaseViewMixin, NavbarViewMixin,
                           ListboardFilterViewMixin,
                           ListboardView):
    listboard_template = 'missing_crf_report_template'
    listboard_url = 'missing_crf_report_url'
    listboard_panel_style = 'success'
    listboard_fa_icon = "far fa-user-circle"

    model = 'flourish_caregiver.maternalvisit'
    model_wrapper_cls = MaternalVisitModelWrapper

    navbar_name = 'flourish_reports'
    navbar_selected_item = 'missing_crfs_reports'

    def get_queryset(self):
        return super().get_queryset().filter(
            appointment__appt_status=COMPLETE_APPT)

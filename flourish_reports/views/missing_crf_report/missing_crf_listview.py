from django.apps import apps as django_apps
from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.view_mixins import ListboardFilterViewMixin, SearchFormViewMixin
from edc_dashboard.views import ListboardView
from edc_navbar import NavbarViewMixin
from ...model_wrappers import CaregiverAppointmentModelWrapper


class MissingCrfListView(EdcBaseViewMixin,
                         NavbarViewMixin,
                         ListboardFilterViewMixin,
                         ListboardView):
    listboard_template = 'missing_crf_listboard_template'
    listboard_url = 'missing_crf_report_url'
    listboard_panel_style = 'success'
    listboard_fa_icon = "far fa-user-circle"

    model = 'edc_appointment.appointment'
    model_wrapper_cls = CaregiverAppointmentModelWrapper
    navbar_name = 'flourish_reports'
    navbar_selected_item = 'missing_crf_report'

    maternal_visit_model = 'flourish_caregiver.maternalvisit'

    @property
    def maternal_visit_cls(self):
        return django_apps.get_model(self.maternal_visit_model)

    def get_queryset(self):

        subject_identifiers = self.maternal_visit_cls.objects.values_list(
            'subject_identifier', flat=True)

        return super().get_queryset().filter(subject_identifier__in=subject_identifiers)

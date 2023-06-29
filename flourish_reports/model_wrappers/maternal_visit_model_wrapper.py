
from django.conf import settings
from edc_model_wrapper.wrappers import ModelWrapper
from edc_visit_schedule import site_visit_schedules
from django.apps import apps as django_apps
from ..views.missing_crf_report.missing_crf_data_statistics import MissingCRFDataStatistics

class MaternalVisitModelWrapper(ModelWrapper):
    model = 'flourish_caregiver.maternalvisit'
    next_url_name = settings.DASHBOARD_URL_NAMES.get('subject_dashboard_url')
    next_url_attrs = ['subject_identifier', 'appointment']

    @property
    def statistics(self):

        stats = MissingCRFDataStatistics()
        stats.visit_object = self.object

        return stats

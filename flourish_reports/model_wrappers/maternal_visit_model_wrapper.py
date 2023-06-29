
from django.conf import settings
from edc_model_wrapper.wrappers import ModelWrapper
from edc_visit_schedule import site_visit_schedules
from django.apps import apps as django_apps
from ..views.missing_crf_report.missing_crf_data_statistics import MissingCRFDataStatistics
from dateutil.relativedelta import relativedelta
class MaternalVisitModelWrapper(ModelWrapper):
    model = 'flourish_caregiver.maternalvisit'
    next_url_name = settings.DASHBOARD_URL_NAMES.get('subject_dashboard_url')
    next_url_attrs = ['subject_identifier', 'appointment']

    @property
    def statistics(self):

        stats = MissingCRFDataStatistics()
        stats.visit_object = self.object

        return stats
    
    @property
    def timepoints(self):
        datetime_open = self.object.appointment.appt_datetime
        datetime_close = datetime_open + relativedelta(months=3)
        return f'{datetime_open.strftime("%Y-%m-%d")} to {datetime_close.strftime("%Y-%m-%d")}'


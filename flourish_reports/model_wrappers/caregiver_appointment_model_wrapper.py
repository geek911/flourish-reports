
from django.conf import settings
from edc_model_wrapper.wrappers import ModelWrapper
from edc_visit_schedule import site_visit_schedules
from django.apps import apps as django_apps
from dateutil.relativedelta import relativedelta

class CaregiverAppointmentModelWrapper(ModelWrapper):
    model = 'edc_appointment.appointment'
    next_url_name = settings.DASHBOARD_URL_NAMES.get('subject_dashboard_url')
    next_url_attrs = ['subject_identifier', 'appointment']

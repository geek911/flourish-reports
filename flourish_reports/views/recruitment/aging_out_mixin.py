from django.apps import apps as django_apps
from edc_base.utils import age
from flourish_caregiver.models.signals import cohort_assigned
from datetime import datetime, timedelta


class AgingOutMixin:

    caregiver_child_consent_model = 'flourish_caregiver.caregiverchildconsent'
    subject_schedule_history_model = 'edc_visit_schedule.subjectschedulehistory'
    child_appointment_model = 'flourish_child.appointment'

    @property
    def caregiver_child_consent_cls(self):
        return django_apps.get_model(self.caregiver_child_consent_model)

    @property
    def child_appointment_cls(self):
        return django_apps.get_model(self.child_appointment_model)

    def get_dates_of_week(self):
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        dates_of_week = [week_start + timedelta(days=i) for i in range(7)]
        return dates_of_week

    def evaluated_cohort(self, consent):
        return cohort_assigned(
            study_child_identifier=consent.study_child_identifier,
            child_dob=consent.child_dob,
            enrollment_date=consent.consent_datetime.date())

    def current_latest_schedule(self, subject_identifier):
        latest_appointment = self.child_appointment_cls.objects.filter(
            subject_identifier=subject_identifier
        ).latest('appt_datetime')

        return latest_appointment

    def get_cohort(self, schedule_name):
        cohort_name = None

        if 'child_a' in schedule_name:
            cohort_name = 'cohort_a'
        elif 'child_b' in schedule_name:
            cohort_name = 'cohort_b'
        elif 'child_c' in schedule_name:
            cohort_name = 'cohort_c'

        return f'{cohort_name}_sec' if 'sec' in schedule_name else cohort_name

    @property
    def child_consents_objs(self):

        consents = self.caregiver_child_consent_cls.objects.filter(
            study_child_identifier__isnull=False)

        return consents

    @property
    def ageing_out_statistics(self):

        statistics = []

        for consent in self.child_consents_objs:

            appt = self.current_latest_schedule(consent.subject_identifier)
            current_cohort = self.get_cohort(appt.schedule_name)

            for day in self.get_dates_of_week():
                age_in_years = age(consent.child_dob, day).years
                singular_stat = [day.strftime("%a %d %b %Y"), []]

                if (5 < age_in_years <= 10 and current_cohort == 'cohort_a') or \
                   (age_in_years > 10 and current_cohort == 'cohort_b'):

                    if consent.subject_identifier in singular_stat[1]:
                        continue

                    singular_stat[1].append(consent.subject_identifier)

                if singular_stat[1]:
                    statistics.append(singular_stat)

        return statistics

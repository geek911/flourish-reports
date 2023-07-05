from django.apps import apps as django_apps
from edc_base.utils import age
from flourish_caregiver.models.signals import cohort_assigned
from datetime import datetime, timedelta
from django.db.models.functions import Length


class AgingOutMixin:

    caregiver_child_consent_model = 'flourish_caregiver.caregiverchildconsent'
    subject_schedule_history_model = 'edc_visit_schedule.subjectschedulehistory'
    child_appointment_model = 'flourish_child.appointment'
    edc_registered_model = 'edc_registration.registeredsubject'
    child_dataset_model = 'flourish_child.childdataset'

    @property
    def caregiver_child_consent_cls(self):
        return django_apps.get_model(self.caregiver_child_consent_model)

    @property
    def child_dataset_cls(self):
        return django_apps.get_model(self.child_dataset_model)

    @property
    def child_appointment_cls(self):
        return django_apps.get_model(self.child_appointment_model)

    @property
    def edc_registered_cls(self):
        return django_apps.get_model(self.edc_registered_model)

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
    def subject_identifiers(self):
        subject_identifiers = self.caregiver_child_consent_cls.objects.filter(
            study_child_identifier__isnull=False
        ).values_list('subject_identifier', flat=True)

        return set(subject_identifiers)

    @property
    def ageing_out_statistics(self):

        statistics = list()
        included = set()
        for subject_identifier in self.subject_identifiers:

            try:

                registered_subject = self.edc_registered_cls.objects.filter(
                    subject_identifier=subject_identifier,
                    dob__isnull=False
                ).latest('consent_datetime')

            except self.edc_registered_cls.DoesNotExist:
                pass
            else:

              

                appt = self.current_latest_schedule(registered_subject.subject_identifier)
                current_cohort = self.get_cohort(appt.schedule_name)

                for day in self.get_dates_of_week():
                    age_in_years = age(registered_subject.dob, day).years
                    singular_stat = [day.strftime("%a %d %b %Y"), []]

                    if (5 < age_in_years <= 10 and current_cohort == 'cohort_a') or \
                            (age_in_years > 10 and current_cohort == 'cohort_b'):

                        if subject_identifier in included:
                            continue
                        else:
                            singular_stat[1].append(registered_subject.subject_identifier)
                            singular_stat[1].append(age_in_years)
                            included.add(subject_identifier)

        


                    if singular_stat[1]:
                        statistics.append(singular_stat)

        return statistics

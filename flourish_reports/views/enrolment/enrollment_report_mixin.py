import re
from collections import defaultdict

from django.apps import apps as django_apps
from django.db.models import Max


def convert_to_snake_case(string):
    snake_case_string = re.sub(r'\s', '_', string.lower())
    return snake_case_string


def convert_to_title_case(snake_case_string):
    title_case_string = snake_case_string.replace("_", " ").title()
    return title_case_string


class EnrolmentReportMixin:
    child_consents_cls = django_apps.get_model('flourish_caregiver.caregiverchildconsent')
    maternal_dataset_cls = django_apps.get_model('flourish_caregiver.maternaldataset')
    cohort_cls = django_apps.get_model('flourish_caregiver.cohort')
    child_dataset_cls = django_apps.get_model('flourish_child.childdataset')
    child_birth_cls = django_apps.get_model('flourish_child.childbirth')
    ante_enrol_cls = django_apps.get_model('flourish_caregiver.antenatalenrollment')

    @property
    def participants_cohort(self):
        return self.cohort_cls.objects.all()

    @property
    def latest_cohort_objs(self):
        latest_cohort_objs_ids = self.participants_cohort.values(
            'subject_identifier').annotate(latest_report_date=Max(
            'assign_datetime')).values_list('id', flat=True)

        return self.participants_cohort.filter(id__in=latest_cohort_objs_ids)

    @property
    def child_consent_objs(self):
        return self.child_consents_cls.objects.all()

    @property
    def child_birth_objs(self):
        return self.child_birth_cls.objects.all()

    def get_enrolment_by_cohort(self, cohort, enrollment_cohort=True):
        return self.participants_cohort.filter(
            name=cohort, enrollment_cohort=enrollment_cohort).values_list(
            'subject_identifier', flat=True)

    def get_current_by_cohort(self, cohort):
        enrolment_cohort = self.latest_cohort_objs.filter(
            name=cohort).values_list('subject_identifier', flat=True)
        return set(list(enrolment_cohort))

    def get_seq_by_cohort(self, enrol_cohort, seq_cohort):
        enrolment_cohort = self.get_enrolment_by_cohort(enrol_cohort)
        seq_by_cohort = []
        for participant in enrolment_cohort:
            participants_cohort = self.participants_cohort.filter(
                subject_identifier=participant, name=seq_cohort)
            if participants_cohort.exists():
                seq_by_cohort.append(participant)

        return set(list(seq_by_cohort))

    def all_cohort_report(self, start_date=None, end_date=None):
        """Return a total enrolment per cohort.
        """
        table = {
            'Cohort A': ['enrollment', 'cohort_b', 'cohort_b_sec', 'cohort_c',
                         'cohort_c_sec'],
            'Cohort B': ['enrollment', 'cohort_b', 'cohort_b_sec', 'cohort_c',
                         'cohort_c_sec'],
            'Cohort C': ['enrollment', 'cohort_b', 'cohort_b_sec', 'cohort_c',
                         'cohort_c_sec'],
            'Cohort A Sec': ['enrollment', 'cohort_b', 'cohort_b_sec', 'cohort_c',
                             'cohort_c_sec'],
            'Cohort B Sec': ['enrollment', 'cohort_b', 'cohort_b_sec', 'cohort_c',
                             'cohort_c_sec'],
            'Cohort C Sec': ['enrollment', 'cohort_b', 'cohort_b_sec', 'cohort_c',
                             'cohort_c_sec'],
        }
        cohort_report = {}
        for cohort, values in table.items():
            cohort_to_snake_case = convert_to_snake_case(cohort)
            cohort_report[cohort] = {'enrollment': self.get_enrolment_by_cohort(
                cohort_to_snake_case).count()}
            for value in values[1:]:
                if value == cohort_to_snake_case or cohort_to_snake_case in value or \
                        value in cohort_to_snake_case:
                    cohort_report[cohort][value] = 0
                    continue
                cohort_report[cohort][value] = len(self.get_seq_by_cohort(
                    enrol_cohort=cohort_to_snake_case, seq_cohort=value))
        return cohort_report

    @property
    def enrolment_exposure_summary(self):
        cohorts = ['cohort_a', 'cohort_b', 'cohort_c', 'cohort_a_sec', 'cohort_b_sec',
                   'cohort_c_sec']
        enrolment_exposure_summary = defaultdict(lambda: defaultdict(int))

        for cohort in cohorts:
            participants = self.get_enrolment_by_cohort(cohort=cohort)
            cohort_name = convert_to_title_case(cohort)
            for participant in participants:
                exposure = self.check_exposure(participant)
                enrolment_exposure_summary[cohort_name][exposure] += 1
                if participant[:-3] in self.heu_art_3drug_combination:
                    enrolment_exposure_summary[cohort_name]['3drug'] += 1
        return enrolment_exposure_summary

    @property
    def current_exposure_summary(self):
        current_exposure_summary = defaultdict(lambda: defaultdict(int))

        participants = self.child_consent_objs.only('subject_identifier').values_list(
            'subject_identifier', flat=True)
        for participant in set(list(participants)):
            try:
                latest_obj = self.participants_cohort.filter(
                    subject_identifier=participant).latest('assign_datetime')
            except self.cohort_cls.DoesNotExist:
                continue
            else:
                exposure = self.check_exposure(participant)
                cohort_name = convert_to_title_case(latest_obj.name)
                current_exposure_summary[cohort_name][exposure] += 1
                if participant[:-3] in self.heu_art_3drug_combination:
                    current_exposure_summary[cohort_name]['3drug'] += 1
        return current_exposure_summary

    def check_exposure(self, participant):
        study_child_identifier = self.child_consent_objs.filter(
            subject_identifier=participant).only('study_child_identifier').latest(
            'consent_datetime').study_child_identifier
        if study_child_identifier in self.unexposed_participants:
            return 'Unexposed'
        elif study_child_identifier in self.exposed_participants:
            return 'Exposed'
        else:
            return 'ANC'

    @property
    def exposed_participants(self):
        exposed_values = ['Exposed', 'exposed']
        return self.child_dataset_cls.objects.filter(
            infant_hiv_exposed__in=exposed_values).values_list(
            'study_child_identifier', flat=True)

    @property
    def heu_art_3drug_combination(self):
        exposed_values = ['Exposed', 'exposed']
        exposed_participants = self.child_dataset_cls.objects.filter(
            infant_hiv_exposed__in=exposed_values).values_list(
            'study_maternal_identifier', flat=True)

        return self.maternal_dataset_cls.objects.filter(
            study_maternal_identifier__in=exposed_participants,
            mom_pregarv_strat='3-drug ART').values_list('subject_identifier', flat=True)

    @property
    def unexposed_participants(self):
        unexposed_values = ['Unexposed', 'unexposed']
        return self.child_dataset_cls.objects.filter(
            infant_hiv_exposed__in=unexposed_values).values_list(
            'study_child_identifier', flat=True)

from collections import defaultdict

from django.apps import apps as django_apps
from django.db.models import Max


def convert_to_title_case(snake_case_string):
    title_case_string = snake_case_string.replace("_", " ").title()
    return title_case_string


class EnrolmentReportMixin:
    cohort_cls = django_apps.get_model('flourish_caregiver.cohort')

    @property
    def participants_cohort(self):
        return self.cohort_cls.objects.all()

    def get_cohorts(self, enroll=False):
        if enroll:
            return self.participants_cohort.filter(enrollment_cohort=True)
        else:
            return self.participants_cohort.all()

    @property
    def get_sequence(self):
        participant_cohorts = defaultdict(list)
        all_cohorts = self.participants_cohort.order_by('assign_datetime')

        for cohort in all_cohorts:
            participant_cohorts[cohort.subject_identifier].append(cohort.name)

        movements = defaultdict(lambda: defaultdict(int))

        for cohorts in participant_cohorts.values():
            for i in range(1, len(cohorts)):
                # increment count of movement from previous_cohort to next_cohort
                movements[cohorts[i - 1]][cohorts[i]] += 1

        return movements

    def generate_report(self, enroll=False, schedule_status=False):
        cohorts = ['cohort_a', 'cohort_b', 'cohort_c', 'cohort_a_sec', 'cohort_b_sec',
                   'cohort_c_sec']

        report = []
        all_cohorts = self.get_cohorts(enroll)
        if schedule_status:
            all_cohorts = all_cohorts.filter(schedule_status=schedule_status)

        for cohort_name in cohorts:
            title_case_cohort_name = convert_to_title_case(cohort_name)
            exposed = all_cohorts.filter(
                name=cohort_name, exposure_status='EXPOSED').values_list(
                'subject_identifier', flat=True).distinct()
            unexposed = all_cohorts.filter(
                name=cohort_name, exposure_status='UNEXPOSED').values_list(
                'subject_identifier', flat=True).distinct()
            exposed = len(set(exposed))
            unexposed = len(set(unexposed))

            report.append(
                {'cohort_name': title_case_cohort_name, 'unexposed': unexposed,
                 'exposed': exposed})

        return report

    @property
    def current_report(self):
        return self.generate_report(enroll=False, schedule_status=True)

    @property
    def enrollment_report(self):
        return self.generate_report(enroll=True)

    @property
    def get_enrolment_total(self):
        enrolment_total = {}
        for cohort in self.enrollment_report:
            enrolment_total[cohort['cohort_name']] = cohort['unexposed'] + cohort[
                'exposed']
        return enrolment_total

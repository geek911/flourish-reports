from django_pandas.io import read_frame
from django.db.models import Q

from flourish_follow.models import LogEntry
from flourish_caregiver.models import (
    ScreeningPriorBhpParticipants, SubjectConsent)


class PrevStudyRecruitmentReportMixin:
    
    def attempts(self, pre_study=None, start_date=None, end_date=None):
        """Return number of contacted participants.
        """
        prev_studies = [
            'Mpepu',
            'Mma Bana',
            'Mashi',
            'Tshilo Dikotla',
            'Tshipidi']
        qs = LogEntry.objects.all()
        if pre_study:
            qs = LogEntry.objects.filter(
                pre_study=pre_study,
                created__date__gte=start_date,
                created__date__lte=end_date)
        elif pre_study == '-----':
            qs = LogEntry.objects.filter(
                created__date__gte=start_date,
                created__date__lte=end_date)
        df = read_frame(qs, fieldnames=['prev_study', 'study_maternal_identifier'])
        df = df.drop_duplicates(subset=['study_maternal_identifier'])
        prev_study_dict = {}
        for prev_study in prev_studies:
            df_prev = df[df['prev_study']==prev_study]
            prev_study_dict[prev_study] = df_prev[df_prev.columns[0]].count()
        return prev_study_dict

    def pending(self, username, start_date=None, end_date=None):
        """Returns number of successful calls.
        """
        successful = 0
        if start_date and end_date:
            successful = LogEntry.objects.filter(
                ~Q(phone_num_success='none_of_the_above'),
                user_created=username,
                created__date__gte=start_date,
                created__date__lte=end_date,
                phone_num_success__isnull=False).values_list(
                    'study_maternal_identifier').distinct().count()
        else:
            successful = LogEntry.objects.filter(
                ~Q(phone_num_success='none_of_the_above'),
                user_created=username,
                phone_num_success__isnull=False,).values_list(
                    'study_maternal_identifier').distinct().count()
        return successful

    def unsuccessful_calls(self, username, start_date=None, end_date=None):
        """Returns number of unsuccessful calls.
        """
        unsuccessful = 0
        if start_date and end_date:
            unsuccessful = LogEntry.objects.filter(
                user_created=username,
                created__date__gte=start_date,
                created__date__lte=end_date,
                phone_num_success__isnull=True,
                phone_num_success='none_of_the_above').values_list(
                    'study_maternal_identifier').distinct().count()
        else:
            unsuccessful = LogEntry.objects.filter(
                user_created=username,
                phone_num_success__isnull=True,
                phone_num_success='none_of_the_above').values_list(
                    'study_maternal_identifier').distinct().count()
        return unsuccessful

    def accepting_apps(self, username, start_date=None, end_date=None):
        """Returns a lost of participants accepting appointments.
        """
        accepting = 0
        if start_date and end_date:
            accepting = LogEntry.objects.filter(
                Q(appt_date__isnull=False) | Q(appt='Yes'),
                user_created=username,
                created__date__gte=start_date,
                created__date__lte=end_date,).values_list(
                    'study_maternal_identifier').distinct().count()
        else:
            accepting = LogEntry.objects.filter(
                Q(appt_date__isnull=False) | Q(appt='Yes'),
                user_created=username).values_list(
                    'study_maternal_identifier').distinct().count()
        return accepting
from functools import reduce

from django.db.models import Q
from edc_constants.constants import NO, YES

from django_pandas.io import read_frame
from flourish_caregiver.models import MaternalDataset, SubjectConsent, ScreeningPriorBhpParticipants
from flourish_follow.models import LogEntry, InPersonContactAttempt, WorkList, LogEntry
import pandas as pd


def merge(lst1, lst2):
    """Return merged list from 2 lists.
    """
    return [a + [b[1]] for (a, b) in zip(lst1, lst2)]


class PrevStudyRecruitmentReportMixin:

    prev_studies = [
            'Mpepu',
            'Mma Bana',
            'Mashi',
            'Tshilo Dikotla',
            'Tshipidi']

    def total_partici_onworklist(self, prev_study=None, start_date=None, end_date=None):

        qs = WorkList.objects.all()
        if prev_study:
            qs = qs.filter(
                    created__range=[start_date, end_date],)
            if prev_study != '-----':
                qs = qs.filter(
                    prev_study=prev_study)

        df = read_frame(qs, fieldnames=['prev_study', 'study_maternal_identifier'])

        df = df.drop_duplicates(subset=['study_maternal_identifier'])

        prev_study_list = []
        for prev_study in self.prev_studies:
            df_prev = df[df['prev_study'] == prev_study]
            prev_study_list.append([prev_study, df_prev[df_prev.columns[0]].count()])
        return prev_study_list

    def total_previous_study_participents(self, prev_study=None, start_date=None,
                                          end_date=None):

        qs = MaternalDataset.objects.all()
        if prev_study:
            qs = qs.filter(created__range=[start_date, end_date],)

            if prev_study != '-----':
                qs = qs.filter(protocol=prev_study)

        df = read_frame(qs, fieldnames=['study_maternal_identifier', 'protocol'])

        # df = df.drop_duplicates(subset=['study_maternal_identifier'])

        prev_study_list = []
        for prev_study in self.prev_studies:
            df_prev = df[df['protocol'] == prev_study]
            prev_study_list.append([prev_study, df_prev[df_prev.columns[0]].count()])
        return prev_study_list

    def cont_contact(self, prev_study=None, start_date=None, end_date=None):
        """Return number of contacted participants who are still being contacted.
        """

        screening_identifiers = SubjectConsent.objects.all().values_list(
            'screening_identifier', flat=True)
        screening_identifiers = list(set(screening_identifiers))

        consented_pids = MaternalDataset.objects.filter(
            screening_identifier__in=screening_identifiers).values_list(
                'study_maternal_identifier', flat=True)

        no_appt_pids = LogEntry.objects.filter(appt=NO).values_list(
            'study_maternal_identifier')

        qs = LogEntry.objects.filter(
            ~Q(study_maternal_identifier__in=no_appt_pids)
            & ~Q(study_maternal_identifier__in=consented_pids),
            ~Q(phone_num_success=['none_of_the_above']),
            appt__in=['thinking', YES])

        if prev_study:
            qs = qs.filter(
                    created__range=[start_date, end_date])

            if prev_study != '-----':
                qs = qs.filter(
                    created__range=[start_date, end_date])

        df = read_frame(qs, fieldnames=['prev_study', 'study_maternal_identifier'])
        df = df.drop_duplicates(subset=['study_maternal_identifier'])

        result = df
        result = result.drop_duplicates(subset=['study_maternal_identifier'])

        prev_study_list = []
        for prev_study in self.prev_studies:
            df_prev = result[result['prev_study'] == prev_study]
            prev_study_list.append([prev_study, df_prev[df_prev.columns[0]].count()])
        return prev_study_list

    def attempts(self, prev_study=None, start_date=None, end_date=None):
        """Return number of contacted participants.
        """

        worklist_qs = WorkList.objects.filter(
            is_called=True,
            assigned__isnull=False,
            called_datetime__isnull=False
        ).values_list('study_maternal_identifier')

        qs = LogEntry.objects.filter(
            study_maternal_identifier__in=worklist_qs,
        )

        if prev_study:
            if prev_study == '-----':

                worklist_qs = WorkList.objects.filter(
                    is_called=True,
                    assigned__isnull=False,
                    created__range=[start_date, end_date]
                ).values_list('study_maternal_identifier')

                qs = LogEntry.objects.filter(
                    study_maternal_identifier__in=worklist_qs,
                    created__range=[start_date, end_date]
                )

            else:
                qs = qs.objects.filter(
                    prev_study=prev_study,
                    created__range=[start_date, end_date])

        df = read_frame(qs, fieldnames=['prev_study', 'study_maternal_identifier'])
        df = df.drop_duplicates(subset=['study_maternal_identifier'])

        # qs1 = InPersonContactAttempt.objects.all()
        # if prev_study:
        #     if prev_study == '-----':
        #         qs1 = InPersonContactAttempt.objects.filter(
        #             created__range=[start_date, end_date])
        #     else:
        #         qs1 = InPersonContactAttempt.objects.filter(
        #             prev_study=prev_study,
        #             created__range=[start_date, end_date])
        # df1 = read_frame(qs1, fieldnames=['prev_study', 'study_maternal_identifier'])
        # df1 = df1.drop_duplicates(subset=['study_maternal_identifier'])

        result = df
        result = result.drop_duplicates(subset=['study_maternal_identifier'])

        prev_study_list = []
        for prev_study in self.prev_studies:
            df_prev = result[result['prev_study'] == prev_study]
            prev_study_list.append([prev_study, df_prev[df_prev.columns[0]].count()])
        return prev_study_list

    def pending(self, prev_study=None, start_date=None, end_date=None):
        """Return number of participants who are randomised but nothing has been done on them.
        """

        qs = WorkList.objects.filter(
            assigned__isnull=False)

        if prev_study:
            qs = qs.filter(
                created__range=[start_date, end_date],
                assigned__isnull=False,
                visited=False)

            if prev_study != '-----':
                qs = qs.filter(prev_study=prev_study)

        df = read_frame(qs, fieldnames=['prev_study', 'study_maternal_identifier'])

        df = df.drop_duplicates(subset=['study_maternal_identifier'])

        prev_study_list = []
        for prev_study in self.prev_studies:
            df_prev = df[df['prev_study'] == prev_study]
            prev_study_list.append([prev_study, df_prev[df_prev.columns[0]].count()])
        return prev_study_list

    def non_randomized(self, prev_study=None, start_date=None, end_date=None):
        """Return number of participants who are randomised but nothing has been done on them.
        """

        qs = WorkList.objects.filter(
            assigned__isnull=True,
        )
        if prev_study:
            qs = qs.filter(created__range=[start_date, end_date])

            if prev_study != '-----':
                qs = qs.filter(prev_study=prev_study,)

        df = read_frame(qs, fieldnames=['prev_study', 'study_maternal_identifier'])

        df = df.drop_duplicates(subset=['study_maternal_identifier'])

        prev_study_list = []
        for prev_study in self.prev_studies:
            df_prev = df[df['prev_study'] == prev_study]
            prev_study_list.append([prev_study, df_prev[df_prev.columns[0]].count()])
        return prev_study_list

    def unable_to_reach(self, prev_study=None, start_date=None, end_date=None):
        """Return number of contacted participants.
        """

        # Call logs
        # identifiers = []

        qs = WorkList.objects.filter(
            is_called=True,
            assigned__isnull=False,
        ).values_list('study_maternal_identifier')

        qs = LogEntry.objects.filter(
            study_maternal_identifier__in=qs,
            phone_num_success=['none_of_the_above'])

        if prev_study:
            if prev_study == '-----':
                qs = LogEntry.objects.filter(
                    phone_num_success=['none_of_the_above'])
            else:
                qs = LogEntry.objects.filter(
                    prev_study=prev_study,
                    created__range=[start_date, end_date],
                    phone_num_success=['none_of_the_above'])
        # identifiers = list(identifiers)
        # In contact attempts
        # qs = InPersonContactAttempt.objects.filter(
        #     Q(study_maternal_identifier__in=identifiers) | Q(successful_location=['none_of_the_above']))
        # if prev_study:
        #     if prev_study == '-----':
        #         qs = InPersonContactAttempt.objects.filter(
        #             study_maternal_identifier__in=identifiers,
        #             created__range=[start_date, end_date],
        #             successful_location=['none_of_the_above'])
        #     else:
        #         qs = InPersonContactAttempt.objects.filter(
        #             study_maternal_identifier__in=identifiers,
        #             prev_study=prev_study,
        #             created__range=[start_date, end_date],
        #             successful_location=['none_of_the_above'])

        df = read_frame(qs, fieldnames=['prev_study', 'study_maternal_identifier'])
        df = df.drop_duplicates(subset=['study_maternal_identifier'])

        prev_study_list = []
        for prev_study in self.prev_studies:
            df_prev = df[df['prev_study'] == prev_study]
            prev_study_list.append([prev_study, df_prev[df_prev.columns[0]].count()])
        return prev_study_list

    def decline_uninterested(self, prev_study=None, start_date=None, end_date=None):
        """Return number of contacted participants.
        """

        qs = LogEntry.objects.filter(Q(may_call__iexact='No') | Q(appt__iexact='No'))

        if prev_study is None or prev_study == '-----':
            if start_date and prev_study:
                qs = LogEntry.objects.filter(
                    Q(may_call__iexact='No') | Q(appt__iexact='No'),
                    created__range=[start_date, end_date],
                )
            else:
                qs = LogEntry.objects.filter(Q(may_call__iexact='No') | Q(appt__iexact='No'))
        else:
            if start_date and prev_study:
                qs = LogEntry.objects.filter(
                    Q(may_call__iexact='No') | Q(appt__iexact='No'),
                    prev_study=prev_study,
                    created__range=[start_date, end_date],
                )
            else:
                qs = LogEntry.objects.filter(
                    Q(may_call__iexact='No') | Q(appt__iexact='No'),
                    prev_study=prev_study,
                )

        df1 = read_frame(qs, fieldnames=['prev_study', 'study_maternal_identifier'])

        df1 = df1.drop_duplicates(subset=['study_maternal_identifier'])

        # Screening rejects
        identifiers = ScreeningPriorBhpParticipants.objects.filter(
            flourish_participation=NO).values_list(
                'study_maternal_identifier', flat=True)
        identifiers = list(set(identifiers))

        qs1 = MaternalDataset.objects.filter(
            study_maternal_identifier__in=identifiers)
        df2 = read_frame(qs1, fieldnames=['protocol', 'study_maternal_identifier'])
        df2 = df2.rename(columns={'protocol': 'prev_study'})
        df2 = df2.drop_duplicates(subset=['study_maternal_identifier'])

        # Merge frames
        frames = [df1, df2]
        df = pd.concat(frames)

        prev_study_list = []
        for prev_study in self.prev_studies:
            df_prev = df[df['prev_study'] == prev_study]
            prev_study_list.append([prev_study, df_prev[df_prev.columns[0]].count()])
        return prev_study_list

    def consented(self, prev_study=None, start_date=None, end_date=None):
        """Return number of contacted participants.
        """

        screening_identifiers = SubjectConsent.objects.all().values_list(
            'screening_identifier', flat=True)
        screening_identifiers = list(set(screening_identifiers))
        qs = MaternalDataset.objects.filter(
            screening_identifier__in=screening_identifiers)
        df = read_frame(qs, fieldnames=['protocol', 'study_maternal_identifier'])
        df = df.drop_duplicates(subset=['study_maternal_identifier'])

        prev_study_list = []
        for prev_study in self.prev_studies:
            df_prev = df[df['protocol'] == prev_study]
            prev_study_list.append([prev_study, df_prev[df_prev.columns[0]].count()])
        return prev_study_list

    def thinking(self, prev_study=None, start_date=None, end_date=None):
        """Return number of contacted participants.
        """

        qs = LogEntry.objects.filter(appt__iexact='thinking')

        if prev_study:

            qs = qs.filter(created__range=[start_date, end_date])
            if prev_study != '-----':
                qs = qs.filter(prev_study=prev_study)

        df = read_frame(qs, fieldnames=['prev_study', 'study_maternal_identifier'])
        df = df.drop_duplicates(subset=['study_maternal_identifier'])

        prev_study_list = []
        for prev_study in self.prev_studies:
            df_prev = df[df['prev_study'] == prev_study]
            prev_study_list.append([prev_study, df_prev[df_prev.columns[0]].count()])
        return prev_study_list

    def total_calculator(self, total, element):
        total += element
        return total

    def prev_report_data(self, prev_study=None, start_date=None, end_date=None):
        """Return the data for the report.
        """
        data = []
        total = []
        if prev_study and start_date and end_date:
            data = [
                self.total_previous_study_participents(
                    prev_study=prev_study,
                    start_date=start_date,
                    end_date=end_date
                ),
                self.total_partici_onworklist(
                    prev_study=prev_study,
                    start_date=start_date,
                    end_date=end_date
                ),
                self.attempts(
                    prev_study=prev_study,
                    start_date=start_date,
                    end_date=end_date),
                self.non_randomized(
                    prev_study=prev_study,
                    start_date=start_date,
                    end_date=end_date),
                self.pending(
                    prev_study=prev_study,
                    start_date=start_date,
                    end_date=end_date),
                self.cont_contact(
                    prev_study=prev_study,
                    start_date=start_date,
                    end_date=end_date),
                self.unable_to_reach(
                    prev_study=prev_study,
                    start_date=start_date,
                    end_date=end_date),
                self.decline_uninterested(
                    prev_study=prev_study,
                    start_date=start_date,
                    end_date=end_date),
                self.thinking(
                    prev_study=prev_study,
                    start_date=start_date,
                    end_date=end_date),
                self.consented(
                    prev_study=prev_study,
                    start_date=start_date,
                    end_date=end_date)]

        else:
            data = [
                self.total_previous_study_participents(),
                self.total_partici_onworklist(),
                self.non_randomized(),
                self.pending(),
                self.cont_contact(),
                self.attempts(),
                self.unable_to_reach(),
                self.decline_uninterested(),
                self.thinking(),
                self.consented()]
        for element in data:
            total_per_column = 0
            for study_number in element:
                total_per_column += study_number[1]
            total.append(total_per_column)

        result = reduce(merge, data)

        return [result, total]

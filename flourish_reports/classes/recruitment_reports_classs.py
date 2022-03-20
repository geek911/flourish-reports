import pandas as pd

from django.core.exceptions import ValidationError
from django.db.models import Q
from django_pandas.io import read_frame

from django.shortcuts import HttpResponse

from flourish_caregiver.models import CaregiverLocator, MaternalDataset, SubjectConsent, ScreeningPriorBhpParticipants
from flourish_follow.models import LogEntry, WorkList
from flourish_child.models import ChildDataset


class PieTotals:
    def __init__(self, mpepu=None, tshipidi=None, mashi=None, mma_bana=None, tshilo_dikotla=None,
                 total_continued_contact=None, total_decline_uninterested=None, total_consented=None,
                 total_unable_to_reach=None):
        self.mpepu = mpepu
        self.tshipidi = tshipidi
        self.mashi = mashi
        self.mma_bana = mma_bana
        self.tshilo_dikotla = tshilo_dikotla
        self.total_continued_contact = total_continued_contact
        self.total_decline_uninterested = total_decline_uninterested
        self.total_consented = total_consented
        self.total_unable_to_reach = total_unable_to_reach


class BarChart:
    def __init__(self, mpepu=None, tshipidi=None, mashi=None, mma_bana=None, tshilo_dikotla=None):
        self.mpepu = mpepu
        self.tshipidi = tshipidi
        self.mashi = mashi
        self.mma_bana = mma_bana
        self.tshilo_dikotla = tshilo_dikotla


class RecruitmentReport:

    @property
    def previous_studies(self):
        """Returns a list of all BHP previous studies used.
        """
        maternal_dataset = MaternalDataset.objects.all()
        return list(set(maternal_dataset.values_list('protocol', flat=True)))

    def caregiver_prev_study_dataset(self):
        """Return the totals of all prev study participant dataset
        for caregivers.
        """
        pie = PieTotals(mpepu=200, tshipidi=244, tshilo_dikotla=1000, mma_bana=500, mashi=700)
        maternal_dataset = MaternalDataset.objects.all()
        df = read_frame(maternal_dataset, fieldnames=['protocol', 'study_maternal_identifier'])

        maternal_dataset_starts = []
        total = 0
        for protocol in self.previous_studies:
            df_prev = df[df['protocol'] == protocol]
            maternal_dataset_starts.append([protocol, df_prev[df_prev.columns[0]].count()])
            if protocol == 'Mpepu':
                pie.mpepu = df_prev[df_prev.columns[0]].count()
            elif protocol == 'Tshilo Dikotla':
                pie.tshilo_dikotla = df_prev[df_prev.columns[0]].count()
            elif protocol == 'Mashi':
                pie.mashi = df_prev[df_prev.columns[0]].count()
            elif protocol == 'Mma Bana':
                pie.mma_bana = df_prev[df_prev.columns[0]].count()
            elif protocol == 'Tshipidi':
                pie.tshipidi = df_prev[df_prev.columns[0]].count()

            total += df_prev[df_prev.columns[0]].count()
        maternal_dataset_starts.append(['All studies', total])
        return maternal_dataset_starts, pie

    def child_prev_study_dataset(self):
        """Return the totals of all prev study child participant dataset.
        """
        child_dataset = ChildDataset.objects.all()
        data = []
        for dt in child_dataset:
            obj_dict = dt.__dict__
            try:
                maternal_dataset = MaternalDataset.objects.get(
                    study_maternal_identifier=obj_dict.get('study_maternal_identifier'))
            except MaternalDataset.DoesNotExist:
                raise ValidationError(f"Missing mother of ID: {obj_dict.get('study_maternal_identifier')}")
            else:
                obj_dict.update(protocol=maternal_dataset.protocol)
            data.append(obj_dict)

        df = pd.DataFrame(data)
        df = df[["study_child_identifier", "protocol"]]
        child_dataset_starts = []
        total = 0
        for protocol in self.previous_studies:
            df_prev = df[df['protocol'] == protocol]
            child_dataset_starts.append([protocol, df_prev[df_prev.columns[0]].count()])
            total += df_prev[df_prev.columns[0]].count()

        child_dataset_starts.append(['All studies', total])
        return child_dataset_starts

    def locator_report(self):
        """Return a list of locator availability per prev study participant.
        """
        # Previous studies data
        data = []
        maternal_dataset = MaternalDataset.objects.all()
        df = read_frame(maternal_dataset, fieldnames=['protocol', 'study_maternal_identifier'])

        # Add total expected locators per study
        maternal_dataset_starts_dict = {}
        for protocol in self.previous_studies:
            df_prev = df[df['protocol'] == protocol]
            maternal_dataset_starts_dict[protocol] = df_prev[df_prev.columns[0]].count()
        dt = [maternal_dataset_starts_dict.get(prev_study) for prev_study in self.previous_studies]
        my_data = dt + [sum(dt)]
        my_data.insert(0, "Total Expected")
        data.append(my_data)

        # Add total locators per study
        locator_identifiers = CaregiverLocator.objects.all().values_list('study_maternal_identifier', flat=True)
        locator_identifiers = list(set(locator_identifiers))

        maternal_dataset = MaternalDataset.objects.filter(study_maternal_identifier__in=locator_identifiers)
        df = read_frame(maternal_dataset, fieldnames=['protocol', 'study_maternal_identifier'])

        maternal_dataset_starts_dict = {}
        for protocol in self.previous_studies:
            df_prev = df[df['protocol'] == protocol]
            maternal_dataset_starts_dict[protocol] = df_prev[df_prev.columns[0]].count()
        dt = [maternal_dataset_starts_dict.get(prev_study) for prev_study in self.previous_studies]
        my_data = dt + [sum(dt)]
        my_data.insert(0, "Total Existing")
        data.append(my_data)

        # Missing locators per prev study
        all_data = MaternalDataset.objects.all().values_list('study_maternal_identifier', flat=True)
        missing_locators_identifiers = list(set(all_data) - set(locator_identifiers))
        missing_locator_dataset = MaternalDataset.objects.filter(
            study_maternal_identifier__in=missing_locators_identifiers)
        df = read_frame(missing_locator_dataset, fieldnames=['protocol', 'study_maternal_identifier'])

        maternal_dataset_starts_dict = {}
        for protocol in self.previous_studies:
            df_prev = df[df['protocol'] == protocol]
            maternal_dataset_starts_dict[protocol] = df_prev[df_prev.columns[0]].count()
        dt = [maternal_dataset_starts_dict.get(prev_study) for prev_study in self.previous_studies]
        my_data = dt + [sum(dt)]
        my_data.insert(0, "Total Missing")
        data.append(my_data)
        return data

    def worklist_report(self):
        """Return a list of worklist report vs all paticipants data. Fixme refactor
        """
        maternal_dataset_identifier = MaternalDataset.objects.all().values_list('study_maternal_identifier', flat=True)
        maternal_dataset_identifier = list(set(maternal_dataset_identifier))

        worklist = WorkList.objects.filter(
            study_maternal_identifier__in=maternal_dataset_identifier).values_list('study_maternal_identifier',
                                                                                   flat=True)
        worklist = list(set(worklist))
        missing_worklist = list(set(maternal_dataset_identifier) - set(worklist))

        # Ranndomised
        randomised_worklist = WorkList.objects.filter(
            assigned__isnull=False,
            study_maternal_identifier__in=maternal_dataset_identifier).values_list('study_maternal_identifier',
                                                                                   flat=True)
        randomised_worklist = list(set(randomised_worklist))

        # Not Ranndomised
        not_randomised_worklist = WorkList.objects.filter(
            assigned__isnull=True,
            study_maternal_identifier__in=maternal_dataset_identifier).values_list('study_maternal_identifier',
                                                                                   flat=True)
        not_randomised_worklist = list(set(not_randomised_worklist))
        final_not_randomised_worklist = []
        for ident in not_randomised_worklist:
            log = LogEntry.objects.filter(study_maternal_identifier=ident)
            if not log:
                final_not_randomised_worklist.append(ident)
        final_not_randomised_worklist = list(set(final_not_randomised_worklist))
        summary_list = []
        columns = ['Total Expected', 'Total Existing worklist', 'Total missing worklist',
                   'Total worked list assigned', 'Worklist not randomised & not attempted']
        data = [[len(maternal_dataset_identifier), len(worklist), len(missing_worklist), len(randomised_worklist),
                 len(final_not_randomised_worklist)]]

        summary_list.append(columns)
        summary_list.append(data)

        df = pd.DataFrame(data, columns=columns)

        # Previous studies data
        data = []
        maternal_dataset = MaternalDataset.objects.all()
        previous_studies = list(set(maternal_dataset.values_list('protocol', flat=True)))
        df = read_frame(maternal_dataset, fieldnames=['protocol', 'study_maternal_identifier'])

        total_expected_worklist = df

        # Add total expected worklist per study
        maternal_dataset_starts_dict = {}
        for protocol in previous_studies:
            df_prev = df[df['protocol'] == protocol]
            maternal_dataset_starts_dict[protocol] = df_prev[df_prev.columns[0]].count()
        dt = [maternal_dataset_starts_dict.get(prev_study) for prev_study in previous_studies] + [
            maternal_dataset.count()]
        dt.insert(0, "Expected Worklist")
        data.append(dt)

        # Add total worklist per study
        all_previous_studies = previous_studies + ['All Studies']

        worklist_identifiers = WorkList.objects.all().values_list('study_maternal_identifier', flat=True)
        worklist_identifiers = list(set(worklist_identifiers))

        maternal_dataset = MaternalDataset.objects.filter(study_maternal_identifier__in=worklist_identifiers)
        df = read_frame(maternal_dataset, fieldnames=['protocol', 'study_maternal_identifier'])

        maternal_dataset_starts_dict = {}
        for protocol in previous_studies:
            df_prev = df[df['protocol'] == protocol]
            maternal_dataset_starts_dict[protocol] = df_prev[df_prev.columns[0]].count()
        dt = [maternal_dataset_starts_dict.get(prev_study) for prev_study in previous_studies]
        my_data = dt + [sum(dt)]
        my_data.insert(0, "Existing Worklist")
        data.append(my_data)

        # Missing worklist per prev study
        all_data = MaternalDataset.objects.all().values_list('study_maternal_identifier', flat=True)
        missing_worklist_identifiers = list(set(all_data) - set(worklist_identifiers))
        missing_worklist_dataset = MaternalDataset.objects.filter(
            study_maternal_identifier__in=missing_worklist_identifiers)
        df = read_frame(missing_worklist_dataset, fieldnames=['protocol', 'study_maternal_identifier'])

        maternal_dataset_starts_dict = {}
        for protocol in previous_studies:
            df_prev = df[df['protocol'] == protocol]
            maternal_dataset_starts_dict[protocol] = df_prev[df_prev.columns[0]].count()
        dt = [maternal_dataset_starts_dict.get(prev_study) for prev_study in previous_studies]
        my_data = dt + [sum(dt)]
        my_data.insert(0, "Missing worklist")
        data.append(my_data)

        # Randomised worklist per prev study
        randomised_worklist_dataset = MaternalDataset.objects.filter(study_maternal_identifier__in=worklist_identifiers)
        df = read_frame(randomised_worklist_dataset, fieldnames=['protocol', 'study_maternal_identifier'])

        maternal_dataset_starts_dict = {}
        for protocol in previous_studies:
            df_prev = df[df['protocol'] == protocol]
            maternal_dataset_starts_dict[protocol] = df_prev[df_prev.columns[0]].count()
        dt = [maternal_dataset_starts_dict.get(prev_study) for prev_study in previous_studies]
        my_data = dt + [sum(dt)]
        my_data.insert(0, "Randomised Worklist")
        data.append(my_data)
        # End

        # Not Randomised Not attempted worklist per prev study
        not_randomised_worklist_dataset = MaternalDataset.objects.filter(
            study_maternal_identifier__in=final_not_randomised_worklist)
        df = read_frame(not_randomised_worklist_dataset, fieldnames=['protocol', 'study_maternal_identifier'])

        maternal_dataset_starts_dict = {}
        for protocol in previous_studies:
            df_prev = df[df['protocol'] == protocol]
            maternal_dataset_starts_dict[protocol] = df_prev[df_prev.columns[0]].count()
        dt = [maternal_dataset_starts_dict.get(prev_study) for prev_study in previous_studies]
        my_data = dt + [sum(dt)]
        my_data.insert(0, "Not randomised & not attempted")
        data.append(my_data)
        # End
        return data

    def attemps_report_data(self):

        data = []
        prev_studies = [
            'Mpepu',
            'Mma Bana',
            'Mashi',
            'Tshilo Dikotla',
            'Tshipidi']

        qs = LogEntry.objects.all()
        attempt_identifiers = qs.values_list('study_maternal_identifier', flat=True)
        data_set_identifier = MaternalDataset.objects.all().values_list('study_maternal_identifier', flat=True)
        all_identifiers = list(set(data_set_identifier))
        tried_identifiers = list(set(attempt_identifiers))
        new_list = list(set(all_identifiers) - set(tried_identifiers))

        # Create a list of those not attempted
        missing_prev_study_list = {}
        merged_list_of_miss_by_study = []
        for prev_study in prev_studies:
            datas = MaternalDataset.objects.filter(protocol=prev_study, study_maternal_identifier__in=new_list)
            merged_list_of_miss_by_study += list(datas.values_list('study_maternal_identifier', 'protocol'))
            missing_prev_study_list[prev_study] = datas.count()

        # Create a list of attempted
        merged_list_of_attempts_by_study = []
        for prev_study in prev_studies:
            datas = MaternalDataset.objects.filter(protocol=prev_study, study_maternal_identifier__in=tried_identifiers)
            merged_list_of_attempts_by_study += list(datas.values_list('study_maternal_identifier', 'protocol'))

        prev_study_list = {}
        total_attempts = 0
        for prev_study in prev_studies:
            datas = LogEntry.objects.filter(prev_study=prev_study).values_list('study_maternal_identifier', flat=True)
            datas = list(set(datas))
            prev_study_list[prev_study] = len(datas)
            total_attempts += len(datas)

        # Add study totals and totals not attempted
        attempts_data = []
        for study, attempts in prev_study_list.items():
            dataset = MaternalDataset.objects.filter(protocol=study)
            attempts_data.append([study, dataset.count(), attempts, missing_prev_study_list.get(study)])


        dataset = MaternalDataset.objects.all()

        all_data = attempts_data + [['All Studies', dataset.count(), total_attempts, len(new_list)]]
        return all_data, total_attempts, len(new_list)

    def participants_to_call_again(self):

        prev_studies = [
            'Mpepu',
            'Mma Bana',
            'Mashi',
            'Tshilo Dikotla',
            'Tshipidi']

        # Return number of contacted participants who are still being contacted.
        total = 0
        screening_identifiers = SubjectConsent.objects.all().values_list(
            'screening_identifier', flat=True)
        screening_identifiers = list(set(screening_identifiers))

        consented_pids = MaternalDataset.objects.filter(
            screening_identifier__in=screening_identifiers).values_list(
            'study_maternal_identifier', flat=True)

        no_appt_pids = LogEntry.objects.filter(appt='No').values_list(
            'study_maternal_identifier', flat=True)

        exclude_identifiers = list(set(consented_pids)) + list(set(no_appt_pids))
        exclude_identifiers = list(set(exclude_identifiers))

        qs = LogEntry.objects.filter(
            ~Q(study_maternal_identifier__in=exclude_identifiers),
            ~Q(phone_num_success=['none_of_the_above']),
            appt__in=['thinking', 'Yes'])

        df = read_frame(qs, fieldnames=['prev_study', 'study_maternal_identifier'])
        df = df.drop_duplicates(subset=['study_maternal_identifier'])

        result = df
        result = result.drop_duplicates(subset=['study_maternal_identifier'])

        prev_study_list = []
        for prev_study in prev_studies:
            df_prev = result[result['prev_study'] == prev_study]
            prev_study_list.append([prev_study, df_prev[df_prev.columns[0]].count()])
            total += df_prev[df_prev.columns[0]].count()
        return prev_study_list, total

    def participants_not_reachable(self):

        prev_studies = [
            'Mpepu',
            'Mma Bana',
            'Mashi',
            'Tshilo Dikotla',
            'Tshipidi']

        screening_identifiers = SubjectConsent.objects.all().values_list(
            'screening_identifier', flat=True)
        screening_identifiers = list(set(screening_identifiers))

        consented_pids = MaternalDataset.objects.filter(
            screening_identifier__in=screening_identifiers).values_list(
            'study_maternal_identifier', flat=True)

        phone_success = [
            ['subject_cell'],
            ['subject_cell_alt'],
            ['subject_phone'],
            ['subject_phone_alt'],
            ['subject_work_phone'],
            ['indirect_contact_cell'],
            ['indirect_contact_phone'],
            ['caretaker_cell'],
            ['caretaker_tel']
        ]

        reacheble_identifiers = LogEntry.objects.filter(
            phone_num_success__in=phone_success).values_list('study_maternal_identifier', flat=True)
        reacheble_identifiers = list(set(reacheble_identifiers))

        qs = LogEntry.objects.filter(
            ~Q(study_maternal_identifier__in=consented_pids),
            ~Q(study_maternal_identifier__in=reacheble_identifiers),
            ~Q(appt__in=['thinking', 'Yes']),
            phone_num_success=['none_of_the_above'],
        )

        df = read_frame(qs, fieldnames=['prev_study', 'study_maternal_identifier'])
        df = df.drop_duplicates(subset=['study_maternal_identifier'])
        # df.to_csv('unable_to_reach.csv', encoding='utf-8')
        prev_study_list = []
        total = 0
        for prev_study in prev_studies:
            df_prev = df[df['prev_study'] == prev_study]
            prev_study_list.append([prev_study, df_prev[df_prev.columns[0]].count()])
            total += df_prev[df_prev.columns[0]].count()

        prev_study_list.append(['All studies', total])
        results = pd.DataFrame(prev_study_list, columns=['Previous Study', 'Total participants'])
        # display(Markdown(f"**Previous studies participants who are still being contacted**"))
        # display(HTML(results.to_html()))
        return prev_study_list, total

    def declined(self):

        prev_studies = [
            'Mpepu',
            'Mma Bana',
            'Mashi',
            'Tshilo Dikotla',
            'Tshipidi']

        screening_identifiers = SubjectConsent.objects.all().values_list(
            'screening_identifier', flat=True)
        screening_identifiers = list(set(screening_identifiers))

        consented_pids = MaternalDataset.objects.filter(
            screening_identifier__in=screening_identifiers).values_list(
            'study_maternal_identifier', flat=True)

        qs = LogEntry.objects.filter(
            ~Q(study_maternal_identifier__in=consented_pids),
            ~Q(appt__in=['thinking', 'Yes']),
            Q(may_call__iexact='No'))

        df1 = read_frame(qs, fieldnames=['prev_study', 'study_maternal_identifier'])

        df1 = df1.drop_duplicates(subset=['study_maternal_identifier'])

        # Screening rejects
        identifiers = ScreeningPriorBhpParticipants.objects.filter(
            flourish_participation='No').values_list(
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
        # df.to_csv('declined.csv', encoding='utf-8')
        prev_study_list = []
        total = 0
        for prev_study in prev_studies:
            df_prev = df[df['prev_study'] == prev_study]
            prev_study_list.append([prev_study, df_prev[df_prev.columns[0]].count()])
            total += df_prev[df_prev.columns[0]].count()

        prev_study_list.append(['All studies', total])

        return prev_study_list, total


    def consented(self):


        prev_studies = [
            'Mpepu',
            'Mma Bana',
            'Mashi',
            'Tshilo Dikotla',
            'Tshipidi']

        screening_identifiers = SubjectConsent.objects.all().values_list(
            'screening_identifier', flat=True)
        screening_identifiers = list(set(screening_identifiers))
        qs = MaternalDataset.objects.filter(
            screening_identifier__in=screening_identifiers)
        df = read_frame(qs, fieldnames=['protocol', 'study_maternal_identifier'])
        df = df.drop_duplicates(subset=['study_maternal_identifier'])
        # df.to_csv('consented.csv', encoding='utf-8')
        prev_study_list = []
        total = 0
        for prev_study in prev_studies:
            df_prev = df[df['protocol'] == prev_study]
            prev_study_list.append([prev_study, df_prev[df_prev.columns[0]].count()])
            total += df_prev[df_prev.columns[0]].count()

        prev_study_list.append(['All studies', total])

        return prev_study_list, total

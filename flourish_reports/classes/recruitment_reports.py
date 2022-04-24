import pandas as pd

from django.core.exceptions import ValidationError
from django.db.models import Q
from django_pandas.io import read_frame

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

    
    @property
    def locator_df(self):
        """Returns a dataframe for locator information availability.
        """
        # Existing total locators per study
        locator_identifiers = CaregiverLocator.objects.all().values_list('study_maternal_identifier', flat=True)
        locator_identifiers = list(set(locator_identifiers))
        maternal_dataset = MaternalDataset.objects.filter(study_maternal_identifier__in=locator_identifiers)
        available_df = read_frame(maternal_dataset, fieldnames=['protocol', 'study_maternal_identifier'])
        available_df["Available"] = True
        
        # Missing locators per prev study
        all_data = MaternalDataset.objects.all().values_list('study_maternal_identifier', flat=True)
        missing_locators_identifiers = list(set(all_data) - set(locator_identifiers))
        missing_locator_dataset = MaternalDataset.objects.filter(
            study_maternal_identifier__in=missing_locators_identifiers)
        not_available_df = read_frame(missing_locator_dataset, fieldnames=['protocol', 'study_maternal_identifier'])
        not_available_df["Available"] = False
        
        # Merge frames
        frames = [available_df, not_available_df]
        df = pd.concat(frames)
        return df

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


    @property
    def randomised_df(self):
        """Return a dataframe for participant randomisation.
        """
        md_identifier = MaternalDataset.objects.all().values_list(
            'study_maternal_identifier', flat=True)
        md_identifier = list(set(md_identifier))

        # Ranndomised
        randomised_worklist = WorkList.objects.filter(
            assigned__isnull=False,
            study_maternal_identifier__in=md_identifier).values_list(
                'study_maternal_identifier', flat=True)
        randomised_worklist = list(set(randomised_worklist))
        maternal_dataset = MaternalDataset.objects.filter(
            study_maternal_identifier__in=randomised_worklist)
        df_randomised = read_frame(
            maternal_dataset, fieldnames=[
                'protocol', 'study_maternal_identifier'])
        df_randomised

        maternal_dataset = MaternalDataset.objects.filter(
            study_maternal_identifier__in=randomised_worklist)
        df_not_randomised = read_frame(
            maternal_dataset, fieldnames=[
                'protocol', 'study_maternal_identifier'])
        df_not_randomised["Randomisation status"] = False
        
        # Merge frames
        frames = [df_randomised, df_not_randomised]
        df = pd.concat(frames)
        return df

    def worklist_report(self):
        """Return a list of worklist report vs all paticipants data.
        """
        md_identifier = MaternalDataset.objects.all().values_list(
            'study_maternal_identifier', flat=True)
        md_identifier = list(set(md_identifier))

        worklist = WorkList.objects.filter(
            study_maternal_identifier__in=md_identifier).values_list(
                'study_maternal_identifier', flat=True)
        worklist = list(set(worklist))
        missing_worklist = list(set(md_identifier) - set(worklist))

        # Ranndomised
        randomised_worklist = WorkList.objects.filter(
            assigned__isnull=False,
            study_maternal_identifier__in=md_identifier).values_list(
                'study_maternal_identifier', flat=True)
        randomised_worklist = list(set(randomised_worklist))

        # Not Ranndomised
        not_randomised_worklist = WorkList.objects.filter(
            assigned__isnull=True,
            study_maternal_identifier__in=md_identifier).values_list(
                'study_maternal_identifier', flat=True)
        not_randomised_worklist = list(set(not_randomised_worklist))
        final_not_randomised_worklist = []
        for ident in not_randomised_worklist:
            log = LogEntry.objects.filter(study_maternal_identifier=ident)
            if not log:
                final_not_randomised_worklist.append(ident)
        final_not_randomised_worklist = list(set(final_not_randomised_worklist))
        summary_list = []
        columns = [
            'Total Expected', 'Total Existing worklist',
            'Total missing worklist',
            'Total worked list assigned',
            'Worklist not randomised & not attempted']
        data = [
            [len(md_identifier), len(worklist), len(missing_worklist),
             len(randomised_worklist), len(final_not_randomised_worklist)]]

        summary_list.append(columns)
        summary_list.append(data)

        # Previous studies data
        data = []
        maternal_dataset = MaternalDataset.objects.all()
        previous_studies = list(
            set(maternal_dataset.values_list('protocol', flat=True)))
        df = read_frame(
            maternal_dataset, fieldnames=[
                'protocol', 'study_maternal_identifier'])

        # Add total expected worklist per study
        md_starts_dict = {}
        for protocol in previous_studies:
            df_prev = df[df['protocol'] == protocol]
            md_starts_dict[
                protocol] = df_prev[df_prev.columns[0]].count()
        dt = [
            md_starts_dict.get(prev_study) for prev_study in previous_studies] + [maternal_dataset.count()]
        dt.insert(0, "Expected Worklist")
        data.append(dt)

        worklist_identifiers = WorkList.objects.all().values_list(
            'study_maternal_identifier', flat=True)
        worklist_identifiers = list(set(worklist_identifiers))

        maternal_dataset = MaternalDataset.objects.filter(
            study_maternal_identifier__in=worklist_identifiers)
        df = read_frame(maternal_dataset, fieldnames=[
            'protocol', 'study_maternal_identifier'])

        md_starts_dict = {}
        for protocol in previous_studies:
            df_prev = df[df['protocol'] == protocol]
            md_starts_dict[protocol] = df_prev[df_prev.columns[0]].count()
        dt = [md_starts_dict.get(prev_study) for prev_study in previous_studies]
        my_data = dt + [sum(dt)]
        my_data.insert(0, "Existing Worklist")
        data.append(my_data)

        # Missing worklist per prev study
        all_data = MaternalDataset.objects.all().values_list(
            'study_maternal_identifier', flat=True)
        missing_worklist_identifiers = list(
            set(all_data) - set(worklist_identifiers))
        missing_worklist_dataset = MaternalDataset.objects.filter(
            study_maternal_identifier__in=missing_worklist_identifiers)
        df = read_frame(missing_worklist_dataset, fieldnames=[
            'protocol', 'study_maternal_identifier'])

        md_starts_dict = {}
        for protocol in previous_studies:
            df_prev = df[df['protocol'] == protocol]
            md_starts_dict[protocol] = df_prev[df_prev.columns[0]].count()
        dt = [md_starts_dict.get(prev_study) for prev_study in previous_studies]
        my_data = dt + [sum(dt)]
        my_data.insert(0, "Missing worklist")
        data.append(my_data)

        # Randomised worklist per prev study
        rd_worklist = MaternalDataset.objects.filter(
            study_maternal_identifier__in=worklist_identifiers)
        df = read_frame(rd_worklist, fieldnames=[
            'protocol', 'study_maternal_identifier'])

        md_starts_dict = {}
        for protocol in previous_studies:
            df_prev = df[df['protocol'] == protocol]
            md_starts_dict[protocol] = df_prev[df_prev.columns[0]].count()
        dt = [md_starts_dict.get(prev_study) for prev_study in previous_studies]
        my_data = dt + [sum(dt)]
        my_data.insert(0, "Randomised Worklist")
        data.append(my_data)
        # End

        # Not Randomised Not attempted worklist per prev study
        not_rd_worklist= MaternalDataset.objects.filter(
            study_maternal_identifier__in=final_not_randomised_worklist)
        df = read_frame(not_rd_worklist, fieldnames=[
            'protocol', 'study_maternal_identifier'])

        md_starts_dict = {}
        for protocol in previous_studies:
            df_prev = df[df['protocol'] == protocol]
            md_starts_dict[protocol] = df_prev[df_prev.columns[0]].count()
        dt = [md_starts_dict.get(prev_study) for prev_study in previous_studies]
        my_data = dt + [sum(dt)]
        my_data.insert(0, "Not randomised & not attempted")
        data.append(my_data)
        # End
        return data

    @property
    def attempted_identifiers(self):
        """Returns a list of identifiers for participants who have an attempt to
        reach them made.
        """
        qs = LogEntry.objects.all()
        attempt_identifiers = qs.values_list(
            'study_maternal_identifier', flat=True)
        return list(set(attempt_identifiers))

    @property
    def consented_identifiers(self):
        """Reutns a list of consented participants.
        """
        screening_identifiers = SubjectConsent.objects.all().values_list(
            'screening_identifier', flat=True)
        screening_identifiers = list(set(screening_identifiers))
        consented_pids = MaternalDataset.objects.filter(
            screening_identifier__in=screening_identifiers).values_list(
                'study_maternal_identifier', flat=True)
        return list(set(consented_pids))


    @property
    def attempts_df(self):
        """Returns a dataframe of attempts.
        """
        data_set_identifier = MaternalDataset.objects.all().values_list(
            'study_maternal_identifier', flat=True)
        all_identifiers = list(set(data_set_identifier))
        maternal_dataset = MaternalDataset.objects.filter(
            study_maternal_identifier__in=self.attempted_identifiers)
        attempted_df = read_frame(maternal_dataset, fieldnames=[
            'protocol', 'study_maternal_identifier'])
        attempted_df["Attempted status"] = True
        
        not_attempted = list(
            set(all_identifiers) - set(self.attempted_identifiers))
        maternal_dataset = MaternalDataset.objects.filter(
            study_maternal_identifier__in=not_attempted)
        not_attempted_df = read_frame(maternal_dataset, fieldnames=[
            'protocol', 'study_maternal_identifier'])
        not_attempted_df["Attempted status"] = False
        
        
        # Merge frames
        frames = [attempted_df, not_attempted_df]
        df = pd.concat(frames)
        return df
        

    def attempts_report_data(self):
        """Returns a report for participants who attempts where made.
        """
        data_set_identifier = MaternalDataset.objects.all().values_list(
            'study_maternal_identifier', flat=True)
        all_identifiers = list(set(data_set_identifier))
        not_attempted = list(
            set(all_identifiers) - set(self.attempted_identifiers))

        # Create a list of those not attempted
        missing_prev_study_list = {}
        merged_list_of_miss_by_study = []
        for prev_study in self.previous_studies:
            datas = MaternalDataset.objects.filter(
                protocol=prev_study,
                study_maternal_identifier__in=not_attempted)
            merged_list_of_miss_by_study += list(
                datas.values_list('study_maternal_identifier', 'protocol'))
            missing_prev_study_list[prev_study] = datas.count()

        # Create a list of attempted
        merged_list_of_attempts_by_study = []
        for prev_study in self.previous_studies:
            datas = MaternalDataset.objects.filter(
                protocol=prev_study,
                study_maternal_identifier__in=self.attempted_identifiers)
            merged_list_of_attempts_by_study += list(
                datas.values_list('study_maternal_identifier', 'protocol'))

        prev_study_list = {}
        total_attempts = 0
        for prev_study in self.previous_studies:
            datas = LogEntry.objects.filter(prev_study=prev_study).values_list(
                'study_maternal_identifier', flat=True)
            datas = list(set(datas))
            prev_study_list[prev_study] = len(datas)
            total_attempts += len(datas)

        # Add study totals and totals not attempted
        attempts_data = []
        for study, attempts in prev_study_list.items():
            dataset = MaternalDataset.objects.filter(protocol=study)
            attempts_data.append(
                [study, dataset.count(),
                 attempts, missing_prev_study_list.get(study)])


        dataset = MaternalDataset.objects.all()

        all_data = attempts_data + [
            ['All studies', dataset.count(),
             total_attempts, len(not_attempted)]]
        return all_data, total_attempts, len(not_attempted)

    @property
    def continued_contact_identifiers(self):
        """Returns a list of participants who are continued to be contacted.
        """
        continued_contact = []
        for identifier in self.attempted_identifiers:
            obj = LogEntry.objects.filter(
                study_maternal_identifier=identifier).order_by('-created')
            if obj:
                if obj[0].appt in ['thinking']:
                    continued_contact.append(identifier)
                elif obj[0].may_call == 'No' and not obj[0].appt in ['No']:
                    continued_contact.append(identifier)
            logs = LogEntry.objects.filter(
                phone_num_success=['none_of_the_above'],
                study_maternal_identifier=identifier).order_by('-created')
            if logs:
                if logs.count() <= 3:
                    if logs[0].final_contact == 'No':
                        continued_contact.append(identifier)
        continued_contact = list(set(continued_contact) - set(self.consented_identifiers))
        return continued_contact


    @property
    def to_call_df(self):
        """Return a dataframe for participants who are still being contacted.
        """
        qs = LogEntry.objects.filter(
            study_maternal_identifier__in=self.continued_contact_identifiers)

        df = read_frame(qs, fieldnames=[
            'prev_study', 'study_maternal_identifier'])
        df = df.drop_duplicates(subset=['study_maternal_identifier'])
        df = df.drop_duplicates(subset=['study_maternal_identifier'])
        return df

    def participants_to_call_again(self):
        """Return a report for participants who are still being contacted.
        """
        result = self.to_call_df
        total = 0
        prev_study_list = []
        for prev_study in self.previous_studies:
            df_prev = result[result['prev_study'] == prev_study]
            prev_study_list.append(
                [prev_study, df_prev[df_prev.columns[0]].count()])
            total += df_prev[df_prev.columns[0]].count()
        
        prev_study_list.append(['All studies', total])
        return prev_study_list, total

    @property
    def unreacheble_closed_identifiers(self):
        """Returns a list of participants that are not reacheble and 3 attempts
        have been made.
        """
        unreacheble = []
        for identifier in self.attempted_identifiers:
            logs = LogEntry.objects.filter(
                phone_num_success=['none_of_the_above'],
                study_maternal_identifier=identifier).order_by('-created')
            if logs.count() >= 3:
                if (logs[0].phone_num_success == ['none_of_the_above'] and
                    logs[1].phone_num_success == ['none_of_the_above'] and 
                    logs[2].phone_num_success == ['none_of_the_above'] and
                    logs[0].final_contact == 'Yes'):
                    unreacheble.append(identifier)
        unreacheble = list(set(unreacheble) - set(self.consented_identifiers))
        return unreacheble

    @property
    def not_reacheble_df(self):
        """"Returns a dataframe for participants who are not reacheble.
        """
        # Not reacheble participants
        qs = LogEntry.objects.filter(
            study_maternal_identifier__in=self.unreacheble_closed_identifiers)

        df = read_frame(qs, fieldnames=[
            'prev_study', 'study_maternal_identifier'])
        df = df.drop_duplicates(subset=['study_maternal_identifier'])
        return df


    def participants_not_reachable(self):
        """Returns a report for participants who are not reacheble.
        """
        df = self.not_reacheble_df
        prev_study_list = []
        total = 0
        for prev_study in self.previous_studies:
            df_prev = df[df['prev_study'] == prev_study]
            prev_study_list.append(
                [prev_study, df_prev[df_prev.columns[0]].count()])
            total += df_prev[df_prev.columns[0]].count()

        prev_study_list.append(['All studies', total])
        return prev_study_list, total

    @property
    def declined_identifiers(self):
        """Return identifiers of participants who declined to be part of the
        study.
        """
        # Declined from call log
        declined_do_not_call = LogEntry.objects.filter(
            study_maternal_identifier__in=self.attempted_identifiers,
            may_call__iexact='No').values_list(
                'study_maternal_identifier', flat=True)
        declined_do_not_call = list(set(declined_do_not_call))
        
        # Screening rejects
        screened_identifiers = ScreeningPriorBhpParticipants.objects.filter(
            flourish_participation='No').values_list(
                'study_maternal_identifier', flat=True)
        screened_identifiers = list(set(screened_identifiers))
        
        # Merge the 2 above lists
        identifiers = screened_identifiers + declined_do_not_call
        identifiers = list(set(identifiers) - set(self.consented_identifiers))
        return identifiers

    @property
    def declined_df(self):
        """Returns a dataframe for declined participants.
        """
        qs = MaternalDataset.objects.filter(
            study_maternal_identifier__in=self.declined_identifiers)
        df = read_frame(qs, fieldnames=[
            'protocol', 'study_maternal_identifier'])
        return df


    def declined(self):
        """Returns a report of declined participants.
        """
        df = self.declined_df
        prev_study_list = []
        total = 0
        for prev_study in self.previous_studies:
            df_prev = df[df['protocol'] == prev_study]
            prev_study_list.append(
                [prev_study, df_prev[df_prev.columns[0]].count()])
            total += df_prev[df_prev.columns[0]].count()

        prev_study_list.append(['All studies', total])

        return prev_study_list, total

    @property
    def consented_df(self):
        """Returns a data frame of consented participants.
        """
        qs = MaternalDataset.objects.filter(
            study_maternal_identifier__in=self.consented_identifiers)
        df = read_frame(qs, fieldnames=[
            'protocol', 'study_maternal_identifier'])
        df = df.drop_duplicates(subset=['study_maternal_identifier'])
        return df

    def consented(self):
        """Returns a report of consented participants.
        """
        df = self.consented_df
        prev_study_list = []
        total = 0
        for prev_study in self.previous_studies:
            df_prev = df[df['protocol'] == prev_study]
            prev_study_list.append(
                [prev_study, df_prev[df_prev.columns[0]].count()])
            total += df_prev[df_prev.columns[0]].count()

        prev_study_list.append(['All studies', total])
        return prev_study_list, total

    def df_transposer(self, elements=[]):
        """
        :param elements: Lists of list, for example:
        elements = [
            [4, 4],
            [4, 4, 1],
            [4, 4, 5, 5, 5, 5, 5, 5],
        ]
        """
        # df - represent the dataframe
        df = pd.DataFrame(data=elements).T
        df = df.fillna(0)
        return df

    @property
    def identifiers_summary_df(self):
        """Return a dataframe of a summary list dataframe of identifiers.
        """
        summary_list = [
            self.attempted_identifiers,
            self.continued_contact_identifiers,
            self.declined_identifiers,
            self.unreacheble_closed_identifiers,
            self.consented_identifiers]
        df = self.df_transposer(elements=summary_list)
        df.columns=[
            'Attempts', 'Continued Contact',
            'Declined', 'Unreacheble', 'Consented']
        
        print(df)
        return df
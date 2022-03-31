import pandas as pd

from flourish_reports.classes import RecruitmentReport


class SummaryReport:


    report_cls = RecruitmentReport()

    @property
    def pre_study_data(self):
        """Returns a data frame of all previous study data participant counts.
        """
        df_all_data = pd.DataFrame(self.report_cls.caregiver_prev_study_dataset()[0], columns=['Previous Studies', 'Dataset Totals'])
        return df_all_data
        
    @property
    def locator_data(self):
        """Returns all previous study locator data starts.
        """
        locator_report = self.report_cls.locator_report()
        expected = locator_report[0]
        existing = locator_report[1]
        missing = locator_report[2]
        expected.pop(0)
        existing.pop(0)
        missing.pop(0)

        prev_studies = self.report_cls.previous_studies + ['All studies']
        data = []
        x = 0
        while x < 6:
            data.append([
                prev_studies[x],
                expected[x],
                existing[x],
                missing[x]
            ])
            x += 1
        df_locator = pd.DataFrame(data, columns=['Previous Studies', 'Expected Locator', 'Existing Locator', 'Missing Locator'])
        return df_locator

    @property
    def randomisation(self):
        """Returns a participant data frame with randomisation starts.
        """
        randomisation = self.report_cls.worklist_report()
        missing_worklist = randomisation[2]
        randomised = randomisation[3]
        not_randomised = randomisation[4]

        missing_worklist.pop(0)
        randomised.pop(0)
        not_randomised.pop(0)

        prev_studies = self.report_cls.previous_studies + ['All studies']
        data = []
        x = 0
        while x < 6:
            data.append([
                prev_studies[x],
                missing_worklist[x],
                randomised[x],
                not_randomised[x]
            ])
            x += 1
        df_randomised = pd.DataFrame(data, columns=['Previous Studies', 'Missing On Worklist', 'Randomised', 'Not Randomised'])
        return df_randomised

    @property
    def attempts_data(self):
        """Returns a data frame for attempts made to call participants for all studies.
        """
        attempts_report_data = self.report_cls.attempts_report_data()
        data = []
        for dt in attempts_report_data[0]:
            data.append([dt[0], dt[2], dt[3]])

        df_attempts = pd.DataFrame(data, columns=['Previous Studies', 'Total Atempts', 'Total Not Attempted'])
        return df_attempts

    @property
    def continued_contact(self):
        """Return a data frame for all participants who are still being contacted.
        """
        continued_contact = self.report_cls.participants_to_call_again()[0]
        df_continued_contact = pd.DataFrame(continued_contact, columns=['Previous Studies', 'Continued Contact'])
        return df_continued_contact
        
    @property
    def not_reacheble(self):
        """Returns a data frame for participants who are not reacheble.
        """
        not_reacheble = self.report_cls.participants_not_reachable()[0]
        df_not_reacheble = pd.DataFrame(not_reacheble, columns=['Previous Studies', 'Not Reacheble'])
        return df_not_reacheble
        
    @property
    def declined(self):
        """Returns a data frame of participants who declined study participation.
        """
        declined = self.report_cls.declined()[0]
        df_declined = pd.DataFrame(declined, columns=['Previous Studies', 'Declined'])
        return df_declined
        
    @property
    def consented(self):
        """Returns a data frame for paarticipants who have been consented into the study.
        """
        consented = self.report_cls.consented()[0]
        df_consented = pd.DataFrame(consented, columns=['Previous Studies', 'Consented'])
        return df_consented
     
    @property
    def summary_report(self):
        """Return a summary report of all startistics.
        """
        result_all_datan_locator = pd.merge(self.pre_study_data, self.locator_data, on='Previous Studies')
        result_randomised_n_attempts = pd.merge(self.randomisation, self.attempts_data, on='Previous Studies')
        result_cont_contact_n_unreacheble = pd.merge(self.continued_contact, self.not_reacheble, on='Previous Studies')
        result_declined_n_consented = pd.merge(self.declined, self.consented, on='Previous Studies')
        result_merge1 = pd.merge(result_all_datan_locator, result_randomised_n_attempts, on='Previous Studies')
        result_merge2 = pd.merge(result_cont_contact_n_unreacheble, result_declined_n_consented, on='Previous Studies')
        result = pd.merge(result_merge1, result_merge2, on='Previous Studies')
        return result
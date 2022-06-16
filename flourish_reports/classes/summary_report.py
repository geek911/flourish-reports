import pandas as pd

from flourish_reports.classes import RecruitmentReport
from ..models import RecruitmentStats


class SummaryReport:

    def __init__(self, study_stats=None):
        self.prev_study_data = []
        self.previous_studies = []

        self.total_expected = []
        self.total_missing = []
        self.total_existing = []

        self.declined_data = []
        self.consented_data = []
        self.participants_not_reachable = []
        self.participants_to_call_again = []
        self.attempts_data = []

        self.expected_worklist = []
        self.existing_worklist = []
        self.missing_worklist = []
        self.randomised = []
        self.not_randomised = []
        for stats in study_stats:
            self.prev_study_data.append([stats.study, stats.dataset_total])
            self.previous_studies.append(stats.study)
            self.total_expected.append(stats.expected_locator)
            self.total_missing.append(stats.missing_locator)
            self.total_existing.append(stats.existing_locator)
            self.declined_data.append([stats.study, stats.declined])
            self.consented_data.append([stats.study, stats.consented])

            self.participants_not_reachable.append(
                    [stats.study, stats.not_reacheble])
            self.participants_to_call_again.append(
                    [stats.study, stats.participants_to_call])

            self.attempts_data.append(
                    [stats.study, stats.study_participants,
                     stats.total_attempts, stats.total_not_attempted])

            self.expected_worklist.append(stats.expected_worklist)
            self.existing_worklist.append(stats.existing_worklist)
            self.missing_worklist.append(stats.missing_worklist)
            self.randomised.append(stats.randomised)
            self.not_randomised.append(stats.not_randomised)

    @property
    def pre_study_data(self):
        """Returns a data frame of all previous study data participant counts.
        """
        df_all_data = pd.DataFrame(self.prev_study_data, columns=['Previous Studies', 'Dataset Totals'])

        return df_all_data

    @property
    def locator_data(self):
        """Returns all previous study locator data starts.
        """
        data = []
        for x in range(len(self.previous_studies)):
            data.append([
                self.previous_studies[x],
                self.total_expected[x],
                self.total_existing[x],
                self.total_missing[x]
            ])
        df_locator = pd.DataFrame(data, columns=['Previous Studies', 'Expected Locator', 'Existing Locator', 'Missing Locator'])
        return df_locator

    @property
    def randomisation(self):
        """Returns a participant data frame with randomisation starts.
        """
        data = []
        for x in range(len(self.previous_studies)):
            data.append([
                self.previous_studies[x],
                self.missing_worklist[x],
                self.randomised[x],
                self.not_randomised[x]
            ])
        df_randomised = pd.DataFrame(data, columns=['Previous Studies', 'Missing On Worklist', 'Randomised', 'Not Randomised'])
        return df_randomised

    @property
    def total_attempts_data(self):
        """Returns a data frame for attempts made to call participants for all studies.
        """
        data = []
        for dt in self.attempts_data:
            data.append([dt[0], dt[2], dt[3]])

        df_attempts = pd.DataFrame(data, columns=['Previous Studies', 'Total Atempts', 'Total Not Attempted'])
        return df_attempts

    @property
    def continued_contact(self):
        """Return a data frame for all participants who are still being contacted.
        """
        df_continued_contact = pd.DataFrame(self.participants_to_call_again, columns=['Previous Studies', 'Continued Contact'])
        return df_continued_contact

    @property
    def not_reacheble(self):
        """Returns a data frame for participants who are not reacheble.
        """
        df_not_reacheble = pd.DataFrame(self.participants_not_reachable, columns=['Previous Studies', 'Not Reacheble'])
        return df_not_reacheble

    @property
    def total_declined(self):
        """Returns a data frame of participants who declined study participation.
        """
        df_declined = pd.DataFrame(self.declined_data, columns=['Previous Studies', 'Declined'])
        return df_declined

    @property
    def total_consented(self):
        """Returns a data frame for paarticipants who have been consented into the study.
        """
        df_consented = pd.DataFrame(self.consented_data, columns=['Previous Studies', 'Consented'])
        return df_consented

    @property
    def summary_report(self):
        """Return a summary report of all startistics.
        """
        result_all_datan_locator = pd.merge(self.pre_study_data, self.locator_data, on='Previous Studies')
        result_randomised_n_attempts = pd.merge(self.randomisation, self.total_attempts_data, on='Previous Studies')
        result_cont_contact_n_unreacheble = pd.merge(self.continued_contact, self.not_reacheble, on='Previous Studies')
        result_declined_n_consented = pd.merge(self.total_declined, self.total_consented, on='Previous Studies')
        result_merge1 = pd.merge(result_all_datan_locator, result_randomised_n_attempts, on='Previous Studies')
        result_merge2 = pd.merge(result_cont_contact_n_unreacheble, result_declined_n_consented, on='Previous Studies')
        result = pd.merge(result_merge1, result_merge2, on='Previous Studies')
        return result

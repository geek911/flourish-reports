from ..classes import RecruitmentReport
from ..models import (
    RecruitmentStats, TotalRecruitmentStats, PieTotalStats)


class GenerateStudyData:

    def populate_previous_study_data(self):
        reports = RecruitmentReport()

        previous_studies = reports.previous_studies
        previous_studies.append('All studies')
        caregiver_prev_study_dataset = reports.caregiver_prev_study_dataset()
        locator_report = reports.locator_report()
        worklist_report = reports.worklist_report()
        attempts_report_data, total_attempts, not_attempted = reports.attempts_report_data()
        participants_to_call_again, total_participants_to_call_again = reports.participants_to_call_again()
        participants_not_reachable, total_participants_not_reachable = reports.participants_not_reachable()
        declined_reports, total_decline = reports.declined()
        consented_reports, total_consented = reports.consented()
        offstudy_reports, total_offstudy = reports.offstudy()
        dataset, pie = caregiver_prev_study_dataset

        TotalRecruitmentStats.objects.all().delete()
        PieTotalStats.objects.all().delete()
        PieTotalStats.objects.create(
            mpepu=pie.mpepu,
            tshipidi=pie.tshipidi,
            mashi=pie.mashi,
            mma_bana=pie.mma_bana,
            tshilo_dikotla=pie.tshilo_dikotla,
            total_continued_contact=pie.total_continued_contact,
            total_decline_uninterested=pie.total_decline_uninterested,
            total_consented=pie.total_consented,
            total_unable_to_reach=pie.total_unable_to_reach
        )
        TotalRecruitmentStats.objects.create(
            total_attempts=total_attempts,
            not_attempted=not_attempted,
            total_participants_to_call_again=total_participants_to_call_again,
            total_participants_not_reachable=total_participants_not_reachable,
            total_decline=total_decline,
            total_consented=total_consented
        )
        for i in range(len(previous_studies)):
            dataset_total = dataset[i][1]
            # array data [['Total Expected', 751, 387, 2490, 94, 564, 4286], ['Total Existing', 737, 387, 2436, 86, 544, 4190], ['Total Missing', 14, 0, 54, 8, 20, 96]]
            # split and get array index 0 expected locator
            # get study value at index i+1 (skip index i = 0 and starts at i+1)
            expected_locator = locator_report[0][i+1]
            existing_locator = locator_report[1][i+1]
            missing_locator = locator_report[2][i+1]

            expected_worklist = worklist_report[0][i+1]
            existing_worklist = worklist_report[1][i+1]
            missing_worklist = worklist_report[2][i+1]
            randomised = worklist_report[3][i+1]
            not_randomised = worklist_report[4][i+1]

            # [['Tshipidi', 751, 514, 236], ['Tshilo Dikotla', 387, 344, 43], ['Mpepu', 2490, 1790, 700], ['Mashi', 94, 70, 24], ['Mma Bana', 564, 481, 82], ['All studies', 4286, 3199, 1085]], 3199, 1085)
            study_participants = attempts_report_data[i][1]
            total_attempts = attempts_report_data[i][2]
            total_not_attempted = attempts_report_data[i][3]

            # [['Tshipidi', 6], ['Tshilo Dikotla', 0], ['Mpepu', 29], ['Mashi', 0], ['Mma Bana', 33], ['All studies', 68]]
            not_reacheble = participants_not_reachable[i][1]

            # [['Tshipidi', 6], ['Tshilo Dikotla', 0], ['Mpepu', 29], ['Mashi', 0], ['Mma Bana', 33], ['All studies', 68]]
            participants_to_call = participants_to_call_again[i][1]

            # [['Tshipidi', 6], ['Tshilo Dikotla', 0], ['Mpepu', 29], ['Mashi', 0], ['Mma Bana', 33], ['All studies', 68]]
            declined = declined_reports[i][1]

            # [['Tshipidi', 6], ['Tshilo Dikotla', 0], ['Mpepu', 29], ['Mashi', 0], ['Mma Bana', 33], ['All studies', 68]]
            consented = consented_reports[i][1]
            offstudy = offstudy_reports[i][1]

            defaults = {
                'dataset_total': dataset_total,
                'expected_locator': expected_locator,
                'existing_locator': existing_locator,
                'missing_locator': missing_locator,
                'missing_worklist': missing_worklist,
                'existing_worklist': existing_worklist,
                'expected_worklist': expected_worklist,
                'randomised': randomised,
                'not_randomised': not_randomised,
                'study_participants': study_participants,
                'total_attempts': total_attempts,
                'total_not_attempted': total_not_attempted,
                'not_reacheble': not_reacheble,
                'participants_to_call': participants_to_call,
                'declined': declined,
                'consented': consented,
                'offstudy': offstudy
            }
            study = previous_studies[i]
            RecruitmentStats.objects.update_or_create(
                study=study,
                defaults=defaults
            )

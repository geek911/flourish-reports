from django.contrib.auth.models import User
from datetime import datetime
from django.db.models import Q

from flourish_follow.models import LogEntry
from flourish_caregiver.models import (
    ScreeningPriorBhpParticipants, SubjectConsent)


class UserRecruitmentReportMixin:

    def calls_contacted(self, username=None, start_date=None, end_date=None):
        """Return number of contacted participants.
        """
        call_contacted = 0

        if start_date and end_date and username:
            # start_date = datetime.strptime(start_date, '%Y-%m-%d')
            # end_date = datetime.strptime(end_date, '%Y-%m-%d')

            call_contacted = LogEntry.objects.filter(
                user_created=username,
                created__gte=start_date,
                created__lte=end_date).values_list(
                'study_maternal_identifier').distinct().count()

            # import pdb;
            # pdb.set_trace()
        else:
            call_contacted = LogEntry.objects.filter(
                user_created=username).values_list(
                'study_maternal_identifier').distinct().count()
        return call_contacted

    def successful_calls(self, username, start_date=None, end_date=None):
        """Returns number of successful calls.
        """
        successful = 0
        if start_date and end_date:
            successful = LogEntry.objects.filter(
                ~Q(phone_num_success=['none_of_the_above']),
                user_created=username,
                created__gte=start_date,
                created__lte=end_date,
                phone_num_success__isnull=False).values_list(
                'study_maternal_identifier').distinct().count()
        else:
            successful = LogEntry.objects.filter(
                ~Q(phone_num_success=['none_of_the_above']),
                user_created=username,
                phone_num_success__isnull=False, ).values_list(
                'study_maternal_identifier').distinct().count()
        return successful

    def unsuccessful_calls(self, username, start_date=None, end_date=None):
        """Returns number of unsuccessful calls.
        """
        unsuccessful = 0
        if start_date and end_date:

            unsuccessful = LogEntry.objects.filter(
                Q(phone_num_success__isnull=True) | Q(phone_num_success=['none_of_the_above']),
                user_created=username,
                created__gte=start_date,
                created__lte=end_date).values_list(
                'study_maternal_identifier').distinct().count()



            test = LogEntry.objects.filter(
                user_created=username,
                phone_num_success=['none_of_the_above'],
                created__gte=start_date,
                created__lte=end_date)


        else:
            unsuccessful = LogEntry.objects.filter(
                Q(phone_num_success__isnull=True) | Q(phone_num_success=['none_of_the_above']),
                user_created=username).values_list(
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
                created__gte=start_date,
                created__lte=end_date, ).values_list(
                'study_maternal_identifier').distinct().count()
        else:
            accepting = LogEntry.objects.filter(
                Q(appt_date__isnull=False) | Q(appt='Yes'),
                user_created=username).values_list(
                'study_maternal_identifier').distinct().count()
        return accepting

    def conversion_calls(self, username, start_date=None, end_date=None):
        """Returns a list of calls that resulted in consents.
        """
        conversion_logs = []
        if start_date and end_date:
            conversion_logs = LogEntry.objects.filter(
                user_created=username,
                created__gte=start_date,
                created__lte=end_date, ).values_list(
                'study_maternal_identifier', flat=True)
        else:
            conversion_logs = LogEntry.objects.filter(
                user_created=username).values_list(
                'study_maternal_identifier', flat=True)
        conversion_list = list(set(conversion_logs))
        screening_list = ScreeningPriorBhpParticipants.objects.filter(
            study_maternal_identifier__in=conversion_list).values_list(
            'screening_identifier', flat=True)
        screening_list = list(set(screening_list))
        conversion = SubjectConsent.objects.filter(
            screening_identifier__in=screening_list).values_list(
            'screening_identifier', flat=True)
        conversion = list(set(conversion))
        return len(conversion)

    def recruitment(self, username=None, start_date=None, end_date=None):
        """Return a recruitment report.
        """
        report = []
        totals = []
        recruiters = User.objects.filter(groups__name='Recruiters')
        t_contacted = 0
        t_successful = 0
        t_unsuccessful = 0
        t_accepting = 0
        t_conversion = 0
        if username and not username == '-----':
            recruiters = User.objects.filter(username=username)
        for recruiter in recruiters:
            username = recruiter.username
            if start_date and end_date:
                call_contacted = self.calls_contacted(
                    username, start_date=start_date, end_date=end_date)
                successful = self.successful_calls(
                    username, start_date=start_date, end_date=end_date)
                unsuccessful = self.unsuccessful_calls(
                    username, start_date=start_date, end_date=end_date)
                accepting = self.accepting_apps(
                    username, start_date=start_date, end_date=end_date)
                conversion = self.conversion_calls(
                    username, start_date=start_date, end_date=end_date)
                if conversion:
                    conversion_percentage = (conversion / call_contacted) * 100
                else:
                    conversion_percentage = 0
                report.append(
                    [recruiter.first_name + ' ' + recruiter.last_name,
                     call_contacted,
                     successful,
                     unsuccessful,
                     accepting,
                     conversion,
                     conversion_percentage])
                # Update totals
                t_contacted += call_contacted
                t_successful += successful
                t_unsuccessful += unsuccessful
                t_accepting += accepting
                t_conversion += conversion
            else:
                call_contacted = self.calls_contacted(username)
                successful = self.successful_calls(username)
                unsuccessful = self.unsuccessful_calls(username)
                accepting = self.accepting_apps(username)
                conversion = self.conversion_calls(username)
                if conversion:
                    conversion_percentage = (conversion / call_contacted) * 100
                else:
                    conversion_percentage = 0
                report.append(
                    [recruiter.first_name + ' ' + recruiter.last_name,
                     call_contacted,
                     successful,
                     unsuccessful,
                     accepting,
                     conversion,
                     conversion_percentage])
                # Update totals
                t_contacted += call_contacted
                t_successful += successful
                t_unsuccessful += unsuccessful
                t_accepting += accepting
                t_conversion += conversion
        totals.append(t_contacted)
        totals.append(t_successful)
        totals.append(t_unsuccessful)
        totals.append(t_accepting)
        totals.append(t_conversion)
        return [totals, report]

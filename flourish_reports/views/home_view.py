import os
import datetime
from django_pandas.io import read_frame
import pandas as pd


from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.urls.base import reverse
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from edc_base.view_mixins import EdcBaseViewMixin
from edc_navbar import NavbarViewMixin

from flourish_follow.models import LogEntry
from flourish_caregiver.models import (
    ScreeningPriorBhpParticipants, SubjectConsent)
from ..forms import RecruitmentReportForm
from ..models import ExportFile
from ..identifiers import ExportIdentifier


class DownloadReportMixin:
    
    def download_data(
            self, description=None, start_date=None,
            end_date=None, report_type=None, df=None):
        """Export all data.
        """

        export_identifier = ExportIdentifier().identifier

        options = {
            'description': description,
            'export_identifier': export_identifier,
            'start_date': start_date,
            'end_date': end_date
        }
        doc = ExportFile.objects.create(**options)
        
        # Document path
        upload_to = ExportFile.document.field.upload_to
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        fname = export_identifier + '_' + timestamp + '.csv'
        final_path = upload_to  + report_type +'/' + fname
         
        # Export path 
        export_path = settings.MEDIA_ROOT + '/documents/' + report_type +'/'
        if not os.path.exists(export_path):
            os.makedirs(export_path)
        export_path += fname
        df.to_csv(export_path, encoding='utf-8', index=False)

        doc.document = final_path
        doc.save()


class HomeView(
        DownloadReportMixin,
        EdcBaseViewMixin, NavbarViewMixin,
        TemplateView, FormView):

    form_class = RecruitmentReportForm
    template_name = 'flourish_reports/home.html'
    navbar_name = 'flourish_reports'
    navbar_selected_item = 'flourish_reports'

    def get_success_url(self):
        return reverse('flourish_reports:home_url')

    def calls_contacted(self, username, start_date=None, end_date=None):
        """Return number of contacted participants.
        """
        call_contacted = 0
        if start_date and end_date:
            call_contacted = LogEntry.objects.filter(
                        user_created=username,
                        created__date__gte=start_date,
                        created__date__lte=end_date).values_list(
                            'study_maternal_identifier').distinct().count()
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

    def conversion_calls(self, username, start_date=None, end_date=None):
        """Returns a list of calls that resulted in consents.
        """
        conversion_logs = []
        if start_date and end_date:
            conversion_logs = LogEntry.objects.filter(
                user_created=username,
                created__date__gte=start_date,
                created__date__lte=end_date,).values_list(
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
                successful = self.calls_contacted(
                    username, start_date=start_date, end_date=end_date)
                unsuccessful = self.unsuccessful_calls(
                    username, start_date=start_date, end_date=end_date)
                accepting = self.accepting_apps(
                    username, start_date=start_date, end_date=end_date)
                conversion = self.conversion_calls(
                    username, start_date=start_date, end_date=end_date)
                if conversion:
                    conversion_percentage = (conversion/call_contacted)*100
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
                successful = self.calls_contacted(username)
                unsuccessful = self.unsuccessful_calls(username)
                accepting = self.accepting_apps(username)
                conversion = self.conversion_calls(username)
                if conversion:
                    conversion_percentage = (conversion/call_contacted)*100
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

    def management_report(self, start_date=None, end_date=None):
        """Returns RA report for management.
        """
        qs = LogEntry.objects.filter(
            created__date__gte=start_date,
            created__date__lte=end_date)
        df = read_frame(qs, fieldnames=[
            'user_created', 'screening_identifier', 'prev_study',
            'call_datetime', 'appt', 'appt_reason_unwilling', 'appt_date'])
        return df

    def form_valid(self, form):
        if form.is_valid():
            start_date = form.data['start_date']
            end_date = form.data['end_date']
            recruitment = self.recruitment(
                start_date=start_date, end_date=end_date)
            totals = [['Totals'] + recruitment[0]]
            data = recruitment[1] + totals
            if 'rdownload_report' in self.request.POST:
                self.download_data(
                    description='Recruitment Productivity Report',
                    start_date=start_date, end_date=end_date,
                    report_type='recruitment_productivity_reports',
                    df=pd.DataFrame(data))
            elif 'mdownload_report' in self.request.POST:
                df = self.management_report(
                    start_date=start_date, end_date=end_date)
                self.download_data(
                    description='Management Report',
                    start_date=start_date, end_date=end_date,
                    report_type='management_reports', df=df)
            management_report_downloads = ExportFile.objects.filter(
                description='Management Report').order_by('uploaded_at')
            recruitment_downloads = ExportFile.objects.filter(
                description='Recruitment Productivity Report').order_by('uploaded_at')
            context = self.get_context_data(**self.kwargs)
            context.update(
                management_report_downloads=management_report_downloads,
                recruitment_downloads=recruitment_downloads,
                form=form,
                recruitment=recruitment)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        management_report_downloads = ExportFile.objects.filter(
            description='Management Report').order_by('uploaded_at')
        recruitment_downloads = ExportFile.objects.filter(
            description='Recruitment Productivity Report').order_by('uploaded_at')
        # Recruitment report
        recruitment = self.recruitment()
        context.update(
            management_report_downloads=management_report_downloads,
            recruitment_downloads=recruitment_downloads,
            recruitment=recruitment)
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

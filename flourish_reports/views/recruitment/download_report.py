from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls.base import reverse
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from edc_base.view_mixins import EdcBaseViewMixin
from edc_navbar import NavbarViewMixin

from ...classes import RecruitmentReport
from ..view_mixins import DownloadReportMixin
from ...models import ExportFile 


class DownloadReportView(EdcBaseViewMixin, DownloadReportMixin,
                            NavbarViewMixin, TemplateView, LoginRequiredMixin):
    template_name = 'flourish_reports/recruit/download_reports.html'
    navbar_name = 'flourish_reports'
    navbar_selected_item = 'flourish_reports'

    def get_success_url(self):
        return reverse('flourish_reports:download_report_url')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        reports = RecruitmentReport()
        
        # Download reports
        download = self.request.GET.get('download', None)
        if download == "locator":
            self.download_data(description="Locator Data",  report_type="Locator Data", df=reports.locator_df)
        elif download == "worklist_data":
            self.download_data(description="Worklist Study Data",  report_type="Worklist Study Data", df=reports.randomised_df)
        elif download == "call_attempts":
            self.download_data(description="Call Attempts Data",  report_type="Call Attempts Data", df=reports.attempts_df)
        elif download == "continued_contact":
            self.download_data(description="Continued Contact Data", report_type="Continued Contact Data", df=reports.to_call_df)
        elif download == "not_reacheble":
            self.download_data(description="Not Reacheble  Data",  report_type="Not Reacheble  Data", df=reports.not_reacheble_df)
        elif download == "declined":
            self.download_data(description="Declined  Data",  report_type="Declined  Data", df=reports.declined_df)
        elif download == "consented":
            self.download_data(description="Consented  Data",  report_type="Consented  Data", df=reports.consented_df)
        elif download == "summary":
            self.download_data(description="Summary  Data",  report_type="Summary  Data", df=reports.identifiers_summary_df)
        
        
        # Downloaed files
        locator_data_downloads = ExportFile.objects.filter(
                description="Locator Data").order_by('uploaded_at')
        worklist_data_downloads = ExportFile.objects.filter(
                description="Worklist Study Data").order_by('uploaded_at')
        call_attempts_data_downloads = ExportFile.objects.filter(
                description="Call Attempts Data").order_by('uploaded_at')
        continued_contact_data_downloads = ExportFile.objects.filter(
                description="Continued Contact Data").order_by('uploaded_at')
        not_reacheble_data_downloads = ExportFile.objects.filter(
                description="Not Reacheble  Data").order_by('uploaded_at')
        declined_data_downloads = ExportFile.objects.filter(
                description="Declined  Data").order_by('uploaded_at')
        consented_data_downloads = ExportFile.objects.filter(
                description="Consented  Data").order_by('uploaded_at')
        summary_data_downloads = ExportFile.objects.filter(
                description="Summary  Data").order_by('uploaded_at')
        context.update(
            # Downloads
            locator_data_downloads=locator_data_downloads,
            worklist_data_downloads=worklist_data_downloads,
            call_attempts_data_downloads=call_attempts_data_downloads,
            not_reacheble_data_downloads=not_reacheble_data_downloads,
            declined_data_downloads=declined_data_downloads,
            consented_data_downloads=consented_data_downloads,
            continued_contact_data_downloads=continued_contact_data_downloads,
            summary_data_downloads=summary_data_downloads,
        )
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

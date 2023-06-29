from django.urls import path
from edc_dashboard import UrlConfig
from .admin_site import flourish_reports_admin
from .views import (
    EnrolmentReportView, RecruitmentReportView,
    DownloadReportView, MissingCrfReportView, MissingCrfDetailedReport)


app_name = 'flourish_reports'

urlpatterns = [
    path('admin/', flourish_reports_admin.urls),
    path('recruitment', RecruitmentReportView.as_view(), name='recruitment_report_url'),
    path('download', DownloadReportView.as_view(), name='download_report_url'),
    path('enrolment', EnrolmentReportView.as_view(), name='enrolment_report_url'),
    path('missing_crf_detailed_report/<id>',
         MissingCrfDetailedReport.as_view(), name='missing_crf_detailed_report_url'),
]


missing_crf_report_listboard_url_config = UrlConfig(
    url_name='missing_crf_report_url',
    view_class=MissingCrfReportView,
    label='missing_crf_report',
    identifier_label='missing_crf_report_url')


urlpatterns += missing_crf_report_listboard_url_config.listboard_urls

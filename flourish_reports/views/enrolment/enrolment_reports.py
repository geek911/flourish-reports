from collections import Counter
from django.apps import apps as django_apps
from django_pandas.io import read_frame
from django.utils.safestring import mark_safe

import pandas as pd

from django.contrib.auth.decorators import login_required
from django.urls.base import reverse
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from edc_base.view_mixins import EdcBaseViewMixin
from edc_navbar import NavbarViewMixin

from ...forms import EnrolmentReportForm
from ...models import ExportFile

from ..view_mixins import DownloadReportMixin

from flourish_follow.models import LogEntry
from flourish_caregiver.models import CaregiverChildConsent


class EnrolmentReportMixin:

    child_consents_cls = django_apps.get_model('flourish_caregiver.caregiverchildconsent')
    maternal_dataset_cls = django_apps.get_model('flourish_caregiver.maternaldataset')
    child_dataset_cls = django_apps.get_model('flourish_child.childdataset')
    registered_subject_cls = django_apps.get_model('edc_registration.registeredsubject')

    def cohort_report(self, start_date=None, end_date=None):
        """Return a total enrolment per cohort.
        """
        if start_date and end_date:
            consents = CaregiverChildConsent.objects.filter(
                created__date__gte=start_date,
                created__date__lte=end_date).values_list(
                    'cohort', flat=True)
        else:
            consents = CaregiverChildConsent.objects.all().values_list(
                    'cohort', flat=True)
        cohorts = Counter(consents)
        report = {}
        c_dict = {
            'cohort_a': 'Cohort A',
            'cohort_b': 'Cohort B',
            'cohort_c': 'Cohort C',
            'cohort_a_sec': 'Cohort A Secondary Aims',
            'cohort_b_sec': 'Cohort B Secondary Aims',
            'cohort_c_sec': 'Cohort C Secondary Aims',
            'cohort_pool': 'Cohort Pool'
            }
        for key, value in cohorts.items():
            if key:
                new_key = c_dict[key]
                report[new_key] = value
        return sorted(report)

    def cohort_a(self, start_date=None, end_date=None):
        """Returns totals for cohort A.
        """
        cohort_a_identifiers = self.child_consents_cls.objects.filter(
            cohort='cohort_a').values_list(
                'subject_consent__screening_identifier')

        study_maternal_identifiers = self.maternal_dataset_cls.objects.values_list(
            'study_maternal_identifier', flat=True).filter(
                screening_identifier__in=cohort_a_identifiers)

        heu_count = self.child_dataset_cls.objects.filter(
            study_maternal_identifier__in=study_maternal_identifiers,
            infant_hiv_exposed='Exposed').count()

        huu_count = self.child_dataset_cls.objects.filter(
            study_maternal_identifier__in=study_maternal_identifiers,
            infant_hiv_exposed='Unexposed').count()

        ante_enrol_cls = django_apps.get_model('flourish_caregiver.antenatalenrollment')
        ante_enrol_count = ante_enrol_cls.objects.all().count()

        cohort_a_dict = {
            'preg_woman': ante_enrol_count,
            'HEU': heu_count,
            'HUU': huu_count
            }
        return cohort_a_dict

    def cohort_b(self, start_date=None, end_date=None):
        """Returns totals for cohort B.
        """

        cohort_a_identifiers = self.child_consents_cls.objects.filter(
            cohort='cohort_b').values_list(
                'subject_consent__screening_identifier')

        study_maternal_identifiers = self.maternal_dataset_cls.objects.values_list(
            'study_maternal_identifier', flat=True).filter(
                screening_identifier__in=cohort_a_identifiers)

        preg_efv_count = self.maternal_dataset_cls.objects.filter(
            study_maternal_identifier__in=study_maternal_identifiers,
            preg_efv=1).count()

        preg_dtg_count = self.maternal_dataset_cls.objects.filter(
            study_maternal_identifier__in=study_maternal_identifiers,
            preg_dtg=1).count()

        hiv_preg_count = self.maternal_dataset_cls.objects.filter(
            study_maternal_identifier__in=study_maternal_identifiers,
            mom_hivstatus='HIV-infected').count()

        cohort_b_dict = {
            'EFV': preg_efv_count,
            'DTG': preg_dtg_count,
            'HIV-Preg': hiv_preg_count
            }
        return cohort_b_dict

    def cohort_c(self, start_date=None, end_date=None):
        """Returns totals for cohort C.
        """

        cohort_c_identifiers = self.child_consents_cls.objects.filter(
            cohort='cohort_b').values_list(
                'subject_consent__screening_identifier')

        study_maternal_identifiers = self.maternal_dataset_cls.objects.values_list(
            'study_maternal_identifier', flat=True).filter(
                screening_identifier__in=cohort_c_identifiers)

        huu_count = self.child_dataset_cls.objects.filter(
            study_maternal_identifier__in=study_maternal_identifiers,
            infant_hiv_exposed='Unexposed').count()

        preg_pi_count = self.maternal_dataset_cls.objects.filter(
            study_maternal_identifier__in=study_maternal_identifiers,
            preg_pi=1).count()

        cohort_c_dict = {
            'HUU': huu_count,
            'PI': preg_pi_count,
            }
        return cohort_c_dict

    def sec_aims(self, start_date=None, end_date=None):
        """Returns totals for Secondary Aims.
        """
        cohort_sec_identifiers = self.child_consents_cls.objects.filter(
            cohort__icontains='sec').values_list(
                'subject_consent__screening_identifier')

        study_maternal_identifiers = self.maternal_dataset_cls.objects.values_list(
            'study_maternal_identifier', flat=True).filter(
                screening_identifier__in=cohort_sec_identifiers)

        hiv_preg_count = self.maternal_dataset_cls.objects.filter(
            study_maternal_identifier__in=study_maternal_identifiers,
            mom_hivstatus='HIV-infected').count()

        hiv_neg_preg_count = self.maternal_dataset_cls.objects.filter(
            study_maternal_identifier__in=study_maternal_identifiers,
            mom_hivstatus='HIV-uninfected').count()

        cohort_sec_dict = {
            'WLHIV': hiv_preg_count,
            'HIV -': hiv_neg_preg_count
            }
        return cohort_sec_dict

    def subject_crfs_missing(self):
        crfmetadata = django_apps.get_model('edc_metadata.crfmetadata')
        registered_identifiers = self.registered_subject_cls.objects.all().values_list(
            'subject_identifier', flat=True)
        required_crfs = crfmetadata.objects.filter(
            subject_identifier__in=registered_identifiers, entry_status='REQUIRED')
        data = [(qs.subject_identifier, qs.schedule_name, qs.visit_code,
                 qs.visit_code_sequence, qs.verbose_name) for qs in required_crfs]
        df = pd.DataFrame.from_records(
            data,
            columns=['Subject Identifier', 'Schedule Name', 'Visit Code', 'Timepoint', 'CRF name'])
        if not df.empty:
            grouped = df.groupby(['Subject Identifier', 'Schedule Name',
                                  'Visit Code', 'Timepoint'])
            grouped = grouped['CRF name'].apply(
                lambda group_series: group_series.tolist()).reset_index()
            groups_html = grouped.to_html()
            groups_html = groups_html.replace(
                '<table border="1" class="dataframe">',
                '<table id="missing-crfs" class="table table-striped table-bordered"'
                'cellspacing="0" width="100%">')
            return groups_html
        return 'No missing forms'


class EnrolmentReportView(
        DownloadReportMixin, EnrolmentReportMixin,
        EdcBaseViewMixin, NavbarViewMixin,
        TemplateView, FormView):

    form_class = EnrolmentReportForm
    template_name = 'flourish_reports/enrolment_reports.html'
    navbar_name = 'flourish_reports'
    navbar_selected_item = 'enrolment_reports'

    def get_success_url(self):
        return reverse('flourish_reports:enrolment_report_url')

    def form_valid(self, form):
        if form.is_valid():
            start_date = form.data['start_date']
            end_date = form.data['end_date']
            data = []
            cohort_report = self.cohort_report(
                start_date=start_date,
                end_date=end_date)
            cohort_a = self.cohort_a(
                start_date=start_date,
                end_date=end_date)
            cohort_b = self.cohort_b(
                start_date=start_date,
                end_date=end_date)
            cohort_c = self.cohort_c(
                start_date=start_date,
                end_date=end_date)
            sec_aims = self.sec_aims(
                start_date=start_date,
                end_date=end_date)
            if 'rdownload_report' in self.request.POST:
                self.download_data(
                    description='Enrolment Report',
                    start_date=start_date, end_date=end_date,
                    report_type='enrolment_reports',
                    df=pd.DataFrame(data))
            enrolment_downloads = ExportFile.objects.filter(
                description='Enrolment Report').order_by('uploaded_at')
            context = self.get_context_data(**self.kwargs)
            context.update(
                enrolment_downloads=enrolment_downloads,
                cohort_report=cohort_report,
                cohort_a=cohort_a,
                cohort_b=cohort_b,
                cohort_c=cohort_c,
                sec_aims=sec_aims,
                form=form)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        enrolment_downloads = ExportFile.objects.filter(
            description='Enrolment Report').order_by('uploaded_at')

        # Enrolment report
        cohort_report = self.cohort_report()
        cohort_a = self.cohort_a()
        cohort_b = self.cohort_b()
        cohort_c = self.cohort_c()
        sec_aims = self.sec_aims()
        subject_crfs_missing = self.subject_crfs_missing()

        context.update(
            enrolment_downloads=enrolment_downloads,
            cohort_report=cohort_report,
            cohort_a=cohort_a,
            cohort_b=cohort_b,
            cohort_c=cohort_c,
            sec_aims=sec_aims,
            subject_crfs_missing=mark_safe(subject_crfs_missing))
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

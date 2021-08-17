from collections import Counter
from collections import OrderedDict

import pandas
from django.apps import apps as django_apps

import pandas as pd

from django.contrib.auth.decorators import login_required
from django.db.models import QuerySet
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
from flourish_caregiver.models import *


class EnrolmentReportMixin:
    child_consents_cls = django_apps.get_model('flourish_caregiver.caregiverchildconsent')
    maternal_dataset_cls = django_apps.get_model('flourish_caregiver.maternaldataset')
    child_dataset_cls = django_apps.get_model('flourish_child.childdataset')

    def all_cohort_report(self, start_date=None, end_date=None):
        """Return a total enrolment per cohort.
        """
        consents: QuerySet = None

        if start_date and end_date:
            consents = CaregiverChildConsent.objects.filter(
                created__gte=start_date,
                created__lte=end_date)
        else:
            consents = CaregiverChildConsent.objects.all()

        # get cohort secondary aims

        reports_totals = {'Cohort A': 0, 'Cohort A Secondary Aims': consents.filter(cohort='cohort_a_sec').count(),
                          'Cohort B': 0, 'Cohort B Secondary Aims': consents.filter(cohort='cohort_b_sec').count(),
                          'Cohort C': 0, 'Cohort C Secondary Aims': consents.filter(cohort='cohort_c_sec').count()}

        # reusing functions to get the total for each cohort

        for value in self.cohort_a().values():
            reports_totals['Cohort A'] += value

        for value in self.cohort_b().values():
            reports_totals['Cohort B'] += value

        for value in self.cohort_c().values():
            reports_totals['Cohort C'] += value

        # reports_totals['Cohort A Secondary Aims'] = consents.

        return reports_totals

    def cohort_a(self, start_date=None, end_date=None):
        """Returns totals for cohort A.
        """
        cohort_a_identifiers = self.child_consents_cls.objects.filter(
            cohort='cohort_a').values_list(
            'subject_consent__screening_identifier')

        study_maternal_identifiers = MaternalDataset.objects.values_list(
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

        cohort_b_identifiers = self.child_consents_cls.objects.filter(
            cohort='cohort_b').values_list(
            'subject_consent__screening_identifier', flat=True)

        study_maternal_identifiers = self.maternal_dataset_cls.objects.values_list(
            'study_maternal_identifier', flat=True).filter(
            screening_identifier__in=cohort_b_identifiers)

        preg_efv_count = self.maternal_dataset_cls.objects.filter(
            study_maternal_identifier__in=study_maternal_identifiers,
            preg_efv=1).count()

        preg_dtg_count = self.maternal_dataset_cls.objects.filter(
            study_maternal_identifier__in=study_maternal_identifiers,
            preg_dtg=1).count()

        hiv_neg_preg_count = self.maternal_dataset_cls.objects.filter(
            study_maternal_identifier__in=study_maternal_identifiers,
            mom_hivstatus='HIV-uninfected').count()

        cohort_b_dict = {
            'EFV': preg_efv_count,
            'DTG': preg_dtg_count,
            'HIV-Preg': hiv_neg_preg_count
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

            cohort_report = self.all_cohort_report(
                start_date=start_date,
                end_date=end_date)

            df1 = pandas.DataFrame(list(cohort_report.items()), columns=['Cohort Enrollments', 'Qty'])

            cohort_a = self.cohort_a(
                start_date=start_date,
                end_date=end_date)

            df2 = pandas.DataFrame(list(cohort_a.items()), columns=['Cohort A', 'Qty'])

            cohort_b = self.cohort_b(
                start_date=start_date,
                end_date=end_date)
            df3 = pandas.DataFrame(list(cohort_b.items()), columns=['Cohort B', 'Qty'])

            cohort_c = self.cohort_c(
                start_date=start_date,
                end_date=end_date)
            df4 = pandas.DataFrame(list(cohort_c.items()), columns=['Cohort C', 'Qty'])

            sec_aims = self.sec_aims(
                start_date=start_date,
                end_date=end_date)
            df5 = pandas.DataFrame(list(sec_aims.items()), columns=['Secondary Aims', 'Qty'])

            df = [
                df1,
                df2,
                df3,
                df4,
                df5
            ]

            if 'rdownload_report' in self.request.POST:
                data = [
                    {"All Cohort Reports": cohort_report.values()},
                    {"Cohort A": [value for value in cohort_a.values()]},
                    {"Cohort B": [value for value in cohort_b.values()]},
                    {"Cohort C": [value for value in cohort_c.values()]},
                    {"Secondary Aims": [value for value in sec_aims.values()]},
                ]

                self.download_data(
                    description='Cohort Report',
                    start_date=start_date, end_date=end_date,
                    report_type='enrolment_reports',
                    df=df)

            enrolment_downloads = ExportFile.objects.filter(
                description='enrolment_reports').order_by('uploaded_at')

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
            description='enrolment_reports').order_by('uploaded_at')

        # Enrolment report
        cohort_a = self.cohort_a()
        cohort_b = self.cohort_b()
        cohort_c = self.cohort_c()
        sec_aims = self.sec_aims()

        context.update(
            enrolment_downloads=enrolment_downloads,
            cohort_report=self.all_cohort_report(),
            cohort_a=cohort_a,
            cohort_b=cohort_b,
            cohort_c=cohort_c,
            sec_aims=sec_aims, )
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

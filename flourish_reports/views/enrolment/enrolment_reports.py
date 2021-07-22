from collections import Counter
from collections import OrderedDict

import pandas
from django.apps import apps as django_apps

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

    def all_cohort_report(self, start_date=None, end_date=None):
        """Return a total enrolment per cohort.
        """
        if start_date and end_date:
            consents = CaregiverChildConsent.objects.filter(
                created__gte=start_date,
                created__lte=end_date).values_list(
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
        return dict(OrderedDict(sorted(report.items())))

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
            df1 = pandas.DataFrame(cohort_report, index=[0])

            cohort_a = self.cohort_a(
                start_date=start_date,
                end_date=end_date)
            df2 = pandas.DataFrame(cohort_a, index=[1])

            cohort_b = self.cohort_b(
                start_date=start_date,
                end_date=end_date)
            df3 = pandas.DataFrame(cohort_b, index=[2])

            cohort_c = self.cohort_c(
                start_date=start_date,
                end_date=end_date)
            df4 = pandas.DataFrame(cohort_c, index=[3])

            sec_aims = self.sec_aims(
                start_date=start_date,
                end_date=end_date)
            df5 = pandas.DataFrame(sec_aims, index=[4])

            df = [
                df1,
                df2,
                df3,
                df4,
                df5
            ]

            # data.extend([cohort_report, cohort_a, cohort_b, cohort_c, sec_aims])

            if 'rdownload_report' in self.request.POST:
                self.download_data(
                    description='Cohort Report',
                    start_date=start_date, end_date=end_date,
                    report_type='enrolment_reports',
                    # df=pd.DataFrame.from_dict(data, orient='index').fillna(0).transpose())
                    df=df)

                # self.download_data(
                #     description='Cohort A Report',
                #     start_date=start_date, end_date=end_date,
                #     report_type='enrolment_reports',
                #     df=pd.DataFrame([cohort_a]))
                #
                # self.download_data(
                #     description='Cohort B Report',
                #     start_date=start_date, end_date=end_date,
                #     report_type='enrolment_reports',
                #     df=pd.DataFrame([cohort_b]))
                #
                # self.download_data(
                #     description='Cohort C Report',
                #     start_date=start_date, end_date=end_date,
                #     report_type='enrolment_reports',
                #     df=pd.DataFrame([cohort_c]))

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

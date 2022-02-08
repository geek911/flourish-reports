from django.apps import apps as django_apps
from django.db.models import QuerySet


class EnrolmentReportMixin:

    child_consents_cls = django_apps.get_model('flourish_caregiver.caregiverchildconsent')
    maternal_dataset_cls = django_apps.get_model('flourish_caregiver.maternaldataset')
    child_dataset_cls = django_apps.get_model('flourish_child.childdataset')
    child_birth_cls = django_apps.get_model('flourish_child.childbirth')

    def all_cohort_report(self, start_date=None, end_date=None):
        """Return a total enrolment per cohort.
        """
        consents: QuerySet = None

        if start_date and end_date:
            consents = self.child_consents_cls.objects.filter(
                created__gte=start_date,
                created__lte=end_date)
        else:
            consents = self.child_consents_cls.objects.all()

        # get cohort secondary aims

        reports_totals = {
            'Cohort A': 0,
            'Cohort A Secondary Aims': consents.filter(cohort='cohort_a_sec').count(),
            'Cohort B': 0,
            'Cohort B Secondary Aims': consents.filter(cohort='cohort_b_sec').count(),
            'Cohort C': 0,
            'Cohort C Secondary Aims': consents.filter(cohort='cohort_c_sec').count()}

        # reusing functions to get the total for each cohort

        for value in self.cohort_a().values():
            reports_totals['Cohort A'] += value

        for value in self.cohort_b().values():
            reports_totals['Cohort B'] += value

        for value in self.cohort_c().values():
            reports_totals['Cohort C'] += value

        # reports_totals['Cohort A Secondary Aims'] = consents.

        return reports_totals

    def get_cohort_identifiers(self, cohort):

        cohort_identifiers = self.child_consents_cls.objects.filter(
            cohort=cohort).values_list(
            'subject_consent__screening_identifier')

        study_maternal_identifiers = self.maternal_dataset_cls.objects.values_list(
            'study_maternal_identifier', flat=True).filter(
            screening_identifier__in=cohort_identifiers)

        return study_maternal_identifiers

    def get_study_child_identifiers(self, study_maternal_identifiers):

        study_child_identifiers = self.child_dataset_cls.objects.values_list(
            'study_child_identifier', flat=True).filter(
            study_maternal_identifier__in=study_maternal_identifiers)

        return study_child_identifiers

    def cohort_a(self, start_date=None, end_date=None):
        """Returns totals for cohort A.
        """
        study_maternal_identifiers = self.get_cohort_identifiers('cohort_a')

        self.cohort_a_heus = self.child_dataset_cls.objects.filter(
            study_maternal_identifier__in=study_maternal_identifiers,
            infant_hiv_exposed__in=['Exposed', 'exposed']).distinct()

        self.cohort_a_huus = self.child_dataset_cls.objects.filter(
            study_maternal_identifier__in=study_maternal_identifiers,
            infant_hiv_exposed__in=['Unexposed', 'unexposed']).distinct()

        ante_enrol_cls = django_apps.get_model('flourish_caregiver.antenatalenrollment')
        self.ante_enrol = ante_enrol_cls.objects.all()

        cohort_a_dict = {
            'preg_woman': self.ante_enrol.count(),
            'HEU': self.cohort_a_heus.count(),
            'HUU': self.cohort_a_huus.count()
        }
        return cohort_a_dict

    def cohort_b(self, start_date=None, end_date=None):
        """Returns totals for cohort B.
        """

        study_maternal_identifiers = self.get_cohort_identifiers('cohort_b')

        preg_efvs = self.maternal_dataset_cls.objects.filter(
            study_maternal_identifier__in=study_maternal_identifiers,
            preg_efv=1).values_list('study_maternal_identifier')

        self.cohort_b_preg_efv = self.get_study_child_identifiers(preg_efvs)

        preg_dtgs = self.maternal_dataset_cls.objects.filter(
            study_maternal_identifier__in=study_maternal_identifiers,
            preg_dtg=1).values_list('study_maternal_identifier')

        self.cohort_b_preg_dtg = self.get_study_child_identifiers(preg_dtgs)

        hiv_neg_pregs = self.maternal_dataset_cls.objects.filter(
            study_maternal_identifier__in=study_maternal_identifiers,
            mom_hivstatus='HIV-uninfected').values_list('study_maternal_identifier')

        self.hiv_neg_preg = self.get_study_child_identifiers(hiv_neg_pregs)

        cohort_b_dict = {
            'EFV': len(set(self.cohort_b_preg_efv)),
            'DTG': len(set(self.cohort_b_preg_dtg)),
            'HIV-Preg': len(set(self.hiv_neg_preg))
        }
        return cohort_b_dict

    def cohort_c(self, start_date=None, end_date=None):
        """Returns totals for cohort C.
        """

        study_maternal_identifiers = self.get_cohort_identifiers('cohort_c')

        self.cohort_c_huus = self.child_dataset_cls.objects.filter(
            study_maternal_identifier__in=study_maternal_identifiers,
            infant_hiv_exposed__in=['Unexposed', 'unexposed']).distinct()

        c_preg_pis = self.maternal_dataset_cls.objects.filter(
            study_maternal_identifier__in=study_maternal_identifiers,
            preg_pi=1).values_list('study_maternal_identifier')

        self.preg_pi = self.get_study_child_identifiers(c_preg_pis)

        cohort_c_dict = {
            'HUU': self.cohort_c_huus.count(),
            'PI': len(set(self.preg_pi)),
        }
        return cohort_c_dict

    def sec_aims(self, start_date=None, end_date=None):
        """Returns totals for Secondary Aims.
        """
        cohort_sec_identifiers = self.child_consents_cls.objects.filter(
            cohort__icontains='_sec').values_list('study_child_identifier')

        study_maternal_identifiers = self.child_dataset_cls.objects.values_list(
            'study_maternal_identifier', flat=True).filter(
            study_child_identifier__in=cohort_sec_identifiers)

        hiv_pos_preg_counts = self.maternal_dataset_cls.objects.filter(
            study_maternal_identifier__in=study_maternal_identifiers,
            mom_hivstatus='HIV-infected').values_list('study_maternal_identifier')

        self.hiv_pos_preg = self.get_study_child_identifiers(hiv_pos_preg_counts)

        hiv_neg_preg_counts = self.maternal_dataset_cls.objects.filter(
            study_maternal_identifier__in=study_maternal_identifiers,
            mom_hivstatus='HIV-uninfected').values_list('study_maternal_identifier')

        self.hiv_neg_preg_sec = self.get_study_child_identifiers(hiv_neg_preg_counts)

        cohort_sec_dict = {
            'WLHIV': len(set(self.hiv_pos_preg)),
            'HIV -': len(set(self.hiv_neg_preg_sec))
        }
        return cohort_sec_dict

    def get_preg_child_pid(self, maternal_subject_identifier):

        try:
            child_birth = self.child_birth_cls.objects.get(
                subject_identifier__startswith=maternal_subject_identifier)
        except self.child_birth_cls.DoesNotExist:
            try:
                child_consent = self.child_consents_cls.objects.filter(
                    subject_identifier__startswith=maternal_subject_identifier,
                    first_name='',
                    last_name='',
                    child_dob__isnull=True).distinct()[0]
            except self.child_consents_cls.DoesNotExist:
                return None
            else:
                return child_consent.subject_identifier
        else:
            return child_birth.subject_identifier

    @property
    def cohort_a_category_pids(self):

        cohort_a_heus = self.cohort_a_heus.values_list('study_child_identifier')

        cohort_a_huus = self.cohort_a_huus.values_list('study_child_identifier')

        heus_pids = self.child_consents_cls.objects.filter(
            study_child_identifier__in=cohort_a_heus).values_list(
                'subject_identifier', flat=True)

        huus_pids = self.child_consents_cls.objects.filter(
            study_child_identifier__in=cohort_a_huus).values_list(
                'subject_identifier', flat=True)

        preg_pids = self.ante_enrol.values_list('subject_identifier', flat=True)

        cohort_a_pids_dict = {
            'preg_woman_pids': [self.get_preg_child_pid(pid) for
                                pid in preg_pids],
            'HEU_pids': heus_pids,
            'HUU_pids': huus_pids
        }

        return cohort_a_pids_dict

    @property
    def cohort_b_category_pids(self):

        preg_efv_pids = self.child_consents_cls.objects.filter(
            study_child_identifier__in=self.cohort_b_preg_efv).values_list(
                'subject_identifier', flat=True)

        b_preg_dtg_pids = self.child_consents_cls.objects.filter(
            study_child_identifier__in=self.cohort_b_preg_dtg).values_list(
                'subject_identifier', flat=True)

        b_hiv_neg_preg_pids = self.child_consents_cls.objects.filter(
            study_child_identifier__in=self.hiv_neg_preg).values_list(
                'subject_identifier', flat=True)

        cohort_b_pids_dict = {
            'EFV_pids': preg_efv_pids,
            'DTG_pids': b_preg_dtg_pids,
            'HIV-Preg_pids': b_hiv_neg_preg_pids
        }

        return cohort_b_pids_dict

    @property
    def cohort_c_category_pids(self,):

        c_huus = self.cohort_c_huus.values_list(
            'study_child_identifier', flat=True)

        c_huus_pids = self.child_consents_cls.objects.filter(
            study_child_identifier__in=c_huus).values_list(
                'subject_identifier', flat=True)

        preg_pis_pids = self.child_consents_cls.objects.filter(
            study_child_identifier__in=self.preg_pi).values_list(
                'subject_identifier', flat=True)

        cohort_c_pids_dict = {
            'HUU_pids': c_huus_pids,
            'PI_pids': preg_pis_pids,
        }
        return cohort_c_pids_dict

    @property
    def sec_aims_category_pids(self,):

        hiv_pos_pids = self.child_consents_cls.objects.filter(
            study_child_identifier__in=self.hiv_pos_preg).values_list(
                'subject_identifier', flat=True)

        hiv_neg_pids = self.child_consents_cls.objects.filter(
            study_child_identifier__in=self.hiv_neg_preg).values_list(
                'subject_identifier', flat=True)

        cohort_sec_pids_dict = {
            'WLHIV': hiv_pos_pids,
            'HIV -': hiv_neg_pids
        }
        return cohort_sec_pids_dict

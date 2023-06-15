from collections import defaultdict

from django.apps import apps as django_apps
from django.db.models import Max


class EnrolmentReportMixin:
    child_consents_cls = django_apps.get_model('flourish_caregiver.caregiverchildconsent')
    maternal_dataset_cls = django_apps.get_model('flourish_caregiver.maternaldataset')
    cohort_cls = django_apps.get_model('flourish_caregiver.cohort')
    child_dataset_cls = django_apps.get_model('flourish_child.childdataset')
    child_birth_cls = django_apps.get_model('flourish_child.childbirth')
    ante_enrol_cls = django_apps.get_model('flourish_caregiver.antenatalenrollment')

    @property
    def participants_cohort(self):
        return self.cohort_cls.objects.all()

    @property
    def latest_cohort_objs(self):
        latest_cohort_objs_ids = self.participants_cohort.values(
            'subject_identifier').annotate(latest_report_date=Max(
            'assign_datetime')).values_list('id', flat=True)

        return self.participants_cohort.filter(id__in=latest_cohort_objs_ids)

    def all_cohort_report(self, start_date=None, end_date=None):
        """Return a total enrolment per cohort.
        """
        table = {
            'Cohort A': ['enrollment', 'cohort_b', 'cohort_b_sec', 'cohort_c',
                         'cohort_c_sec'],
            'Cohort B': ['enrollment', 'cohort_b', 'cohort_b_sec', 'cohort_c',
                         'cohort_c_sec'],
            'Cohort C': ['enrollment', 'cohort_b', 'cohort_b_sec', 'cohort_c',
                         'cohort_c_sec'],
            'Cohort A Secondary Aims': ['enrollment', 'cohort_b', 'cohort_b_sec',
                                        'cohort_c', 'cohort_c_sec'],
            'Cohort B Secondary Aims': ['enrollment', 'cohort_b', 'cohort_b_sec',
                                        'cohort_c', 'cohort_c_sec'],
            'Cohort C Secondary Aims': ['enrollment', 'cohort_b', 'cohort_b_sec',
                                        'cohort_c', 'cohort_c_sec'],
        }
        cohort_report = {}
        for cohort, values in table.items():
            cohort_report[cohort] = {'enrollment': self.get_cohort_enrolment_data(cohort)}
            for value in values[1:]:
                cohort_report[cohort][value] = self.get_aged_up(prev_cohort=value,
                                                                new_cohort=cohort)

        return cohort_report

    def get_data(self, key, cohort):
        if key == 'enrollment':
            return self.get_cohort_enrolment_data(cohort=cohort)
        else:
            return self.get_aged_up(new_cohort=key, prev_cohort=cohort)

    def get_aged_up(self, prev_cohort, new_cohort):
        if 'Cohort A' in prev_cohort:
            prev_cohort = 'cohort_a'
        if 'Cohort B' in prev_cohort:
            prev_cohort = 'cohort_b'
        if 'Cohort C' in prev_cohort:
            prev_cohort = 'cohort_c'

        enrolment_cohort = self.cohort_data(name=prev_cohort).values_list(
            'subject_identifier', flat=True).distinct()
        return self.latest_cohort_objs.filter(
            name=new_cohort, subject_identifier__in=enrolment_cohort).count()

    def cohort_data(self, name, enrolment=True):
        return self.participants_cohort.filter(name=name, enrollment_cohort=True) if \
            enrolment else self.latest_cohort_objs.filter(name=name)

    def get_cohort_enrolment_data(self, cohort):

        reports_totals = {
            'Cohort A': 0,
            'Cohort A Secondary Aims': self.cohort_data(name='cohort_a_sec').count(),
            'Cohort B': 0,
            'Cohort B Secondary Aims': self.cohort_data(name='cohort_b_sec').count(),
            'Cohort C': 0,
            'Cohort C Secondary Aims': self.cohort_data(name='cohort_c_sec').count()
        }

        # reusing functions to get the total for each cohort

        for value in self.cohort_a().values():
            reports_totals['Cohort A'] += value.count()

        for value in self.cohort_b().values():
            reports_totals['Cohort B'] += value.count()

        for value in self.cohort_c().values():
            reports_totals['Cohort C'] += value.count()

        # reports_totals['Cohort A Secondary Aims'] = consents.

        return reports_totals[cohort]

    def get_cohort_identifiers(self, cohort, enrolment=True):

        cohort_identifiers = self.cohort_data(
            name=cohort, enrolment=enrolment).values_list('subject_identifier', flat=True)

        caregiver_ids = [subj_id[:-3] for subj_id in cohort_identifiers]

        study_maternal_identifiers = self.maternal_dataset_cls.objects.filter(
            subject_identifier__in=caregiver_ids).values_list(
            'study_maternal_identifier', flat=True)

        return study_maternal_identifiers

    def get_study_child_identifiers(self, study_maternal_identifiers):

        study_child_identifiers = self.child_dataset_cls.objects.filter(
            study_maternal_identifier__in=study_maternal_identifiers).values_list(
            'study_child_identifier', flat=True)

        return study_child_identifiers

    def exposed_participants(self, study_maternal_identifiers):
        return self.child_dataset_cls.objects.filter(
            study_maternal_identifier__in=study_maternal_identifiers,
            infant_hiv_exposed__in=['Exposed', 'exposed']).distinct()

    def unexposed_participants(self, study_maternal_identifiers):
        return self.child_dataset_cls.objects.filter(
            study_maternal_identifier__in=study_maternal_identifiers,
            infant_hiv_exposed__in=['Unexposed', 'unexposed']).distinct()

    @property
    def generate_enrolment_cohort_breakdown(self):
        cohorts = {
            'Cohort A': self.get_breakdown('cohort_a'),
            'Cohort B': self.get_breakdown('cohort_b', heu_3_drug_art=True),
            'Cohort C': self.get_breakdown('cohort_c', heu_3_drug_art=True),
            'Cohort A Secondary Aims': self.get_breakdown('cohort_a_sec'),
            'Cohort B Secondary Aims': self.get_breakdown('cohort_b_sec',
                                                          heu_3_drug_art=True),
            'Cohort C Secondary Aims': self.get_breakdown('cohort_c_sec',
                                                          heu_3_drug_art=True)
        }
        return cohorts

    @property
    def generate_current_cohort_breakdown(self):
        cohorts = {
            'Cohort A': self.get_breakdown('cohort_a', enrolment=False),
            'Cohort B': self.get_breakdown('cohort_b', enrolment=False,
                                           heu_3_drug_art=True),
            'Cohort C': self.get_breakdown('cohort_c', enrolment=False,
                                           heu_3_drug_art=True),
            'Cohort A Secondary Aims': self.get_breakdown('cohort_a_sec',
                                                          enrolment=False),
            'Cohort B Secondary Aims': self.get_breakdown('cohort_b_sec', enrolment=False,
                                                          heu_3_drug_art=True),
            'Cohort C Secondary Aims': self.get_breakdown('cohort_c_sec', enrolment=False,
                                                          heu_3_drug_art=True)
        }
        return cohorts

    def get_breakdown(self, cohort_name, enrolment=True, heu_3_drug_art=False):
        cohort = self.get_cohort(cohort_name, enrolment=enrolment)
        heu = cohort.get('HEU').count()
        huu = cohort.get('HUU').count()
        heu_3_drug_art_value = cohort.get('HEU 3-drug ART').count() if heu_3_drug_art else 0
        return [self.get_pregnant_woman(cohort_name).count() if cohort_name == 'cohort_a' else 0,
                heu, huu, heu_3_drug_art_value]

    def get_pregnant_woman(self, cohort_name):
        return self.cohort_a(enrolment=True).get(
            'preg_woman') if cohort_name == 'cohort_a' else 0

    @property
    def ante_enrol(self):
        return self.ante_enrol_cls.objects.all()

    def cohort_a(self, start_date=None, end_date=None, enrolment=True):
        """Returns totals for cohort A.
        """
        study_maternal_identifiers = self.get_cohort_identifiers('cohort_a',
                                                                 enrolment=enrolment)

        return {
            'preg_woman': self.ante_enrol,
            'HEU': self.exposed_participants(
                study_maternal_identifiers=study_maternal_identifiers),
            'HUU': self.unexposed_participants(
                study_maternal_identifiers=study_maternal_identifiers)
        }

    def heu_art_3drug_combination(self, study_maternal_identifiers):
        exposed_participants = self.exposed_participants(
            study_maternal_identifiers=study_maternal_identifiers).values_list(
            'study_maternal_identifier', flat=True)
        return self.maternal_dataset_cls.objects.filter(
            study_maternal_identifier__in=exposed_participants,
            mom_pregarv_strat='3-drug ART').values_list('study_maternal_identifier')

    def get_cohort(self, cohort_type, enrolment=True):
        study_maternal_identifiers = self.get_cohort_identifiers(cohort_type,
                                                                 enrolment=enrolment)

        return {
            'HUU': self.unexposed_participants(
                study_maternal_identifiers=study_maternal_identifiers),
            'HEU 3-drug ART': self.heu_art_3drug_combination(
                study_maternal_identifiers=study_maternal_identifiers),
            'HEU': self.exposed_participants(
                study_maternal_identifiers=study_maternal_identifiers)
        }

    def cohort_b(self, start_date=None, end_date=None):
        """Returns totals for cohort B.
        """

        study_maternal_identifiers = self.get_cohort_identifiers('cohort_b')

        return {
            'HUU': self.unexposed_participants(
                study_maternal_identifiers=study_maternal_identifiers),
            'HEU 3-drug ART': self.heu_art_3drug_combination(
                study_maternal_identifiers=study_maternal_identifiers)
        }

    def cohort_c(self, start_date=None, end_date=None):
        """Returns totals for cohort C.
        """

        study_maternal_identifiers = self.get_cohort_identifiers('cohort_c')

        return {
            'HUU': self.unexposed_participants(
                study_maternal_identifiers=study_maternal_identifiers),
            'HEU 3-drug ART': self.heu_art_3drug_combination(
                study_maternal_identifiers=study_maternal_identifiers)
        }

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

        cohort_a_heus = self.cohort_a().get('HEU').values_list('study_child_identifier')

        cohort_a_huus = self.cohort_a().get('HUU').values_list('study_child_identifier')

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

        huu_pids = self.child_consents_cls.objects.filter(
            study_child_identifier__in=self.get_cohort(
                cohort_type='cohort_b', enrolment=False).get('HUU').values_list(
                'study_child_identifier')).values_list('subject_identifier', flat=True)

        heu_pids = self.child_consents_cls.objects.filter(
            study_child_identifier__in=self.get_cohort(
                cohort_type='cohort_b', enrolment=False).get('HEU').values_list(
                'study_child_identifier')).values_list('subject_identifier', flat=True)

        heu_art_3drug = self.child_consents_cls.objects.filter(
            subject_consent__subject_identifier__in=self.get_cohort(
                cohort_type='cohort_b', enrolment=False).get(
                'HEU 3-drug ART').values_list('subject_identifier')).values_list(
            'subject_identifier', flat=True)

        cohort_b_pids_dict = {
            'HUU': huu_pids,
            'HEU': heu_pids,
            'HEU 3-drug ART': heu_art_3drug,
        }

        return cohort_b_pids_dict

    @property
    def cohort_c_category_pids(self, ):

        huu_pids = self.child_consents_cls.objects.filter(
            study_child_identifier__in=self.get_cohort(
                cohort_type='cohort_c', enrolment=False).get('HUU').values_list(
                'study_child_identifier')).values_list('subject_identifier', flat=True)

        heu_pids = self.child_consents_cls.objects.filter(
            study_child_identifier__in=self.get_cohort(
                cohort_type='cohort_c', enrolment=False).get('HEU').values_list(
                'study_child_identifier')).values_list('subject_identifier', flat=True)

        heu_art_3drug = self.child_consents_cls.objects.filter(
            subject_consent__subject_identifier__in=self.get_cohort(
                cohort_type='cohort_c', enrolment=False).get(
                'HEU 3-drug ART').values_list('subject_identifier')).values_list(
            'subject_identifier', flat=True)

        return {
            'HUU': huu_pids,
            'HEU': heu_pids,
            'HEU 3-drug ART': heu_art_3drug,
        }

    @property
    def sec_aims_category_pids(self, ):

        hiv_pos_pids = self.child_consents_cls.objects.filter(
            study_child_identifier__in=self.hiv_pos_preg).values_list(
            'subject_identifier', flat=True)

        hiv_neg_sec_pids = self.child_consents_cls.objects.filter(
            study_child_identifier__in=self.hiv_neg_preg_sec).values_list(
            'subject_identifier', flat=True)

        cohort_sec_pids_dict = {
            'WLHIV': hiv_pos_pids,
            'HIV -': hiv_neg_sec_pids
        }
        return cohort_sec_pids_dict

from django import template
from django.apps import apps as django_apps

register = template.Library()


@register.inclusion_tag('flourish_reports/enrolment/cohort_breakdown.html')
def cohort_breakdown(data, title):
    return dict(
        data=data,
        title=title
    )


@register.inclusion_tag('flourish_reports/enrolment/targets_reports.html')
def targets_reports(data, heu_target, huu_target):
    return dict(
        title=data.get('cohort_name'),
        heu_target=heu_target,
        huu_target=huu_target,
        unexposed=data.get('unexposed'),
        exposed=data.get('exposed'),
    )


@register.filter
def get_item(dictionary, key):
    if dictionary is not None and isinstance(dictionary, dict):
        return dictionary.get(key)


@register.simple_tag
def convert_to_title_case(snake_case_string):
    title_case_string = snake_case_string.replace("_", " ").title()
    return title_case_string


@register.filter
def get_cohort_breakdown(cohort, report_type=''):
    cohort_cls = django_apps.get_model('flourish_caregiver.cohort')
    if report_type.lower() == 'current':
        cohorts = cohort_cls.objects.filter(name=cohort, current_cohort=True)
    elif report_type.lower() == 'enrolment':
        cohorts = cohort_cls.objects.filter(name=cohort, enrollment_cohort=True)

    anc_unexposed = 0
    anc_exposed = 0
    prior_unexposed = 0
    prior_exposed = 0
    for cohort in cohorts:
        if cohort.exposure_status == 'EXPOSED':
            if cohort.check_antenetal_exists():
                anc_exposed += 1
            else:
                prior_exposed += 1
        else:
            if cohort.check_antenetal_exists():
                anc_unexposed += 1
            else:
                prior_unexposed += 1
    return [{'cohort_name': 'ANC', 'exposed': anc_exposed, 'unexposed': anc_unexposed},
            {'cohort_name': 'BHP-Prior', 'exposed': prior_exposed, 'unexposed': prior_unexposed}]

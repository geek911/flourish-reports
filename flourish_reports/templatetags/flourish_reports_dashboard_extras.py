from django import template

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

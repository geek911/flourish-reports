from django import template

register = template.Library()


@register.inclusion_tag('flourish_reports/enrolment/cohort_breakdown.html')
def cohort_breakdown(data, title):
    return dict(
        data=data,
        title=title
    )


@register.inclusion_tag('flourish_reports/enrolment/cohort_panel.html')
def cohort_b_panel(data):
    title = 'Cohort B'
    return dict(
        data=data,
        title=title,
        huu_limit=100,
        drug_limit=200,
    )


@register.inclusion_tag('flourish_reports/enrolment/cohort_panel.html')
def cohort_c_panel(data):
    title = 'Cohort C'
    return dict(
        data=data,
        title=title,
        huu_limit=200,
        drug_limit=100,
    )

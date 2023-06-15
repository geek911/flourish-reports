from django import template

register = template.Library()


@register.inclusion_tag('flourish_reports/enrolment/cohort_breakdown.html')
def cohort_breakdown(data, title):
    return dict(
        data=data,
        title=title
    )

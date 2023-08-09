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


@register.filter
def get_item(dictionary, key):
    if dictionary is not None and isinstance(dictionary, dict):
        return dictionary.get(key)


@register.filter
def get_item_key(dictionary, key):
    title_to_snake_case_key = title_to_snake_case(key)
    if dictionary is not None and isinstance(dictionary, dict):
        return dictionary.get(title_to_snake_case_key)


def title_to_snake_case(title):
    # Replace spaces with underscores
    snake = title.replace(" ", "_")
    # Convert all characters to lower case
    snake = snake.lower()
    # Return the snake case string
    return snake

from django.apps import AppConfig as DjangoApponfig


class AppConfig(DjangoApponfig):
    name = 'flourish_reports'
    verbose_name = 'Flourish Reports'
    admin_site_name = 'flourish_reports_admin'
    extra_assignee_choices = ()
    assignable_users_group = 'assignable users'

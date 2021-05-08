from django.conf import settings

from edc_navbar import NavbarItem, site_navbars, Navbar

flourish_reports = Navbar(name='flourish_reports')
no_url_namespace = True if settings.APP_NAME == 'flourish_reports' else False

flourish_reports.append_item(
    NavbarItem(name='flourish_reports',
               label='Flourish reports',
               fa_icon='fa-cogs',
               url_name='flourish_reports:home_url'))

site_navbars.register(flourish_reports)

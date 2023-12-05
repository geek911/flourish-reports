from collections import defaultdict

from django.contrib.auth.decorators import login_required
from django.urls.base import reverse
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from edc_base.view_mixins import EdcBaseViewMixin
from edc_navbar import NavbarViewMixin


class MissingCrfTemplateView(EdcBaseViewMixin,
                             NavbarViewMixin, TemplateView):
    template_name = 'flourish_reports/missing_crfs/missing_crf_templateview.html'
    navbar_name = 'flourish_reports'
    navbar_selected_item = 'enrolment_reports'

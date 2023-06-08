from typing import Any, Optional
from django.db import models
from django.http import HttpResponse
from django.apps import apps as django_apps
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls.base import reverse
from django.utils.decorators import method_decorator
from django.views.generic import DetailView
from edc_base.view_mixins import EdcBaseViewMixin
from edc_navbar import NavbarViewMixin
from .missing_crf_report_mixin import MissingCrfDetailedMixin
from .missing_crf_data_statistics import MissingCRFDataStatistics


class MissingCrfDetailedReport(EdcBaseViewMixin,
                               NavbarViewMixin,
                               DetailView,
                               LoginRequiredMixin,
                               MissingCrfDetailedMixin):
    template_name = 'flourish_reports/missing_crfs/missing_crf_detailed_report.html'
    navbar_name = 'flourish_reports'
    navbar_selected_item = 'flourish_reports'
    maternal_visit_model = 'flourish_caregiver.maternalvisit'

    @property
    def maternal_visit_cls(self):
        return django_apps.get_model(self.maternal_visit_model)

    def get_object(self):
        return self.maternal_visit_cls.objects.get(id=self.kwargs['id'])

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context["crf_statistics"] = self.all_crf_statistics

        return context

    @property
    def all_crf_statistics(self):
        # Put in a mixin
        self.statistics = MissingCRFDataStatistics()
        self.statistics.visit_object = self.object

        # breakpoint()

        result = []

        for crf in self.statistics.crfs:
            models_cls = django_apps.get_model(crf.model)
            crf_obj = models_cls.objects.filter(maternal_visit=self.object)

            result_dict = dict()

            verbose_name = models_cls._meta.verbose_name
            required = crf.required

            exist = True if crf_obj.exists() else False

            result_dict['verbose_name'] = verbose_name
            result_dict['required'] = required
            result_dict['exist'] = exist

            result.append(result_dict)
        return result

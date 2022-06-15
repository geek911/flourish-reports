
from django.db import models
from edc_base.model_mixins import BaseUuidModel
from edc_search.model_mixins import SearchSlugManager


class TotalRecruitmentStatsManager(SearchSlugManager, models.Manager):

    def get_by_natural_key(self, eligibility_identifier):
        return self.get(screening_identifier=eligibility_identifier)


class TotalRecruitmentStats(BaseUuidModel):

    objects = TotalRecruitmentStatsManager()

    total_attempts = models.PositiveIntegerField(
        verbose_name='Total attempts',
        blank=True,
        null=True)

    not_attempted = models.PositiveIntegerField(
        verbose_name='Total not attempted',
        blank=True,
        null=True)

    total_participants_to_call_again = models.PositiveIntegerField(
        verbose_name='Total participants to call again',
        blank=True,
        null=True)

    total_participants_not_reachable = models.PositiveIntegerField(
        verbose_name='Total participants not reachable',
        blank=True,
        null=True)

    total_decline = models.PositiveIntegerField(
        verbose_name='Total decline',
        blank=True,
        null=True)

    total_consented = models.PositiveIntegerField(
        verbose_name='Total consented',
        blank=True,
        null=True)

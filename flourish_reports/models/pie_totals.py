
from django.db import models
from edc_base.model_mixins import BaseUuidModel
from edc_search.model_mixins import SearchSlugManager


class PieTotalStatsManager(SearchSlugManager, models.Manager):

    def get_by_natural_key(self, eligibility_identifier):
        return self.get(screening_identifier=eligibility_identifier)


class PieTotalStats(BaseUuidModel):

    objects = PieTotalStatsManager()

    mpepu = models.CharField(
        verbose_name='Mpepu',
        max_length=36,
        blank=True,
        null=True,
        unique=True)

    tshipidi = models.PositiveIntegerField(
        verbose_name='Tshipidi',
        blank=True,
        null=True)

    mashi = models.PositiveIntegerField(
        verbose_name='Mashi',
        blank=True,
        null=True)

    mma_bana = models.PositiveIntegerField(
        verbose_name='Mma bana study',
        blank=True,
        null=True)

    tshilo_dikotla = models.PositiveIntegerField(
        verbose_name='Tshilo dikotla study',
        blank=True,
        null=True)

    total_continued_contact = models.PositiveIntegerField(
        verbose_name='Total continued contact',
        blank=True,
        null=True)

    total_decline_uninterested = models.PositiveIntegerField(
        verbose_name='Total decline uninterested',
        blank=True,
        null=True)

    total_consented = models.PositiveIntegerField(
        verbose_name='Total consented',
        blank=True,
        null=True)

    total_unable_to_reach = models.PositiveIntegerField(
        verbose_name='Total unable to reach',
        blank=True,
        null=True)


from django.db import models
from edc_base.model_mixins import BaseUuidModel
from edc_search.model_mixins import SearchSlugManager


class RecruitmentStatsManager(SearchSlugManager, models.Manager):

    def get_by_natural_key(self, eligibility_identifier):
        return self.get(screening_identifier=eligibility_identifier)


class RecruitmentStats(BaseUuidModel):

    objects = RecruitmentStatsManager()

    study = models.CharField(
        verbose_name='Previous Studies',
        max_length=36,
        blank=True,
        null=True,
        unique=True)

    dataset_total = models.PositiveIntegerField(
        verbose_name='Dataset totals',
        blank=True,
        null=True)

    expected_locator = models.PositiveIntegerField(
        verbose_name='Expected locator',
        blank=True,
        null=True)

    existing_locator = models.PositiveIntegerField(
        verbose_name='Existing locator',
        blank=True,
        null=True)

    missing_locator = models.PositiveIntegerField(
        verbose_name='Missing locator',
        blank=True,
        null=True)

    missing_worklist = models.PositiveIntegerField(
        verbose_name='Missing on worklist',
        blank=True,
        null=True)

    existing_worklist = models.PositiveIntegerField(
        verbose_name='Exisiting on worklist',
        blank=True,
        null=True)

    expected_worklist = models.PositiveIntegerField(
        verbose_name='Expected on worklist',
        blank=True,
        null=True)

    randomised = models.PositiveIntegerField(
        verbose_name='Randomised',
        blank=True,
        null=True)

    not_randomised = models.PositiveIntegerField(
        verbose_name='Not randomised & not attempted',
        blank=True,
        null=True)

    study_participants = models.PositiveIntegerField(
        verbose_name='Total study participants',
        blank=True,
        null=True)

    total_attempts = models.PositiveIntegerField(
        verbose_name='Total attempts',
        blank=True,
        null=True)

    total_not_attempted = models.PositiveIntegerField(
        verbose_name='Total not attempted',
        blank=True,
        null=True)

    not_reacheble = models.PositiveIntegerField(
        verbose_name='Participant not reachable',
        blank=True,
        null=True)

    participants_to_call = models.PositiveIntegerField(
        verbose_name='Participants to call again',
        blank=True,
        null=True)

    declined = models.PositiveIntegerField(
        verbose_name='Declined',
        blank=True,
        null=True)

    consented = models.PositiveIntegerField(
        verbose_name='Consented',
        blank=True,
        null=True)

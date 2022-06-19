from celery import shared_task
from .classes import GenerateStudyData


@shared_task(bind=True)
def populate_study_data(self):
    GenerateStudyData().populate_previous_study_data()

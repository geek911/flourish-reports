from edc_visit_schedule import site_visit_schedules
from django.apps import apps as django_apps


class MissingCRFDataStatistics:

    def __init__(self):
        self.visit_object = None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(MissingCRFDataStatistics, cls).__new__(cls)
        return cls.instance

    @property
    def visits_dict(self):
        visit_schedule = site_visit_schedules.get_visit_schedule(
            visit_schedule_name=self.visit_object.visit_schedule_name)
        visits = dict(visit_schedule.schedules).get(self.visit_object.schedule_name).visits

        return dict(visits)

    @property
    def title(self):
        return self.visits_dict[self.visit_object.visit_code].title

    @property
    def crfs(self):
        return self.visits_dict[self.visit_object.visit_code].crfs

    @property
    def total_crfs(self):
        return len(self.crfs)

    @property
    def missing_crfs(self):
        total = 0

        for crf in self.visits_dict[self.visit_object.visit_code].crfs:
            model_cls = django_apps.get_model(crf.model)
            crf_exist = model_cls.objects.filter(maternal_visit=self.visit_object).exists()

            if not crf_exist:
                total += 1

        return total

    @property
    def total_crfs_prn(self):
        return len(self.visits_dict[self.visit_object.visit_code].crfs_prn)

    @property
    def missing_crfs_prn(self):
        total = 0

        for crf in self.visits_dict[self.visit_object.visit_code].crfs_prn:
            model_cls = django_apps.get_model(crf.model)
            crf_exist = model_cls.objects.filter(maternal_visit=self.visit_object).exists()

            if not crf_exist:
                total += 1

        return total

    @property
    def total_requisitions(self):
        return len(self.visits_dict[self.visit_object.visit_code].requisitions)

    @property
    def missing_requisitions(self):
        total = 0

        for crf in self.visits_dict[self.visit_object.visit_code].requisitions:
            model_cls = django_apps.get_model(crf.model)
            crf_exist = model_cls.objects.filter(maternal_visit=self.visit_object).exists()

            if not crf_exist:
                total += 1

        return total

    @property
    def visit_code(self):
        return self.visit_object.visit_code

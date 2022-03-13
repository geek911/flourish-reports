import pandas as pd

from django.core.exceptions import ValidationError
from django_pandas.io import read_frame
from django.shortcuts import HttpResponse

from flourish_caregiver.models import CaregiverLocator, MaternalDataset
from flourish_child.models import ChildDataset


class RecruitmentReport:
    
    @property
    def previous_studies(self):
        """Returns a list of all BHP previous studies used.
        """
        maternal_dataset = MaternalDataset.objects.all()
        return list(set(maternal_dataset.values_list('protocol', flat=True)))
    
    def caregiver_prev_study_dataset(self):
        """Return the totals of all prev study participant dataset
        for caregivers.
        """
        maternal_dataset = MaternalDataset.objects.all()
        df = read_frame(maternal_dataset, fieldnames=['protocol', 'study_maternal_identifier'])
        
        maternal_dataset_starts = []
        total = 0
        for protocol in self.previous_studies:
            df_prev = df[df['protocol'] == protocol]
            maternal_dataset_starts.append([protocol, df_prev[df_prev.columns[0]].count()])
            total += df_prev[df_prev.columns[0]].count()
        maternal_dataset_starts.append(['All studies', total])
        return maternal_dataset_starts


    def child_prev_study_dataset(self):
        """Return the totals of all prev study child participant dataset.
        """
        child_dataset = ChildDataset.objects.all()
        data = []
        for dt in child_dataset:
            obj_dict = dt.__dict__
            try:
                maternal_dataset = MaternalDataset.objects.get(study_maternal_identifier=obj_dict.get('study_maternal_identifier'))
            except MaternalDataset.DoesNotExist:
                raise ValidationError(f"Missing mother of ID: {obj_dict.get('study_maternal_identifier')}")
            else:
                obj_dict.update(protocol=maternal_dataset.protocol)
            data.append(obj_dict)
            
        df = pd.DataFrame(data)
        df = df[["study_child_identifier", "protocol"]]
        child_dataset_starts = []
        total = 0
        for protocol in self.previous_studies:
            df_prev = df[df['protocol'] == protocol]
            child_dataset_starts.append([protocol, df_prev[df_prev.columns[0]].count()])
            total += df_prev[df_prev.columns[0]].count()

        child_dataset_starts.append(['All studies', total])
        return child_dataset_starts
        

    def locator_report(self):
        """Return a list of locator availability per prev study participant.
        """
        # Previous studies data
        data = []
        maternal_dataset = MaternalDataset.objects.all()
        df = read_frame(maternal_dataset, fieldnames=['protocol', 'study_maternal_identifier'])
        
        # Add total expected locators per study
        maternal_dataset_starts_dict = {}
        for protocol in self.previous_studies:
            df_prev = df[df['protocol'] == protocol]
            maternal_dataset_starts_dict[protocol] = df_prev[df_prev.columns[0]].count()
        dt = [maternal_dataset_starts_dict.get(prev_study) for prev_study in self.previous_studies]
        data.append(dt + [sum(dt)])
        
        #Add total locators per study
        locator_identifiers = CaregiverLocator.objects.all().values_list('study_maternal_identifier', flat=True)
        locator_identifiers = list(set(locator_identifiers))
        
        maternal_dataset = MaternalDataset.objects.filter(study_maternal_identifier__in=locator_identifiers)
        df = read_frame(maternal_dataset, fieldnames=['protocol', 'study_maternal_identifier'])
        
        maternal_dataset_starts_dict = {}
        for protocol in self.previous_studies:
            df_prev = df[df['protocol'] == protocol]
            maternal_dataset_starts_dict[protocol] = df_prev[df_prev.columns[0]].count()
        dt = [maternal_dataset_starts_dict.get(prev_study) for prev_study in self.previous_studies]
        data.append(dt + [sum(dt)])
        
        # Missing locators per prev study
        all_data = MaternalDataset.objects.all().values_list('study_maternal_identifier', flat=True)
        missing_locators_identifiers = list(set(all_data) - set(locator_identifiers))
        missing_locator_dataset = MaternalDataset.objects.filter(study_maternal_identifier__in=missing_locators_identifiers)
        df = read_frame(missing_locator_dataset, fieldnames=['protocol', 'study_maternal_identifier'])
        
        maternal_dataset_starts_dict = {}
        for protocol in self.previous_studies:
            df_prev = df[df['protocol'] == protocol]
            maternal_dataset_starts_dict[protocol] = df_prev[df_prev.columns[0]].count()
        dt = [maternal_dataset_starts_dict.get(prev_study) for prev_study in self.previous_studies]
        data.append(dt + [sum(dt)])
    
        totals_per_study = []
        count = 0
        for data_list in data:
            total += data_list[count]
        
        return data
        
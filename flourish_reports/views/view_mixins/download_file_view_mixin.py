import datetime
import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage

from ...identifiers import ExportIdentifier
from ...models import ExportFile


class DownloadReportMixin:

    def download_data(
            self, description=None, start_date=None,
            end_date=None, report_type=None, df=None):
        """
        This method is for saving files which will be later be
        downloaded by the user
        """

        """
        Preparing to upload the file
        """

        export_identifier = ExportIdentifier().identifier
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        documents_folder = 'documents'
        file_name = f'{export_identifier}_{timestamp}.csv'
        file_directory = os.path.join(settings.MEDIA_ROOT, documents_folder, report_type)

        """
        Check if the directory exist
        """
        if not os.path.exists(file_directory):
            os.mkdir(file_directory)

        final_path = os.path.join(file_directory, file_name)

        """
        If dataframes are passed as a list this section merges 
        the df into one single file
        """
        if type(df) == list:
            for single_df in df:
                # single_df.transpose()
                single_df.to_csv(final_path, mode='a', index=True)

        else:
            df.to_csv(final_path, encoding='utf-8', index=False)

        """
        Now save the actual path after exporting the data
        """
        export_file = ExportFile()
        export_file.export_identifier = export_identifier
        export_file.start_date = start_date
        export_file.end_date = end_date
        export_file.description = report_type
        export_file.document = os.path.join(documents_folder, report_type, file_name)
        export_file.save()

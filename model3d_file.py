import os
import uuid
import logging
from werkzeug.utils import secure_filename
import cadquery as cq

from exceptions import FileConversionError, InvalidFileTypeError, NoFileSelectedError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Model3DFile:
    def __init__(self, filename: str, file_bytes_provider, temp_folder: str):
        """
        :param filename: the provided file name, including extension, excluding absolute path
        :param file_bytes_provider: the function or closure to run for obtaining the file bytes
        :param temp_folder: the temporary folder to write intermediate file output to
        """
        self.stl_file_path = None
        self.step_file_path = None
        
        if filename == '':
            raise NoFileSelectedError('No selected file')

        self.file_id = str(uuid.uuid4())  # Generate a unique filename
        self._temp_folder = temp_folder
        self._process_file(filename, file_bytes_provider)

    def _process_file(self, filename: str, file_bytes):
        filename = secure_filename(filename)
        filename = filename.lower()
        if filename.endswith('.stl'):
            self.stl_file_path = self._save_file(file_bytes, 'stl')
        elif filename.endswith('.stp') or filename.endswith('.step'):
            self.step_file_path = self._save_file(file_bytes, 'stp')
            self.stl_file_path = os.path.join(self._temp_folder, self.file_id + '.stl')
            self._convert_to_stl()
        else:
            raise InvalidFileTypeError('Invalid file type')

    def _save_file(self, file_bytes, extension: str):
        file_path = os.path.join(self._temp_folder, f'{self.file_id}.{extension}')
        with open(file_path, 'wb') as f:
            f.write(file_bytes())

        return file_path

    def _convert_to_stl(self):
        try:
            # Import the STEP file from the filesystem
            imported = cq.importers.importStep(self.step_file_path)

            # Export to STL format in the temp folder
            cq.exporters.export(imported, self.stl_file_path)
        except Exception as e:
            # Handle exceptions that occur during conversion
            logger.error("Error converting file to STL: %s", e)
            raise FileConversionError('Error during file conversion') from e

    def __del__(self):
        # Destructor to remove existing files when the object is destroyed
        try:
            if self.step_file_path is not None and os.path.exists(self.step_file_path):
                os.remove(self.step_file_path)
            if self.stl_file_path is not None and os.path.exists(self.stl_file_path):
                os.remove(self.stl_file_path)
        except Exception as e:
            logger.error("Error removing files: %s", e)

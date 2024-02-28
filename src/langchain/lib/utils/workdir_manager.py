from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Union
import os
import shutil
import json


class WorkDirManager:
    _instance: 'WorkDirManager' = None
    _temp_dir: TemporaryDirectory = None
    _working_directory: Path = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WorkDirManager, cls).__new__(cls)
            cls._temp_dir = TemporaryDirectory()
            cls._working_directory = Path(cls._temp_dir.name)
        return cls._instance

    @classmethod
    def add_file(cls, filename, content_or_path: Union[str, bytes, Path], save_as_json=False):
        target_path = cls._working_directory / filename
        if save_as_json:
            with open(target_path, 'w') as file:
                json.dump(content_or_path, file)
        elif isinstance(content_or_path, Path) or os.path.isfile(content_or_path):
            shutil.copy(content_or_path, target_path)
        else:
            mode = 'wb' if isinstance(content_or_path, bytes) else 'w'
            with open(target_path, mode) as file:
                file.write(content_or_path)

        return target_path

    @classmethod
    def load_file(cls, filename: Path, return_path=False):
        file_path = cls._working_directory / filename
        if not file_path.exists():
            return None

        if return_path:
            return file_path

        with open(file_path, 'r') as file:
            return file.read()

    @classmethod
    def list_files(cls):
        return [f for f in cls._working_directory.iterdir() if f.is_file()]

    @classmethod
    def delete_file(cls, filename):
        file_path = cls._working_directory / filename
        if file_path.exists():
            file_path.unlink()
            return True
        return False

    @classmethod
    def cleanup(cls):
        if cls._temp_dir:
            cls._temp_dir.cleanup()
            cls._temp_dir = None
            cls._instance = None
            cls._working_directory = None


# Probably not best practice instantiating it here...
WorkDirManager()

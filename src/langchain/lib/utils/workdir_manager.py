from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Union, Optional
import os
import shutil
import json
from datetime import datetime
from geopandas import GeoDataFrame


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
    def add_file(cls, filename, content_or_path: Union[GeoDataFrame, str, bytes, Path], save_as_json=False) -> Path:
        filename = Path(filename).name
        target_path: Path = cls._working_directory / filename
        if save_as_json:
            if isinstance(content_or_path, GeoDataFrame):
                with open(target_path, 'w') as file:
                    file.write(content_or_path.to_json())
            else:
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
    def load_file(cls, filename: Union[str, Path], return_path=False) -> Optional[Union[str, Path]]:
        if isinstance(filename, str):
            filename = Path(filename)

        file_path = cls._working_directory / filename.name
        if not file_path.exists():
            return None

        if return_path:
            return file_path

        try:
            with open(file_path, 'r') as file:
                return file.read()
        except IOError as e:
            print(f"Error opening file: {e}")
            return None

    @staticmethod
    def _filter_file_names(file_names: list[Path], exclude_extensions):
        filtered_file_names = []
        for file_name in file_names:
            if file_name.name == 'README':
                continue
            if file_name.suffix not in exclude_extensions:
                filtered_file_names.append(file_name)
        return filtered_file_names

    @classmethod
    def list_files(cls, exclude_extensions=['.shx', '.cpg', '.dbf', '.prj']):
        file_names = [f for f in cls._working_directory.iterdir()]
        print(len(file_names))
        filtered_files = cls._filter_file_names(
            file_names, exclude_extensions)
        print(len(filtered_files))
        return filtered_files

    @classmethod
    def delete_file(cls, filename):
        filename = Path(filename).name
        file_path = cls._working_directory / filename
        if file_path.exists():
            file_path.unlink()
            return True
        return False

    @classmethod
    def get_abs_path(cls):
        return str(cls._working_directory)

    @classmethod
    def cleanup(cls):
        if cls._temp_dir:
            cls._temp_dir.cleanup()
            cls._temp_dir = None
            cls._instance = None
            cls._working_directory = None

    @classmethod
    def get_latest_file_added(cls):
        files = cls.list_files()
        if not files:
            return None

        # Debugging: Verify each symlink before proceeding
        for file in files:
            if not file.resolve().exists():
                print(f"Broken link or missing file: {file}")
                continue

        latest_file = max(files, key=lambda f: f.stat(
            follow_symlinks=True).st_mtime)
        return datetime.fromtimestamp(latest_file.stat(follow_symlinks=True).st_mtime)

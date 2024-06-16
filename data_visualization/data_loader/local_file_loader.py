import os
from enum import Enum
from typing import Any
from pandas import (
    read_csv,
    read_excel,
    read_parquet,
    read_json,
    read_pickle,
    DataFrame
)
class FileExtension(Enum):
    """
    Enumerates supported file extensions and their associated file types.

    Attributes:
        CSV (str): Represents CSV files.
        JSON (str): Represents JSON files.
        PARQUET (str): Represents Parquet files.
        EXCEL (tuple): Represents Excel files with extensions "xlsx" or "xls".
        PICKLE (tuple): Represents Pickle files with extensions "pickle", "pkl", or "p".
    """

    CSV = "csv"
    JSON = "json"
    PARQUET = "parquet"
    EXCEL = ("xlsx", "xls")
    PICKLE = ("pickle", "pkl", "p")

class File:
    """
    Encapsulates the functionality of reading files into pandas DataFrames.

    Methods:
        _get_extension(self) -> str:
            Determines the file extension from the stored filepath.

        read(self, file_path: str = None) -> DataFrame:
            Reads the contents of a file into a pandas DataFrame.
    """
    _EXTENSIONS: dict[FileExtension, Any]= {
        FileExtension.CSV: read_csv,
        FileExtension.JSON: read_json,
        FileExtension.PARQUET: read_parquet,
        FileExtension.EXCEL: read_excel,
        FileExtension.PICKLE: read_pickle
    }

    def __init__(self) -> None:
        self.data: DataFrame = None
        self.file_path: str = None
        self.extension: str = None

    def _get_extension(self) -> str:
        """
        Determines the file extension from the stored filepath.

        Returns:
            str: The file extension (e.g., "csv", "json", "parquet").

        Raises:
            ValueError: If the file extension is not supported.
        """
        _, file_extension = os.path.splitext(self.file_path)
        file_extension = file_extension[1:]
        for ext in FileExtension:
            if file_extension in ext.value:
                return ext
        raise ValueError(f'Unsupported file extension: {file_extension}')

    def read(self, file_path: str = None) -> DataFrame:
        """
        Args:
        file_path (str): Path to the file to read. Defaults to None.

        Returns:
            DataFrame containing the read data.

        Raises:
            ValueError: If the file extension is not supported.

        Supported File Extensions:
            - CSV
            - JSON
            - Parquet
            - Excel
            - Pickle

        Read a file from a specified path:
            data = File().read("data.csv")
        """
        if file_path is not None:
            self.file_path = file_path  # Update file_path if provided

        self.extension = self._get_extension()
        read_func = self._EXTENSIONS.get(self.extension)

        if read_func is None:
            raise ValueError(f'Unsupported file extension: {self.extension}')

        self.data = read_func(self.file_path)  # Store the read data
        return self.data


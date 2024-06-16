import opendatasets as od
import json

# TODO: Implement KaggleFile class
class KaggleFile:
    def __init__(self) -> None:
        pass

    def download_kaggle_dataset(url: str = None, dry_run: bool = False):
        try:
            od.download(dataset_id_or_url=url, data_dir='./Datasets', dry_run = dry_run)
        except ValueError as e:
            raise "Invalid URL."

    def set_credentials(username: str = None, key: str = None):
        credentials = {
            "username": username,
            "key": key
        }
        try:
            with open('kaggle.json', 'w') as f:
                json.dump(credentials, f)
        except ValueError as e:
            raise "JSON file was not found."

import yaml
import os

CONFIG_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config', 'settings.yaml'))

def load_config():
    with open(CONFIG_FILE_PATH, 'r') as f:
        return yaml.safe_load(f)

def save_config(updated_config):
    with open(CONFIG_FILE_PATH, "w") as f:
        yaml.dump(updated_config, f)

def save_config(data):
    with open("config/settings.yaml", "w") as f:
        yaml.safe_dump(data, f)
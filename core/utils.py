import yaml

def load_config():
    with open("config/settings.yaml", "r") as file:
        return yaml.safe_load(file)

import json

def load_config(file_path='config.json'):
    """
    Loads configuration from a JSON file.

    Parameters:
        file_path (str): The path to the configuration file.

    Returns:
        dict: A dictionary containing configuration parameters.

    Raises:
        FileNotFoundError: If the configuration file is not found.
        ValueError: If the configuration file is missing required keys.
    """
    try:
        with open(file_path, 'r') as file:
            config = json.load(file)
        return config
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file {file_path} not found.")
    except json.JSONDecodeError:
        raise ValueError(f"Configuration file {file_path} contains invalid JSON.")

from typing import Dict, Tuple


def parse_config(filename: str) -> Dict[str, object]:
    """
    Parse the configuration file and return a dictionary
    containing all configuration values.
    """

    config: Dict[str, object] = {}

    try:
        with open(filename, "r") as file:
            for line in file:
                line = line.strip()

                # ignore empty lines and comments
                if not line or line.startswith("#"):
                    continue

                if "=" not in line:
                    raise ValueError(f"Invalid line in config: {line}")

                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()

                config[key] = value

    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found: {filename}")

    # convert values
    try:
        config["WIDTH"] = int(config["WIDTH"])
        config["HEIGHT"] = int(config["HEIGHT"])

        config["ENTRY"] = tuple(map(int, config["ENTRY"].split(",")))
        config["EXIT"] = tuple(map(int, config["EXIT"].split(",")))

        config["PERFECT"] = config["PERFECT"].lower() == "true"

    except KeyError as e:
        raise ValueError(f"Missing required config key: {e}")

    return config
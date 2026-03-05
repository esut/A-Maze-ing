from typing import Dict, Tuple


def parse_config(filename: str) -> Dict:
    """
    Read configuration file and return a dictionary.
    """

    config: Dict = {}

    with open(filename, "r") as file:
        for line in file:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            key, value = line.split("=")
            config[key] = value

    config["WIDTH"] = int(config["WIDTH"])
    config["HEIGHT"] = int(config["HEIGHT"])

    x, y = config["ENTRY"].split(",")
    config["ENTRY"] = (int(x), int(y))

    x, y = config["EXIT"].split(",")
    config["EXIT"] = (int(x), int(y))

    config["PERFECT"] = config["PERFECT"].lower() == "true"

    return config
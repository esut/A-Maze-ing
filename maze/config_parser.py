from typing import Dict, Tuple


def parse_config(filename: str) -> Dict[str, object]:
    config: Dict[str, object] = {}

    with open(filename, "r") as file:
        for line in file:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            key, value = line.split("=")
            config[key] = value

    width = int(config["WIDTH"])
    height = int(config["HEIGHT"])

    entry = tuple(map(int, config["ENTRY"].split(",")))
    exit = tuple(map(int, config["EXIT"].split(",")))

    seed = int(config["SEED"])

    return {
        "WIDTH": width,
        "HEIGHT": height,
        "ENTRY": entry,
        "EXIT": exit,
        "OUTPUT_FILE": config["OUTPUT_FILE"],
        "SEED": seed,
    }
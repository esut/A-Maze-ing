from typing import Dict, Any


def parse_config(filename: str) -> Dict[str, Any]:
    """Read configuration file and return a dictionary.

    Args:
        filename: Path to the configuration file

    Returns:
        Dictionary containing parsed configuration values

    Raises:
        FileNotFoundError: If the configuration file doesn't exist
        ValueError: If the configuration format is invalid
    """
    config: Dict[str, Any] = {}

    try:
        with open(filename, "r") as file:
            line_num: int = 0
            for line in file:
                line_num += 1
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue

                # Parse KEY=VALUE format
                if "=" not in line:
                    raise ValueError(
                        f"Line {line_num}: Invalid format. "
                        f"Expected KEY=VALUE, got: {line}"
                    )

                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()

                if not key:
                    raise ValueError(
                        f"Line {line_num}: Empty key in configuration"
                    )

                config[key] = value

    except FileNotFoundError:
        raise FileNotFoundError(
            f"Configuration file '{filename}' not found"
        )

    # Validate required keys
    required_keys = ["WIDTH", "HEIGHT", "ENTRY", "EXIT",
                     "OUTPUT_FILE", "PERFECT"]
    missing_keys = [key for key in required_keys if key not in config]
    if missing_keys:
        raise ValueError(
            f"Missing required configuration keys: {', '.join(missing_keys)}"
        )

    # Parse and validate WIDTH
    try:
        config["WIDTH"] = int(config["WIDTH"])
        if config["WIDTH"] <= 0:
            raise ValueError("WIDTH must be positive")
    except ValueError as e:
        raise ValueError(f"Invalid WIDTH value: {e}")

    # Parse and validate HEIGHT
    try:
        config["HEIGHT"] = int(config["HEIGHT"])
        if config["HEIGHT"] <= 0:
            raise ValueError("HEIGHT must be positive")
    except ValueError as e:
        raise ValueError(f"Invalid HEIGHT value: {e}")

    # Parse and validate ENTRY coordinates
    try:
        entry_parts = config["ENTRY"].split(",")
        if len(entry_parts) != 2:
            raise ValueError("ENTRY must be in format 'x,y'")
        x, y = int(entry_parts[0].strip()), int(entry_parts[1].strip())
        config["ENTRY"] = (x, y)
    except ValueError as e:
        raise ValueError(f"Invalid ENTRY coordinates: {e}")

    # Parse and validate EXIT coordinates
    try:
        exit_parts = config["EXIT"].split(",")
        if len(exit_parts) != 2:
            raise ValueError("EXIT must be in format 'x,y'")
        x, y = int(exit_parts[0].strip()), int(exit_parts[1].strip())
        config["EXIT"] = (x, y)
    except ValueError as e:
        raise ValueError(f"Invalid EXIT coordinates: {e}")

    # Parse PERFECT flag
    config["PERFECT"] = config["PERFECT"].lower() == "true"

    # Parse optional SEED
    if "SEED" in config:
        try:
            config["SEED"] = int(config["SEED"])
        except ValueError:
            raise ValueError(
                f"Invalid SEED value: {config['SEED']}. Must be an integer"
            )

    return config

import sys

from pydantic import BaseModel, Field, NonNegativeInt

from custom_print import print_yellow
from utils import read_config


class WindowConfig(BaseModel):
    """Configuration for the window

    Args:
        width: The width of the window. Defaults to 1280.
        height: The height of the window. Defaults to 720.
        seed: The seed for the random number generator. Defaults to 42.
        pacgum: The seed for the random number generator. Defaults to 42.

    NOTE: The window size is not configurable from the config file,
          it is fixed to 1280x720 which is provided in this validation model
    """

    width: int = Field(1920, ge=500, description="Width must be at least 500")
    height: int = Field(
        1080, ge=500, description="Height must be at least 500"
    )
    seed: NonNegativeInt = 42
    pacgum: NonNegativeInt = 42


class PlayerConfig(BaseModel):
    lives: NonNegativeInt = 3
    points_per_ghost: NonNegativeInt = 200
    points_per_pacgum: NonNegativeInt = 15
    points_per_super_pacgum: NonNegativeInt = 50
    highscore_filename: str = "highscores.json"
    level_max_time: NonNegativeInt = 90


class MapConfig(BaseModel):
    width: NonNegativeInt = 23
    height: NonNegativeInt = 14


# Validate the config file, (the above model is realted to it)
class Config_Validator(BaseModel):
    window: WindowConfig
    player: PlayerConfig
    maps: list[MapConfig]


def check_missing_config_data(config: dict) -> dict:
    """Check structural integrity of configuration and strip None or negative values.

    Keys with None or negative values are removed from the dictionary so that
    Pydantic automatically falls back to default field values.

    Args:
        config (dict): Raw configuration dictionary from JSON.

    Returns:
        dict: The cleaned configuration dictionary.

    Raises:
        ValueError: If payload or top-level sections are missing or have invalid types.
    """
    if not isinstance(config, dict):
        raise ValueError(
            "Invalid configuration: Payload must be a dictionary."
        )

    missing_errors = []

    # Standard dictionary sections to validate and clean
    expected_dict_sections = ["window", "player"]

    # Validate and clean 'window' and 'player' sections
    for section_name in expected_dict_sections:
        if section_name not in config or config[section_name] is None:
            missing_errors.append(
                f"Missing top-level section: '{section_name}'"
            )
            continue

        section_data = config[section_name]
        if not isinstance(section_data, dict):
            missing_errors.append(
                f"Section '{section_name}' must be a dictionary."
            )
            continue

        # Remove keys with None or negative numeric values so later pydantic
        # can fall back to default values
        # using list to avoid pyther error 'change dict while iterating it
        for key, val in list(section_data.items()):
            if val is None or (isinstance(val, (int, float)) and val < 0):
                missing_errors.append(
                    "Invalid value "
                    f"'{val}' for key '{key}' in section '{section_name}'."
                )
                del section_data[key]

    # Validate and clean 'maps' list section
    if "maps" not in config or config["maps"] is None:
        missing_errors.append("Missing top-level section: 'maps'")
    elif not isinstance(config["maps"], list):
        missing_errors.append("Section 'maps' must be a list.")
    else:
        for index, map_item in enumerate(config["maps"]):
            if not isinstance(map_item, dict):
                missing_errors.append(
                    f"Item in 'maps' at index {index} is not a dictionary."
                )
                continue

            # Remove keys with None or negative numeric values inside map dicts
            for key, val in list(map_item.items()):
                if val is None or (isinstance(val, (int, float)) and val < 0):
                    missing_errors.append(
                        "Invalid value "
                        f"'{val}' for key '{key}' in map at index {index}."
                    )
                    del map_item[key]

    # Raise ValueError if top-level structure check failed
    if missing_errors:
        message = "\n - ".join(missing_errors)
        print_yellow(
            f"Config check failed:\n - {message}\n Fallback to default values."
        )

    return config


def handle_config_validation() -> dict:
    """Handle the config file and validate it"""

    if len(sys.argv) < 2:
        print_yellow("Warning: Please provide a config file")
        sys.exit(1)

    # Read config file, validate it, convert it back to dict
    config_data = read_config()
    try:
        half_validated_config = check_missing_config_data(config_data)
    except Exception as e:
        print_yellow(f"{e}")
        # DO not exit so pydantic validator set
        # default for missings or malformed data
    validated_config: Config_Validator = Config_Validator.model_validate(
        half_validated_config
    )
    config: dict = validated_config.model_dump()

    return config

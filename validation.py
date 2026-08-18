from pydantic import BaseModel, Field, NonNegativeInt


class WindowConfig(BaseModel):
    width: int = Field(..., ge=500, description="Width must be at least 500")
    height: int = Field(..., ge=500, description="Height must be at least 500")
    seed: NonNegativeInt
    pacgum: NonNegativeInt


class PlayerConfig(BaseModel):
    lives: NonNegativeInt
    points_per_ghost: NonNegativeInt
    points_per_pacgum: NonNegativeInt
    points_per_super_pacgum: NonNegativeInt
    highscore_filename: str
    level_max_time: NonNegativeInt


class MapConfig(BaseModel):
    width: NonNegativeInt
    height: NonNegativeInt


# Validate the config file, (the above model is realted to it)
class Config_Validator(BaseModel):
    window: WindowConfig
    player: PlayerConfig
    maps: list[MapConfig]

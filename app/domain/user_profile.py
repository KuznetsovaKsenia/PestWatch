from enum import Enum


class UserProfile(str, Enum):
    HUMAN = "HUMAN"
    GARDEN = "GARDEN"
    VEGETABLE_GARDEN = "VEGETABLE_GARDEN"
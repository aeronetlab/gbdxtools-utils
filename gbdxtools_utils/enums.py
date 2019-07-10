import enum


class LoadStatus(enum.Enum):
    SUCCESS = 0
    FAILED = 1
    NOT_IN_CATALOG = 2

from enum import IntEnum


class BookingStatus(IntEnum):
    active = 0
    cancelled = 1
    completed = 2
    deleted = 3
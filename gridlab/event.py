from enum import StrEnum


class Event(StrEnum):
    MOVE = 'move'
    DIE = 'die'
    KEY_PICKUP = 'key_pickup'
    DOOR_UNLOCK = 'door_unlock'
    TIMER_RESET = 'timer_reset'

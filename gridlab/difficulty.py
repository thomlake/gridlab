from enum import StrEnum


class Difficulty(StrEnum):
    TRIVIAL = 'trivial'
    EASY = 'easy'
    MODERATE = 'moderate'
    HARD = 'hard'
    EXPERT = 'expert'
    UNCLASSIFIED = 'unclassified'


def get_difficulty_score(d: Difficulty):
    return list(Difficulty).index(d)

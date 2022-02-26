from enum import Enum


class ResultCode(Enum):
    USER_NAME = 1
    E_USER_NAME = 2
    E_ALLIANCE_NAME = 3
    LEVEL_1 = 4
    LEVEL_2 = 5
    LEVEL_3 = 6
    E_LEVEL_3 = 7
    E_LEVEL_2 = 8
    E_LEVEL_1 = 9
    SENPO_1_1 = 10
    SENPO_1_2 = 11
    SENPO_1_3 = 12
    SENPO_2_1 = 13
    SENPO_2_2 = 14
    SENPO_2_3 = 15
    SENPO_3_1 = 16
    SENPO_3_2 = 17
    SENPO_3_3 = 18
    E_SENPO_3_1 = 19
    E_SENPO_3_2 = 20
    E_SENPO_3_3 = 21
    E_SENPO_2_1 = 22
    E_SENPO_2_2 = 23
    E_SENPO_2_3 = 24
    E_SENPO_1_1 = 25
    E_SENPO_1_2 = 26
    E_SENPO_1_3 = 27


class SuccessCode(Enum):
    INSERT = 0
    UPDATE = 1
    FAILED = 2

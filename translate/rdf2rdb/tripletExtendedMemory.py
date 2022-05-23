from translate.rdf2rdb.tripletExtended import TripletExtended
from typing import List


class TripletExtendedMemory:
    def __init__(self):
        self.level_lowest = 1
        self.level_now = 1
        self.level_max = 1
        self.level_max_allowed = 1
        self.tps_ext_arr_arr: List[List[TripletExtended]] = []

    def get_allowed_memory(self) -> List[TripletExtended]:
        combined = []
        for i in range(0, self.level_max_allowed):
            combined.extend(self.tps_ext_arr_arr[i])
        return combined

    def set_memory(self, level: int, tps_ext_arr: List[TripletExtended]) -> None:
        self.level_max = level if level > self.level_max else self.level_max
        if len(self.tps_ext_arr_arr) + 1 < level:
            raise Exception(f"You can not set memory level {level} \n"
                            f"because your memory currently has only {len(self.tps_ext_arr_arr)} levels. \n"
                            f"It is more than one step behind")
        if len(self.tps_ext_arr_arr) < level:
            self.tps_ext_arr_arr.append([])
        self.tps_ext_arr_arr[level - 1] = tps_ext_arr

    def forget_top_memory(self) -> None:
        self.level_max_allowed -= 1
        self.tps_ext_arr_arr.pop()
        self.level_max -= 1

    def align_levels_to(self, level: int) -> None:
        while self.level_max > level:
            self.forget_top_memory()
        return

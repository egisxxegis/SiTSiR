from typing import List

from SQL.join import Join
from SQL.select import Select
from SQL.where import Where


class Union:
    def __init__(self):
        self.select = Select()
        self.joins_arr: List[Join] = []
        self.where = Where()

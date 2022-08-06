#!/usr/bin/env python3
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
import fileinput
from re import finditer, search
from typing import Dict, List

class ChairKind(Enum):
    Wooden = 'W'
    Plastic = 'P'
    Sofa = 'S'
    China = 'C'

ChairCount = Dict[ChairKind, int]

@dataclass
class RoomRow():
    y: int
    x_begin: int
    x_end: int

@dataclass
class Room():
    name: str = 'UNKNOWN'
    chair_count: ChairCount = field(default_factory = dict)
    rows: List[RoomRow] = field(default_factory = list)
    is_completed: bool = False

    def __repr__(self):
        return f'{self.name}:\n{chair_count_stringified(self.chair_count)}'


def chair_count_stringified(chair_count: ChairCount) -> str:
    return ', '.join([f'{c.value}: {chair_count[c]}' for c in ChairKind])


def chair_count_from_rooms(rooms: List[Room]) -> ChairCount:
    result: ChairCount = defaultdict(int)

    for r in rooms:
        for k, v in r.chair_count.items():
            result[k] += v
        
    return result


def rooms_from_plan(plan: str) -> List[Room]:
    result: List[Room] = []

    rows = plan.split('\n')
    rooms: List[Room] = []

    for y, row in enumerate(rows):
        walls = list(finditer(r'[^/\\|+-]+', row))
        if not walls:
            continue

        room_rows = [RoomRow(y, wall.start(), wall.end()) for wall in walls]
        for room in rooms:
            for room_row in room_rows:
                if max(room.rows[-1].x_begin, room_row.x_begin) < min(room.rows[-1].x_end, room_row.x_end):
                    room.rows.append(room_row)
                    room_rows.remove(room_row)
                    break
            else: # no room_row added => is_completed
                text = ''.join([rows[s.y][s.x_begin:s.x_end] for s in room.rows])
                name = search(r'\([a-z ]+\)', text)
                room.is_completed = True
                room.chair_count = {c: text.count(c.value) for c in ChairKind}
                room.name = name[0][1:-1] if name else 'UNKNOWN'
                result.append(room)
                
        # remove completed rooms for next iteration
        rooms = [r for r in rooms if r.is_completed == False]

        # create new rooms with remaining room_rows
        for room_row in room_rows:
            room = Room()
            room.rows.append(room_row)
            rooms.append(room)

    result = list(filter(lambda room: room.name != 'UNKNOWN', result))

    return result


if __name__ == '__main__':
    plan = ''
    for line in fileinput.input(encoding="utf-8"):
        plan += line
         
    rooms = rooms_from_plan(plan)
    chair_count = chair_count_from_rooms(rooms)

    print(f'total:\n{chair_count_stringified(chair_count)}')
    for r in sorted(rooms, key=lambda room: room.name):
        print(r)

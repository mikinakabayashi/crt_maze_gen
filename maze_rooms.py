import random
from functools import reduce

try:
    from msvcrt import getch
except ImportError:
    import sys
    import tty
    import termios

    def getch():

        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            return sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)


NORTH = 1
WEST = 2
SOUTH = 4
EAST = 8

DIRECTIONS = [
    NORTH, WEST, SOUTH, EAST
]

OFFSETS = {
    NORTH: (0, -1),
    WEST: (-1, 0),
    SOUTH: (0, 1),
    EAST: (1, 0),
}


def offset(pos, dir):
    ofs = OFFSETS[dir]
    return (pos[0] + ofs[0], pos[1] + ofs[1])


OPPOSITE = {
    NORTH: SOUTH,
    WEST: EAST,
    SOUTH: NORTH,
    EAST: WEST,
}

LINES = {
    0: " ",
    NORTH: "╵",
    WEST: "╴",
    SOUTH: "╷",
    EAST: "╶",
    (NORTH | WEST): "┘",
    (NORTH | SOUTH): "│",
    (NORTH | EAST): "└",
    (WEST | SOUTH): "┐",
    (WEST | EAST): "─",
    (SOUTH | EAST): "┌",
    (NORTH | WEST | SOUTH): "┤",
    (NORTH | WEST | EAST): "┴",
    (NORTH | SOUTH | EAST): "├",
    (WEST | SOUTH | EAST): "┬",
    (NORTH | WEST | SOUTH | EAST): "┼",
}

LINE_UNDEFINED = "▒"

CONNECTION_WEIGHT = [1.0, 0.9, 0.25, 0.15]


def has_neighbor(rooms, pos):
    return any(map(lambda d: offset(pos, d) in rooms, DIRECTIONS))


def create_room(rooms, pos):
    if pos in rooms:
        return
    if not has_neighbor(rooms, pos):
        return
    possible_connection = list(DIRECTIONS)
    found_connection = []
    for dir in list(possible_connection):
        neighbor = offset(pos, dir)
        if neighbor in rooms:
            if rooms[neighbor] & OPPOSITE[dir]:
                found_connection.append(dir)
            possible_connection.remove(dir)
    random.shuffle(possible_connection)
    for dir in possible_connection:
        weight = CONNECTION_WEIGHT[len(found_connection)]
        if random.random() < weight:
            found_connection.append(dir)
    rooms[pos] = reduce(lambda a, c: a | c, found_connection, 0)


def create_neighbor_rooms(rooms, center, r):
    r = abs(r)
    north = center[1] - r
    south = center[1] + r + 1
    west = center[0] - r
    east = center[0] + r + 1
    new_rooms = filter(lambda p: p[0] <= r and p[1] not in rooms,sorted(
        [(abs(x - center[0]) + abs(y - center[1]), (x, y)) for y in range(north, south) for x in range(west, east)],
        key=lambda p:p[0]
    ))
    for _, pos in new_rooms:
        create_room(rooms, pos)


def display(rooms, north, west, south, east, cursor = None):
    for y in range(north, south):
        row = ""
        for x in range(west, east):
            room_char = LINES.get(rooms.get((x, y), None), LINE_UNDEFINED)
            if (x, y) == cursor:
                row += f"\x1b[41m{room_char}\x1b[0m"
            else:
                row += room_char
        print(row)
    if cursor is not None:
        print(cursor, end="  ")
    print("Arrows: Move, q: Quit   ")


def update_display(rooms, r_offset, r_width, center, erase=True):
    north = center[1] + r_offset
    south = north + r_width
    west = center[0] + r_offset
    east = west + r_width
    if erase:
        print(f"\x1b[{r_width+1}A", end="")
    display(rooms, north, west, south, east, center)


rooms = {(0, 0): (NORTH | WEST | SOUTH | EAST)}

r_offset = -9
r_width = 19

pos = (0, 0)
create_neighbor_rooms(rooms, pos, r_offset)
update_display(rooms, r_offset, r_width, pos, False)

while True:
    key = ord(getch())
    if key == ord("q"):
        break
    elif key == ord('w'):
        if rooms[pos] & NORTH:
            pos = offset(pos, NORTH)
            create_neighbor_rooms(rooms, pos, r_offset)
            update_display(rooms, r_offset, r_width, pos)
        continue
    elif key == ord('s'):
        if rooms[pos] & SOUTH:
            pos = offset(pos, SOUTH)
            create_neighbor_rooms(rooms, pos, r_offset)
            update_display(rooms, r_offset, r_width, pos)
        continue
    elif key == ord('d'):
        if rooms[pos] & EAST:
            pos = offset(pos, EAST)
            create_neighbor_rooms(rooms, pos, r_offset)
            update_display(rooms, r_offset, r_width, pos)
        continue
    elif key == ord('a'):
        if rooms[pos] & WEST:
            pos = offset(pos, WEST)
            create_neighbor_rooms(rooms, pos, r_offset)
            update_display(rooms, r_offset, r_width, pos)
        continue

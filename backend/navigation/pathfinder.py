# navigation/pathfinder.py
from collections import deque
from navigation.graph import load_graph


def find_path(room_from: str, room_to: str, device_id: str = None) -> list | None:
    graph = load_graph(device_id)

    if room_from not in graph or room_to not in graph:
        return None
    if room_from == room_to:
        return []

    queue   = deque()
    visited = set()
    queue.append((room_from, []))
    visited.add(room_from)

    while queue:
        current, path = queue.popleft()
        for edge in graph[current]:
            voisin   = edge["voisin"]
            angle    = edge["angle"]
            new_path = path + [{
                "de":    current,
                "vers":  voisin,
                "angle": angle     # ← angle absolu stocké
            }]
            if voisin == room_to:
                return new_path
            if voisin not in visited:
                visited.add(voisin)
                queue.append((voisin, new_path))

    return None
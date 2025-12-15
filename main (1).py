# Name: Hyunmin Kim
# Date: 2025-10-03
# CPSC383: Assignment 1
# Tutorial: 01
# UCID: 30112596

from aegis_game.stub import *
import heapq, math

# ------------------------------------
# Config / Globals
# ------------------------------------

ORDER = [
    Direction.NORTH, Direction.NORTHEAST, Direction.EAST, Direction.SOUTHEAST,
    Direction.SOUTH, Direction.SOUTHWEST, Direction.WEST, Direction.NORTHWEST
]

goal_cached = None  # Survivor Location once discovered

# ------------------------------------
# Heuristic & Costs
# ------------------------------------

def heuristic(a, b):
    """
    Compute the octile distance between two points (a, b).
    This is admissible for 8-connected grids and combines
    Manhattan distance with diagonal movement.
    """
    dx = abs(a.x - b.x)
    dy = abs(a.y - b.y)
    return dx + dy + (math.sqrt(2.0) - 2.0) * min(dx, dy)

def edge_cost(src_loc, d):
    """
    Get the movement cost from a source location in direction d.
    Returns:
      - float: cost value if available and valid
      - None: if blocked or infinite
    Defaults unseen costs to 1.0 (optimistic for replanning).
    """
    info = get_cell_info_at(src_loc)
    try:
        c = float(info.move_costs[d])
        if c <= 0.0 or c == float("inf"):
            return None
        return c
    except Exception:
        return 1.0

def dest_move_cost(loc):
    """
    Get the cost of entering a destination cell.
    Reads structured field `move_cost`, or parses from string
    if not directly available. Falls back to 1.0.
    """
    info = get_cell_info_at(loc)
    try:
        c = float(info.move_cost)
        if c > 0.0 and c != float("inf"):
            return c
    except Exception:
        pass
    try:
        s = str(info)
        idx = s.find("Move Cost:")
        if idx >= 0:
            tail = s[idx + len("Move Cost:"):].strip()
            num = ""
            k = 0
            while k < len(tail) and (tail[k].isdigit() or tail[k] == "."):
                num = num + tail[k]
                k = k + 1
            if len(num) > 0:
                c2 = float(num)
                if c2 > 0.0 and c2 != float("inf"):
                    return c2
    except Exception:
        pass
    return 1.0

# ------------------------------------
# Safety checks: killers / rubble / traps
# ------------------------------------

def is_killer(dest_loc):
    """
    Check if a given location is a 'killer' cell.
    Examines structured fields, layers, top_layer, or string
    representation of the cell to catch various cases.
    """
    info = get_cell_info_at(dest_loc)
    try:
        if info.is_killer_cell():
            return True
    except Exception:
        pass
    try:
        if hasattr(info, "layers"):
            L = getattr(info, "layers")
            try:
                _ = iter(L)
                for obj in L:
                    try:
                        if "killer" in str(obj).lower():
                            return True
                    except Exception:
                        pass
            except Exception:
                pass
    except Exception:
        pass
    try:
        if "killer" in str(info.top_layer).lower():
            return True
    except Exception:
        pass
    try:
        if "killer" in str(info).lower():
            return True
    except Exception:
        pass
    return False

def looks_like_rubble_obj(obj):
    """
    Classify an object as rubble or trap based on:
      - energy_required (>=500 = trap)
      - string containing 'rubble'
    Returns: "trap", "rubble", or None
    """
    try:
        if hasattr(obj, "id") and hasattr(obj, "energy_required"):
            _ = int(getattr(obj, "id"))
            er = int(getattr(obj, "energy_required"))
            if er >= 500:
                return "trap"
            return "rubble"
    except Exception:
        pass
    try:
        s = str(obj).lower()
        if "rubble" in s:
            return "rubble"
    except Exception:
        pass
    return None

def cell_has_rubble_or_trap(dest_loc):
    """
    Check if a cell contains rubble or trap objects
    by scanning its layers or top_layer.
    Returns: "rubble", "trap", or None
    """
    info = get_cell_info_at(dest_loc)
    try:
        if hasattr(info, "layers"):
            L = getattr(info, "layers")
            try:
                _ = iter(L)
                for item in L:
                    tag = looks_like_rubble_obj(item)
                    if tag is not None:
                        return tag
            except Exception:
                pass
    except Exception:
        pass
    try:
        tag2 = looks_like_rubble_obj(info.top_layer)
        if tag2 is not None:
            return tag2
    except Exception:
        pass
    try:
        if "rubble" in str(info).lower():
            return "rubble"
    except Exception:
        pass
    return None

def edge_rubble_or_trap(src_loc, d):
    """
    Classify the edge (src -> src+d) by cost:
      - "trap": cost >= 500
      - "rubble": cost > 1
      - "ok": cost <= 1
      - "blocked": invalid edge
    """
    c = edge_cost(src_loc, d)
    if c is None:
        return "blocked"
    if c >= 500.0:
        return "trap"
    if c > 1.0:
        return "rubble"
    return "ok"

def diagonal_blocked(cur, d):
    """
    Placeholder for diagonal corner-cutting check.
    Currently always returns False (no blocking).
    """
    return False

# ------------------------------------
# Neighbor expansion
# ------------------------------------

def neighbors(loc):
    """
    Generate valid neighbor cells from a given location.
    Skips killers and traps but allows rubble.
    Respects diagonal corner-block rules.
    Returns: list of (next_loc, direction, cost, tie_idx)
    """
    out = []
    i = 0
    while i < len(ORDER):
        d = ORDER[i]
        nxt = Location(loc.x + d.dx, loc.y + d.dy)
        if on_map(nxt):
            if d.dx != 0 and d.dy != 0 and diagonal_blocked(loc, d):
                log("Blocking diagonal {} from {} (unsafe corner)".format(d, loc))
                i = i + 1
                continue
            if is_killer(nxt):
                log("Skipping killer at {}".format(nxt))
                i = i + 1
                continue
            mc = dest_move_cost(nxt)
            if mc >= 500.0:
                log("Skipping TRAP CELL at {} (dest move_cost={})".format(nxt, mc))
                i = i + 1
                continue
            edge_tag = edge_rubble_or_trap(loc, d)
            if edge_tag == "trap":
                log("Skipping TRAP edge {} -> {} (very high cost)".format(loc, nxt))
                i = i + 1
                continue
            if edge_tag == "blocked":
                i = i + 1
                continue
            c = edge_cost(loc, d)
            if c is not None:
                out.append((nxt, d, c, i))
        i = i + 1
    return out

# ------------------------------------
# A* Search
# ------------------------------------

def astar(start, goal):
    """
    Run A* search to find lowest-cost path from start to goal.
    Uses octile heuristic and neighbor expansion rules.
    Returns: list of Directions, or None if no safe path.
    """
    if start == goal:
        return []

    pq = []  # (f, tie_idx, g, loc, path)
    f0 = heuristic(start, goal)
    heapq.heappush(pq, (f0, 0, 0.0, start, []))
    best_g = {start: 0.0}

    while len(pq) > 0:
        f, tie_idx, g, cur, path = heapq.heappop(pq)
        if cur == goal:
            log("A* path found: length={} cost={}".format(len(path), g))
            return path

        nbrs = neighbors(cur)
        j = 0
        while j < len(nbrs):
            nxt, d, c, idx = nbrs[j]
            ng = g + c
            prev = best_g.get(nxt, float("inf"))
            if ng < prev:
                best_g[nxt] = ng
                nf = ng + heuristic(nxt, goal)
                heapq.heappush(pq, (nf, idx, ng, nxt, path + [d]))
            j = j + 1

    log("A*: no safe route")
    return None

# ------------------------------------
# Survivor discovery
# ------------------------------------

def find_survivor():
    """
    Scan a large square area around current location to find
    a Survivor object in the map. Returns its Location or None.
    """
    me = get_location()
    dx = -80
    while dx <= 80:
        dy = -80
        while dy <= 80:
            loc = Location(me.x + dx, me.y + dy)
            if on_map(loc):
                info = get_cell_info_at(loc)
                if isinstance(info.top_layer, Survivor):
                    log("Survivor spotted at {}".format(loc))
                    return loc
            dy = dy + 1
        dx = dx + 1
    return None

# ------------------------------------
# THINK loop
# ------------------------------------

def think():
    """
    Main agent decision-making loop.
    Steps:
      - Round 1: move CENTER to reveal local costs (needed in V3).
      - If standing on survivor: call SAVE.
      - Else: find survivor (cache location), or wait if unseen.
      - Use A* to plan path toward survivor.
      - Validate next move (energy, killers, traps).
      - Move accordingly, or wait (CENTER) if unsafe.
    """
    global goal_cached

    if get_round_number() == 1:
        log("Round 1: CENTER to reveal local move costs (V3)")
        move(Direction.CENTER)
        return

    me = get_location()
    here = get_cell_info_at(me)

    if isinstance(here.top_layer, Survivor):
        log("On survivor tile -> SAVE")
        save()
        return

    if goal_cached is None:
        goal_cached = find_survivor()
        if goal_cached is None:
            log("Survivor not visible yet -> wait")
            move(Direction.CENTER)
            return

    energy = get_energy_level()
    log("Round {} | Energy={} | Me={} | Goal={}".format(get_round_number(), energy, me, goal_cached))

    path = astar(me, goal_cached)

    if path and len(path) > 0:
        d0 = path[0]
        nxt = Location(me.x + d0.dx, me.y + d0.dy)

        if not on_map(nxt):
            log("Abort {}: off-map to {}".format(d0, nxt))
            move(Direction.CENTER)
            return
        if d0.dx != 0 and d0.dy != 0 and diagonal_blocked(me, d0):
            log("Abort {}: diagonal corner blocked near {}".format(d0, me))
            move(Direction.CENTER)
            return
        if is_killer(nxt):
            log("Abort {}: killer at {}".format(d0, nxt))
            move(Direction.CENTER)
            return

        mc_dest = dest_move_cost(nxt)
        edge_tag_exec = edge_rubble_or_trap(me, d0)
        cell_tag_exec = cell_has_rubble_or_trap(nxt)
        c0 = edge_cost(me, d0)
        ninfo = get_cell_info_at(nxt)
        log("Next {} -> {} | edge_cost={} | dest_cell_cost={} | edge_tag={} | cell_tag={} | dest_info={}".format(
            d0, nxt, c0, mc_dest, edge_tag_exec, cell_tag_exec, str(ninfo)
        ))

        if mc_dest >= 500.0:
            log("Abort {}: TRAP CELL at {} (dest move_cost={})".format(d0, nxt, mc_dest))
            move(Direction.CENTER)
            return
        if edge_tag_exec == "trap":
            log("Abort {}: TRAP edge to {}".format(d0, nxt))
            move(Direction.CENTER)
            return
        if cell_tag_exec == "trap":
            log("Abort {}: TRAP (object) at {}".format(d0, nxt))
            move(Direction.CENTER)
            return

        if c0 is None:
            log("Abort {}: invalid/blocked cost".format(d0))
            move(Direction.CENTER)
            return
        if c0 > get_energy_level():
            log("Abort {}: need {}, have {}".format(d0, c0, get_energy_level()))
            move(Direction.CENTER)
            return

        log("MOVE {} -> {} (cost={})".format(d0, nxt, c0))
        move(d0)
        return

    log("No safe step; waiting")
    move(Direction.CENTER)

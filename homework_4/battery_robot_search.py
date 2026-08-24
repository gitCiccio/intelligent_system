"""
Robot with Limited Battery — Search Problem Formalization and Empirical Comparison
====================================================================================

State representations
----------------------
WEAK (inadequate):   s = (x, y)
    Only physical position. Violates the Markov property: whether future moves
    are legal (and whether the goal is truly reachable) depends on remaining
    battery, which this representation discards. Different physical situations
    (same cell, different battery levels) collapse into the same state.

ADEQUATE:            s = (x, y, battery)
    Position plus remaining autonomy. Minimal and Markovian: everything needed
    to determine legal successors and the goal test is contained in the state.

Problem formalization (adequate representation)
-------------------------------------------------
Initial state   : s0 = (x_start, y_start, k)      [robot starts with full battery]
Successor fn    : from (x, y, b), for each action in {N, S, E, W} leading to a
                   valid, non-obstacle cell (x', y'):
                     - if b == 0: no legal moves (robot stranded)
                     - else: b' = k if (x', y') is a recharge cell, else b' = b - 1
Goal test       : (x, y) == (x_goal, y_goal)   [independent of battery level]
Path cost       : uniform, 1 per action (number of steps)

Two scenarios are modeled to stress-test Iterative Deepening Search (IDS):
  A) No recharge cells  -> depth in the search tree is a faithful proxy for
     battery consumed. IDS behaves well (see report, Part 3).
  B) With a recharge cell -> depth stops corresponding to true remaining
     autonomy. A naive IDS that caps its depth limit at k fails to find a
     solution that actually requires more than k steps. IDS must decouple its
     iteration limit from k and rely on the (x, y, battery) state to remain
     correct (see report, Part 4).

This script implements BFS, UCS and IDS (both tree-search and graph-search
variants) and empirically compares node expansions across both scenarios.
"""

from dataclasses import dataclass
from typing import Tuple, List, Set, Optional
import heapq
from collections import deque
import csv


@dataclass(frozen=True)
class State:
    x: int
    y: int
    battery: int


class BatteryRobotProblem:
    """Search problem: Robot with Limited Battery (adequate state representation)."""

    ACTIONS = {'N': (0, -1), 'S': (0, 1), 'E': (1, 0), 'W': (-1, 0)}

    def __init__(self, grid_w: int, grid_h: int, obstacles: Set[Tuple[int, int]],
                 start: Tuple[int, int], goal: Tuple[int, int],
                 recharge_cells: Set[Tuple[int, int]], k: int):
        self.w = grid_w
        self.h = grid_h
        self.obstacles = obstacles
        self.start = start
        self.goal = goal
        self.recharge_cells = recharge_cells
        self.k = k

    def initial_state(self) -> State:
        return State(self.start[0], self.start[1], self.k)

    def is_goal(self, s: State) -> bool:
        return (s.x, s.y) == self.goal

    def _valid_cell(self, x: int, y: int) -> bool:
        return 0 <= x < self.w and 0 <= y < self.h and (x, y) not in self.obstacles

    def successors(self, s: State) -> List[Tuple[str, State, int]]:
        """Returns list of (action, next_state, step_cost)."""
        result = []
        if s.battery <= 0:
            return result
        for action, (dx, dy) in self.ACTIONS.items():
            nx, ny = s.x + dx, s.y + dy
            if not self._valid_cell(nx, ny):
                continue
            nb = self.k if (nx, ny) in self.recharge_cells else s.battery - 1
            result.append((action, State(nx, ny, nb), 1))
        return result


class Node:
    __slots__ = ['state', 'parent', 'action', 'path_cost', 'depth']

    def __init__(self, state, parent=None, action=None, path_cost=0, depth=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost
        self.depth = depth

    def path(self):
        node, p = self, []
        while node:
            p.append(node)
            node = node.parent
        return list(reversed(p))


def expand(problem, node):
    return [Node(ns, node, a, node.path_cost + c, node.depth + 1)
            for a, ns, c in problem.successors(node.state)]


def bfs_graph_search(problem):
    start = Node(problem.initial_state())
    if problem.is_goal(start.state):
        return start, 0
    frontier = deque([start])
    explored = {start.state}
    generated = 1
    while frontier:
        node = frontier.popleft()
        for child in expand(problem, node):
            generated += 1
            if child.state not in explored:
                if problem.is_goal(child.state):
                    return child, generated
                explored.add(child.state)
                frontier.append(child)
    return None, generated


def ucs_graph_search(problem):
    start = Node(problem.initial_state())
    frontier = [(start.path_cost, id(start), start)]
    best_cost = {start.state: 0}
    generated = 1
    while frontier:
        cost, _, node = heapq.heappop(frontier)
        if cost > best_cost.get(node.state, float('inf')):
            continue
        if problem.is_goal(node.state):
            return node, generated
        for child in expand(problem, node):
            generated += 1
            if child.path_cost < best_cost.get(child.state, float('inf')):
                best_cost[child.state] = child.path_cost
                heapq.heappush(frontier, (child.path_cost, id(child), child))
    return None, generated


def depth_limited_search_tree(problem, limit):
    """Plain DLS, tree search (no duplicate detection at all)."""
    generated = 0

    def recursive_dls(node, limit):
        nonlocal generated
        if problem.is_goal(node.state):
            return node, 'found'
        if limit == 0:
            return None, 'cutoff'
        cutoff_occurred = False
        for child in expand(problem, node):
            generated += 1
            result, status = recursive_dls(child, limit - 1)
            if status == 'cutoff':
                cutoff_occurred = True
            elif status != 'failure':
                return result, 'found'
        return (None, 'cutoff') if cutoff_occurred else (None, 'failure')

    start = Node(problem.initial_state())
    generated += 1
    result, _ = recursive_dls(start, limit)
    return result, generated


def ids_tree_search(problem, max_depth=200):
    """IDS using plain tree-search DLS (no state deduplication)."""
    total_generated = 0
    for depth in range(max_depth + 1):
        result, generated = depth_limited_search_tree(problem, depth)
        total_generated += generated
        if result is not None:
            return result, total_generated, depth
    return None, total_generated, None


def dls_graph_search(problem, limit):
    """Depth-limited search with a SHARED explored set (graph search)."""
    generated = 1
    start = Node(problem.initial_state())
    if problem.is_goal(start.state):
        return start, generated
    stack = [(start, 0)]
    best_depth = {start.state: 0}
    while stack:
        node, depth = stack.pop()
        if depth >= limit:
            continue
        for child in expand(problem, node):
            generated += 1
            if problem.is_goal(child.state):
                return child, generated
            if child.state not in best_depth or best_depth[child.state] > depth + 1:
                best_depth[child.state] = depth + 1
                stack.append((child, depth + 1))
    return None, generated


def ids_graph_search(problem, max_depth=200):
    """IDS using graph-search DLS at every iteration (shared explored set)."""
    total_generated = 0
    for depth in range(max_depth + 1):
        result, generated = dls_graph_search(problem, depth)
        total_generated += generated
        if result is not None:
            return result, total_generated, depth
    return None, total_generated, None


def print_path(node):
    if node is None:
        print("  NO SOLUTION FOUND")
        return
    for n in node.path():
        print(f"  {n.state}  action={n.action}")


def run_scenario_A():
    """Positive example: no recharge cells, k large enough. Depth == battery consumed."""
    obstacles = {(2, 1), (2, 2), (2, 3), (5, 4), (5, 5), (1, 5)}
    problem = BatteryRobotProblem(
        grid_w=7, grid_h=7, obstacles=obstacles,
        start=(0, 0), goal=(6, 6), recharge_cells=set(), k=14
    )
    bfs_node, bfs_gen = bfs_graph_search(problem)
    ucs_node, ucs_gen = ucs_graph_search(problem)
    ids_tree_node, ids_tree_gen, _ = ids_tree_search(problem, max_depth=20)
    ids_graph_node, ids_graph_gen, _ = ids_graph_search(problem, max_depth=20)

    return [
        ("Scenario A (no recharge, k=14)", "BFS (graph search)", bfs_node.path_cost, bfs_gen),
        ("Scenario A (no recharge, k=14)", "UCS (graph search)", ucs_node.path_cost, ucs_gen),
        ("Scenario A (no recharge, k=14)", "IDS - tree search (no dedup)", ids_tree_node.path_cost, ids_tree_gen),
        ("Scenario A (no recharge, k=14)", "IDS - graph search (shared explored set)", ids_graph_node.path_cost, ids_graph_gen),
    ]


def run_scenario_B():
    """Negative example: recharge cell present. Naive IDS caps depth at k and fails."""
    obstacles = {(2, 1), (2, 2), (2, 3), (2, 4), (4, 0), (4, 1), (4, 2)}
    recharge = {(3, 3)}
    problem = BatteryRobotProblem(
        grid_w=7, grid_h=7, obstacles=obstacles,
        start=(0, 0), goal=(6, 0), recharge_cells=recharge, k=6
    )
    bfs_node, bfs_gen = bfs_graph_search(problem)
    ucs_node, ucs_gen = ucs_graph_search(problem)

    # Naive IDS: iteration limit wrongly capped at k (treats depth as if it were true autonomy)
    ids_naive_node, ids_naive_gen, _ = ids_graph_search(problem, max_depth=problem.k)

    # Correct IDS: iteration limit decoupled from k, state includes battery
    ids_correct_node, ids_correct_gen, _ = ids_graph_search(problem, max_depth=20)

    return [
        ("Scenario B (recharge, k=6)", "BFS (graph search)", bfs_node.path_cost, bfs_gen),
        ("Scenario B (recharge, k=6)", "UCS (graph search)", ucs_node.path_cost, ucs_gen),
        ("Scenario B (recharge, k=6)", "IDS naive (depth capped at k)",
         "NO SOLUTION" if ids_naive_node is None else ids_naive_node.path_cost, ids_naive_gen),
        ("Scenario B (recharge, k=6)", "IDS correct (depth decoupled from k)",
         ids_correct_node.path_cost, ids_correct_gen),
    ], bfs_node


if __name__ == "__main__":
    print("=" * 70)
    print("SCENARIO A — No recharge cells (positive example for IDS)")
    print("=" * 70)
    rows_a = run_scenario_A()
    for r in rows_a:
        print(f"{r[1]:<45} cost={r[2]:<6} nodes_generated={r[3]}")

    print()
    print("=" * 70)
    print("SCENARIO B — With recharge cell (negative example for IDS)")
    print("=" * 70)
    rows_b, bfs_solution = run_scenario_B()
    for r in rows_b:
        print(f"{r[1]:<45} cost={r[2]:<6} nodes_generated={r[3]}")

    print("\nOptimal path found by BFS/UCS in Scenario B (passes through recharge cell):")
    print_path(bfs_solution)

    with open("battery_robot_search_comparison.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Scenario", "Algorithm", "Solution Cost (steps)", "Nodes Generated"])
        for row in rows_a + rows_b:
            writer.writerow(row)
    print("\nResults exported to battery_robot_search_comparison.csv")

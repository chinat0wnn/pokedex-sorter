"""
Each algorithm receives a list of dicts {"id": int, "name": str, "img": str}
and returns a list of step dicts consumed by the frontend animator.

Step types:
  {"type": "compare",   "indices": [i, j]}
  {"type": "swap",      "indices": [i, j]}
  {"type": "overwrite", "index":  i, "value": {...}}
  {"type": "pivot",     "index":  i}
  {"type": "sorted",    "index":  i}
"""

from typing import Any


def _item(arr: list, i: int) -> dict:
    return dict(arr[i])


# ─────────────────────────── Bubble Sort ───────────────────────────

def bubble_sort(arr: list[dict]) -> list[dict]:
    a = [dict(x) for x in arr]
    n = len(a)
    steps: list[dict] = []

    for i in range(n - 1):
        for j in range(n - i - 1):
            steps.append({"type": "compare", "indices": [j, j + 1]})
            if a[j]["id"] > a[j + 1]["id"]:
                steps.append({"type": "swap", "indices": [j, j + 1]})
                a[j], a[j + 1] = a[j + 1], a[j]
        steps.append({"type": "sorted", "index": n - i - 1})

    steps.append({"type": "sorted", "index": 0})
    return steps


# ─────────────────────────── Selection Sort ────────────────────────

def selection_sort(arr: list[dict]) -> list[dict]:
    a = [dict(x) for x in arr]
    n = len(a)
    steps: list[dict] = []

    for i in range(n - 1):
        min_idx = i
        for j in range(i + 1, n):
            steps.append({"type": "compare", "indices": [min_idx, j]})
            if a[j]["id"] < a[min_idx]["id"]:
                min_idx = j
        if min_idx != i:
            steps.append({"type": "swap", "indices": [i, min_idx]})
            a[i], a[min_idx] = a[min_idx], a[i]
        steps.append({"type": "sorted", "index": i})

    steps.append({"type": "sorted", "index": n - 1})
    return steps


# ─────────────────────────── Insertion Sort ────────────────────────

def insertion_sort(arr: list[dict]) -> list[dict]:
    a = [dict(x) for x in arr]
    n = len(a)
    steps: list[dict] = []

    steps.append({"type": "sorted", "index": 0})
    for i in range(1, n):
        j = i
        while j > 0:
            steps.append({"type": "compare", "indices": [j - 1, j]})
            if a[j]["id"] < a[j - 1]["id"]:
                steps.append({"type": "swap", "indices": [j - 1, j]})
                a[j], a[j - 1] = a[j - 1], a[j]
                j -= 1
            else:
                break
        steps.append({"type": "sorted", "index": i})

    return steps


# ─────────────────────────── Merge Sort ────────────────────────────

def merge_sort(arr: list[dict]) -> list[dict]:
    a = [dict(x) for x in arr]
    steps: list[dict] = []

    def _merge(array: list, l: int, r: int):
        if l >= r:
            return
        m = (l + r) // 2
        _merge(array, l, m)
        _merge(array, m + 1, r)

        left  = array[l : m + 1]
        right = array[m + 1 : r + 1]
        i = j = 0
        k = l

        while i < len(left) and j < len(right):
            steps.append({"type": "compare", "indices": [l + i, m + 1 + j]})
            if left[i]["id"] <= right[j]["id"]:
                steps.append({"type": "overwrite", "index": k, "value": dict(left[i])})
                array[k] = dict(left[i])
                i += 1
            else:
                steps.append({"type": "overwrite", "index": k, "value": dict(right[j])})
                array[k] = dict(right[j])
                j += 1
            k += 1

        while i < len(left):
            steps.append({"type": "overwrite", "index": k, "value": dict(left[i])})
            array[k] = dict(left[i])
            i += 1
            k += 1

        while j < len(right):
            steps.append({"type": "overwrite", "index": k, "value": dict(right[j])})
            array[k] = dict(right[j])
            j += 1
            k += 1

    _merge(a, 0, len(a) - 1)

    for idx in range(len(a)):
        steps.append({"type": "sorted", "index": idx})

    return steps


# ─────────────────────────── Quick Sort ────────────────────────────

def quick_sort(arr: list[dict]) -> list[dict]:
    a = [dict(x) for x in arr]
    steps: list[dict] = []

    def _partition(array: list, low: int, high: int) -> int:
        steps.append({"type": "pivot", "index": high})
        i = low - 1
        for j in range(low, high):
            steps.append({"type": "compare", "indices": [j, high]})
            if array[j]["id"] <= array[high]["id"]:
                i += 1
                if i != j:
                    steps.append({"type": "swap", "indices": [i, j]})
                    array[i], array[j] = array[j], array[i]
        i += 1
        if i != high:
            steps.append({"type": "swap", "indices": [i, high]})
            array[i], array[high] = array[high], array[i]
        steps.append({"type": "sorted", "index": i})
        return i

    def _quick(array: list, low: int, high: int):
        if low >= high:
            return
        pivot_idx = _partition(array, low, high)
        _quick(array, low, pivot_idx - 1)
        _quick(array, pivot_idx + 1, high)

    _quick(a, 0, len(a) - 1)
    if a:
        steps.append({"type": "sorted", "index": 0})

    return steps


# ─────────────────────────── Dispatcher ────────────────────────────

ALGORITHMS = {
    "bubble":    bubble_sort,
    "selection": selection_sort,
    "insertion": insertion_sort,
    "merge":     merge_sort,
    "quick":     quick_sort,
}

COMPLEXITIES = {
    "bubble":    {"name": "Bubble Sort",    "best": "O(n)",       "average": "O(n²)",      "worst": "O(n²)",      "space": "O(1)"},
    "selection": {"name": "Selection Sort", "best": "O(n²)",      "average": "O(n²)",      "worst": "O(n²)",      "space": "O(1)"},
    "insertion": {"name": "Insertion Sort", "best": "O(n)",       "average": "O(n²)",      "worst": "O(n²)",      "space": "O(1)"},
    "merge":     {"name": "Merge Sort",     "best": "O(n log n)", "average": "O(n log n)", "worst": "O(n log n)", "space": "O(n)"},
    "quick":     {"name": "Quick Sort",     "best": "O(n log n)", "average": "O(n log n)", "worst": "O(n²)",      "space": "O(log n)"},
}


def run_algorithm(name: str, arr: list[dict]) -> dict[str, Any]:
    if name not in ALGORITHMS:
        raise ValueError(f"Unknown algorithm: {name!r}. Valid: {list(ALGORITHMS)}")
    steps = ALGORITHMS[name](arr)
    compares = sum(1 for s in steps if s["type"] == "compare")
    swaps    = sum(1 for s in steps if s["type"] == "swap")
    writes   = sum(1 for s in steps if s["type"] == "overwrite")
    return {
        "algorithm":   name,
        "complexity":  COMPLEXITIES[name],
        "steps":       steps,
        "total_steps": len(steps),
        "stats": {
            "compares": compares,
            "swaps":    swaps,
            "writes":   writes,
            "total":    compares + swaps + writes,
            "n":        len(arr),
        },
    }

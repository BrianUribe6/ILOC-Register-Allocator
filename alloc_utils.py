from collections import Counter, defaultdict
from typing import Any, List


def isregister(string) -> bool:
    """Returns True if string is not an integer constant."""
    return string is not None and not string.isdigit()


def range_cmp(a, b):
    """compares register according to their count and live ranges. If two
    registers have the same count then the one with the larger live range is
    considered smaller and thefore chosen first by a sorting function.

    inputs: a list containing register name, count, range start, range end.
    """
    _, a_count, a_start, a_end = a
    _, b_count, b_start, b_end = b
    if a_count == b_count:
        a_len = a_end - a_start
        b_len = b_end - b_start
        return -1 if a_len > b_len else 1 if a_len < b_len else 0
    
    return a_count - b_count


def get_reg_count(instructions) -> Counter:
    """computes the number of occurrences for each register"""
    count = Counter()
    for inst in instructions:
        for i in range(1, len(inst)):
            if isregister(inst[i]): #skip integer constants
                count[inst[i]] += 1
    
    return count


def get_live_ranges(instructions):
    """Returns a mapping of each vr register to its live range"""
    live_ranges = {}
    for j, i in enumerate(instructions):
        for op in i[1:]:
            if isregister(op):
                if op not in live_ranges:
                    live_ranges[op] = [j, float('inf')]
                else:
                    live_ranges[op][1] = j
    
    for vr in live_ranges:
        #a virtual register is live on exit between its declaration
        #and its last usage (non inclusive)
        live_ranges[vr][1] -= 1
        live_ranges[vr] = tuple(live_ranges[vr])
    
    return live_ranges


def get_max_live(live_ranges):
    """Returns the maximum number of overlapping live ranges. It assumes
    ranges are already sorted by their start point.
    """
    max_live = float('-inf')
    curr_live = 0

    start, end = [], []
    for s, e in live_ranges:
        start.append(s)
        end.append(e)
    
    end.sort()
    i = j = 0
    while i < len(start) and j < len(end):
        if start[i] < end[j]:
            curr_live += 1
            i += 1
            max_live = max(curr_live, max_live)
        else:
            curr_live -= 1
            j += 1
    
    return max_live


def get_vr_usage(instructions):
    """returns a mapping of each virtual register to a list of occurrences.
    """
    usage = defaultdict(list)
    for i in reversed(range(len(instructions))):
        for reg in instructions[i][1:]:
            if isregister(reg):
                usage[reg].append(i)
    
    return usage
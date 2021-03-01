import platform
import subprocess
from typing import List
import unittest
import alloc
from collections import namedtuple
from alloc_utils import get_live_ranges, get_max_live, range_cmp
from functools import cmp_to_key


COMMAND = './sim -i 1024'
DIR = r'test_blocks'
Test = namedtuple("Test", ["block_name", "instruction", "cmd_input", "expected"])

num_registers = [5, 10, 15]
testcases = [
    ("1 1", ["22", "20", "56", "110"]),
    (""   , ["3", "4", "6", "11"]),
    ("1 1", ["12"]),
    ("1 1", ["12"]),
    ("0 1", ['0', '1', '1', '2', '3', '5', '8', '13', '21', '34', '55', '89']),
    ("3 5", ['3', '5', '8', '13', '21', '34', '55', '89', '144', '233', '377', '610']),
    (""   , ["-10"])
]

if platform.system() == "Windows":
    #make use of Windows Subsystem for Linux to execute ILOC simulator
    COMMAND = f"wsl {COMMAND}" 


def get_output(cmd_input, alloc_result):
    cmd = f"{COMMAND} {cmd_input}"
    input_txt = '\n'.join(str(i) for i in alloc_result).encode()
    result = subprocess.run(cmd, input=input_txt, capture_output=True)

    if result.returncode != 0:
        err_msg = ''.join(result.stderr.decode())
        raise ValueError(f"{cmd} failed with status code {result.returncode}."
                         f"{err_msg}\n")

    return result.stdout.decode().strip().split('\n')


def get_tests():
    for b, testcase in enumerate(testcases):
        input_txt, expected_output = testcase
        b_name = f'block{b}.i'
        test = Test(
            block_name=b_name,
            instruction=alloc.read_instructions(f"{DIR}/{b_name}"),
            cmd_input=input_txt,
            expected=expected_output
        )
        yield test


class TestUtils(unittest.TestCase):
    
    def test_get_live_range(self):
        """get_live_range should outputs a valid list of live ranges
        """
        instructions = alloc.read_instructions(f"{DIR}/block6.i")
        result = get_live_ranges(instructions)
        expected = {
            'r0': (0, 11),
            'r1': (1, 9),
            'r2': (2, 3),
            'r3': (3, 6),
            'r4': (4, 8),
            'r5': (5, 7),
            'r6': (6, 6),
            'r7': (7, 7),
            'r8': (8, 8),
            'r9': (9, 9),
            'r10': (10,10)
        }
        self.assertDictEqual(result, expected)


    def test_max_live(self):
        input_pairs = [
            (0, 11), (1, 9), (2, 3), (3, 6), (4, 8),(5, 7), (6, 6), 
            (7, 7), (8, 8), (9, 9), (10, 10)
        ]
        result = get_max_live(input_pairs)
        self.assertEqual(result, 5)
    

    def test_range_cmp_sorts_based_on_live_ranges(self):
        input_pairs = [
            (None, 4, 0, 11), (None, 4, 1, 9), (None, 2, 2, 3), 
            (None, 2, 3, 6), (None, 8, 4, 8)
        ]
        input_pairs.sort(key=cmp_to_key(range_cmp))
        expected = [
            (None, 2, 3, 6), (None, 2, 2, 3), (None, 4, 0, 11), 
            (None, 4, 1, 9), (None, 8, 4, 8)
        ]
        self.assertEqual(input_pairs, expected)


class AllocatorTest(unittest.TestCase):
  
    def test_simple_allocator(self):
        for t in get_tests():
            for k in num_registers:
                allocator = alloc.SimpleAlloc(t.instruction)
                result = allocator.allocate(k)
                out = get_output(t.cmd_input, result)[:-1]
                self.assertEqual(
                    t.expected, out,
                    f"{t.block_name} failed with k = {k}"
                ) 


    def test_top_down_allocator(self):
        for t in get_tests():
            for k in num_registers:
                allocator = alloc.TopDownAlloc(t.instruction)
                result = allocator.allocate(k)
                out = get_output(t.cmd_input, result)[:-1]
                self.assertEqual(
                    t.expected, out,
                    f"{t.block_name} failed with k = {k}"
                ) 

    
    def test_bottom_up_allocator(self):        
        for t in get_tests():
            for k in num_registers:
                allocator = alloc.BottomUpAlloc(t.instruction)
                result = allocator.allocate(k)
                out = get_output(t.cmd_input, result)[:-1]
                self.assertEqual(
                    t.expected, out,
                    f"{t.block_name} failed with k = {k}"
                ) 


    def test_custom_allocator(self):
        for t in get_tests():
            for k in num_registers:
                allocator = alloc.LinearScanAlloc(t.instruction)
                result = allocator.allocate(k)
                out = get_output(t.cmd_input, result)[:-1]
                self.assertEqual(
                    t.expected, out,
                    f"{t.block_name} failed with k = {k}"
                )

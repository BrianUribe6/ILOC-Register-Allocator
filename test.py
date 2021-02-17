import platform
import subprocess
from typing import List
import unittest
import alloc
from collections import namedtuple


COMMAND = './sim -i 1024'
DIR = r'test_blocks'
NUM_BLOCKS = 6
Test = namedtuple("Test", ["block_name", "instruction", "cmd_input", "expected"])

num_registers = [5, 10, 15]
testcases = [
    ("1 1", ["22", "20", "56", "110"]),
    (""   , ["3", "4", "6", "11"]),
    ("1 1", ["12"]),
    ("1 1", ["12"]),
    ("0 1", ['0', '1', '1', '2', '3', '5', '8', '13', '21', '34', '55', '89']),
    ("3 5", ['3', '5', '8', '13', '21', '34', '55', '89', '144', '233', '377', '610'])
]

if platform.system() == "Windows":
    #make use of Windows Subsystem for Linux to execute ILOC simulator
    COMMAND = f"wsl {COMMAND}" 

def instr_to_bytes(instructions: List[alloc.Instruction]):
    """converts instruction List into a byte string suitable for the terminal
    """
    return '\n'.join(str(i) for i in instructions).encode()


def get_output(cmd_input, alloc_result):
    cmd = f"{COMMAND} {cmd_input}"
    input_txt = instr_to_bytes(alloc_result)
    result = subprocess.run(cmd, input=input_txt, capture_output=True)

    if result.returncode != 0:
        raise ValueError(f"{cmd} failed with status code {result.returncode}.")

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


class SimpleAllocatorTest(unittest.TestCase):
  
    def test_simple_allocator(self):
        for t in get_tests():
            for k in num_registers:
                result = alloc.simple_allocator(t.instruction, k)
                out = get_output(t.cmd_input, result)[:-1]
                self.assertEqual(
                    t.expected, out,
                    f"{t.block_name} failed with k = {k}"
                ) 


    def test_top_down_allocator(self):
        self.skipTest("Not implemented")

    
    def test_bottom_up_allocator(self):
        for t in get_tests():
            for k in num_registers:
                allocator = alloc.BottomUpAlloc(t.instruction, k)
                result = allocator.allocate()
                out = get_output(t.cmd_input, result)[:-1]
                self.assertEqual(
                    t.expected, out,
                    f"{t.block_name} failed with k = {k}"
                ) 


    def test_custom_allocator(self):
        self.skipTest("Not implemented")

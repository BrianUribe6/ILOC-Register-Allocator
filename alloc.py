import argparse
import re
from collections import Counter, defaultdict
from typing import List, NamedTuple


NUM_FEASIBLE = 2

class Instruction(NamedTuple):
    opcode: str     # instruction name
    op1: str        # first operand: virtual register or integer constant
    op2: str = None # second operand: virtual register/None/integer constant
    dst: str = None # destination register

    def get_operands(self):
        return (self.op1, self.op2)


    def __str__(self) -> str:
        if self.opcode == 'storeAI':
            return f'{self.opcode}\t{self.op1}\t=> {self.op2}, {self.dst}'
        
        if self.opcode == 'store':
            return f'{self.opcode}\t{self.op1}\t=> {self.op2}'

        if self.opcode == 'output':
            return f'{self.opcode}\t{self.op1}'

        if self.opcode == 'outputAI':
            return f'{self.opcode} {self.op1}, {self.dst}'

        if self.op2 is None: #regular 2 argument instruction
            return f'{self.opcode}\t{self.op1}\t=> {self.dst}'
        #regular 3 argument instructions
        return f'{self.opcode}\t{self.op1}, {self.op2}\t=> {self.dst}'


class BottomUpAlloc:

    def __init__(self, instructions, num_regs) -> None:
        if num_regs < 2:
            raise ValueError("Number of registers must be 2 or greater.")

        self.instructions = instructions
        self.regs = [self.Register(f"r{j}") for j in range(1, num_regs + 1)]
        self.offset = -4
        self.available = [r for r in self.regs]
        self.base_ptr = self.Register('r0')
        self.location = {'r0': self.base_ptr} #set r0 aside from allocation
        self.spilled = {}
        self.result = []
    

    def _get_vr_usage(self):
        """returns a mapping of each virtual register to a list of occurrences.
        """
        usage = defaultdict(list)
        for i in reversed(range(len(self.instructions))):
            for reg in self.instructions[i][1:]:
                if isregister(reg):
                    usage[reg].append(i)

        return usage


    def _alloc(self, vr):
        """Attempts to map a virtual register a free physical register.
        If not possible it spills the register that isn't needed for the longest
        time.
        """
        reg = None
        if vr == self.base_ptr.phy_name: # avoid reassigning r0
            return self.base_ptr
            
        if len(self.available) > 0:
            reg = self.available.pop()
        else:
            #find the register that we won't need for the longest time
            reg = max(self.regs, key= lambda x: x.next)
            self._spill(reg)
        
        self.location[vr] = reg
        reg.vr_name = vr
        # reg.next = -1 #avoids reusing this register for the next operand

        return reg


    def _ensure(self, vr):
        """ Makes sure vr is mapped to valid physical register. If vr has been
        spilled before. The appropiate load instructions is added to result,
        and a physical is made available to hold vr. Otherwise a new physical
        register is mapped.
        """
        reg = None        

        if vr in self.location and vr not in self.spilled:
            reg = self.location[vr]
        
        elif vr in self.spilled:
            pos = self.spilled[vr]
            reg = self._alloc(vr)
            self.result.append(
                Instruction("loadAI", self.base_ptr.phy_name, pos, reg.phy_name)
            )
            del self.spilled[vr]
        else:
            reg = self._alloc(vr)
        
        return reg    

    
    def _spill(self, reg):
        """Restore register to default values and generate store instruction"""
        vr = reg.vr_name
        self.spilled[vr] = self.offset
        self.result.append(
            Instruction("storeAI", reg.phy_name, self.base_ptr.phy_name, self.offset)
        )
        reg.vr_name = None
        reg.next = float('inf')
        self.offset -= 4
    

    def _free(self, reg):
        if reg == self.base_ptr:
            return
        if reg.vr_name:
            del self.location[reg.vr_name]
        reg.vr_name = None
        reg.next = float('inf')
        self.available.append(reg)


    def allocate(self):
        """Returns resulting list of instructions after performing register
        reallocation and assignment.
        """                    
        next_use = self._get_vr_usage()
        for i in self.instructions:
            new_instr = [i.opcode]
            # ensure both operands are in physical registers 
            for vr in i.get_operands():
                name = vr
                if isregister(vr):
                    reg = self._ensure(vr)
                    name = reg.phy_name
                new_instr.append(name)
            # check if we can reuse any operand as destination
            for vr in i.get_operands():
                if isregister(vr):
                    reg = self.location[vr]
                    if not next_use[vr]:
                        self._free(reg)
                    else: # we couldn't reuse so update its next usage
                        reg.next = next_use[vr].pop() 
            
            dst = vr = i.dst
            if isregister(vr):
                reg = self._alloc(vr)
                dst = reg.phy_name
                try:
                    next_use[vr].pop() # discard current use 
                    reg.next = next_use[vr].pop()
                except:
                    self._free(reg)
                    
            self.result.append(Instruction(*new_instr, dst))
        
        return self.result


    class Register:
        """Physical register representation.

        phy_name: physical name
        vr_name: name of the virtual register it is representing
        next: index of the next usage of its virtual register.
        """  
        def __init__(self, phy_name, vr_name=None, next=float('inf')):
            self.phy_name = phy_name
            self.vr_name = vr_name
            self.next = next


        def __repr__(self) -> str:
            return f"Register{self.phy_name, self.vr_name, self.next}"




def isregister(string) -> bool:
    """Returns True if string is not an integer constant."""
    return string is not None and not string.isdigit()


def write_instructions(instructions):
    for instruction in instructions:
        print(instruction)


def count_reg(instructions) -> Counter:
    """computes the number of occurrences for each register"""
    count = Counter()
    for inst in instructions:
        for i in range(1, len(inst)):
            if isregister(inst[i]): #skip integer constants
                count[inst[i]] += 1
    
    return count


def spill(instr, var_name, offset, used):
    """Inserts instructions to place/load a virtual register into an available
    space in memory.
    """
    i = 0
    for used_reg in used:
        if not used_reg: break
        i += 1
    
    i %= len(used)     # if all feasibles register are used then reuse r1.
    used[i] = True
    feasible_reg = f'r{i + 1}'
    spill_code = None
    if var_name == 'dst':
        instr = instr._replace(dst=feasible_reg)
        spill_code = Instruction('storeAI', feasible_reg, 'r0', offset)
    else:
        # we need to spill a source register.
        new_value = {var_name: feasible_reg}
        spill_code = Instruction('loadAI', 'r0', offset, feasible_reg)
        instr = instr._replace(**new_value)

    return instr, spill_code


def simple_allocator(instructions, num_registers):
    """
    """
    if num_registers < NUM_FEASIBLE:
        raise ValueError(f"number of register must be at least {NUM_FEASIBLE}.")

    result = []
    count = count_reg(instructions)
    total_vars = len(count) - ('r0' in count)
    allocd, memory = {'r0': 'r0'}, {}
    cur_offset = -4
    # registers 1 to NUM_FEASIBLE are reserved. We will assign as many 
    # physical registers as we can for the remaining k.
    j = NUM_FEASIBLE + 1 if total_vars > num_registers else 1
    for p in count.most_common():
        reg, _ = p
        if reg == 'r0': continue
        if j <= num_registers:
            allocd[reg] = f'r{j}'
            j += 1
        else:
            memory[reg] = cur_offset
            cur_offset -= 4
    # Rewrite instructions inserting spill code where needed. While keeping track 
    # of which fesible registers are available to avoid reusing a register
    # that is already an operand.
    used = [False] * NUM_FEASIBLE   
    for instr in instructions:
        #check which of the registers needs to be spilled
        inst_params = instr._asdict()
        spill_code = {'storeAI':[], 'loadAI': []}
        for i, var_name in enumerate(inst_params):
            if i == 0: #skip instruction name
                continue
            reg = inst_params[var_name]
            if reg in memory: #generate corresponding spill code
                instr, spill_instr = spill(instr, var_name, memory[reg], used)
                spill_code[spill_instr.opcode].append(spill_instr)
            elif reg in allocd: # just assign a physical register 
                assign = {var_name : allocd[reg]}
                instr = instr._replace(**assign)
        
        result += spill_code['loadAI'] + [instr] + spill_code['storeAI']
        used[0] = used[1] = False
        

    return result
        

def top_down_allocator(instructions, k):
    pass


def get_vr_usage(instructions):
    """returns a mapping of each virtual register to a list of occurrences.
    """
    usage = defaultdict(list)
    for i in reversed(range(len(instructions))):
        for reg in instructions[i][1:]:
            if isregister(reg):
                usage[reg].append(i)
    
    return usage

               
def custom_allocator(instructions, k):
    pass


def read_instructions(filename) -> List[Instruction]:
    """read instructions from an ILOC file.
    """
    instructions = []
    match_words = re.compile("\w+")
    match_comments = re.compile("\/\/.*")
    with open(filename, 'r') as code:
        for line in code:
            line = match_comments.sub("", line) #eliminate inline comments
            line = match_words.findall(line)
            if line:
                num_args = len(line) - 1
                if num_args > 3:
                    raise ValueError(f"{line} is an invalid ILOC instruction.")

                if num_args == 2 and line[0] != 'store':
                    # exclude store since it's last parameter
                    # works as an operand and not a destination
                    instructions.append(
                        Instruction(line[0], line[1], dst=line[2])
                    )
                else: #3 and 1 parameter instructions
                    instructions.append(Instruction(*line))


    return instructions
            

def main():
    parser = argparse.ArgumentParser(
        description='ILOC register allocator',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "registers", type=int,
        help='number of registers for the target machine'
    )
    parser.add_argument(
        'algorithm', type=str, choices=['b', 's', 't', 'o'],
        help='algorithm used to allocated registers\n'
            'b: bottom-up approach\n'
            's: simple top-down (no live ranges)\n'
            't: top-down with live ranges and max live\n'
            'o: custom allocator'
    )
    parser.add_argument(
        'filename', type=str,
        help='name of the file containing the ILOC program'
    )
    args = parser.parse_args()
    instructions = read_instructions(args.filename)

    result = None
    if args.algorithm == 's':
        result = simple_allocator(instructions, args.registers)
    elif args.algorithm == 't':
        result = top_down_allocator(instructions, args.registers)
    elif args.algorithm == 'b':
        allocator = BottomUpAlloc(instructions, args.registers)
        result = allocator.allocate()
    else:
        result = custom_allocator(instructions, args.registers)

    write_instructions(result)


if __name__ == '__main__':
    main()

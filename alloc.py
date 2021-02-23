import argparse
import re
from collections import Counter, defaultdict
from typing import List, NamedTuple
from functools import cmp_to_key
from alloc_utils import *


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


class SimpleAlloc:
    def __init__(self, instructions) -> None:
        self.instructions = instructions
        self.count = get_reg_count(instructions)
        self.used = [False] * NUM_FEASIBLE
        self.bp = 'r0'  # base pointer
    

    def spill(self, instr, param, offset):
        """Inserts instructions to store/load a virtual register into an available
        space in memory.
        """
        i = 0
        for used_reg in self.used:
            if not used_reg: break
            i += 1
        
        i %= len(self.used)  # if all feasibles register are used then reuse r1.
        self.used[i] = True
        feasible_reg = f'r{i + 1}'
        vr = instr[param]
        self.loc[vr] = instr[param] = feasible_reg
        
        store = None
        if param == 'dst':
            # save this value to memory AFTER executing previous instruction
            store = Instruction('storeAI', feasible_reg, self.bp, offset)
        else:
            # load value from memory into source register
            self.result.append(
                Instruction('loadAI', self.bp, offset, feasible_reg)
            )

        return store
    

    def assign(self, k) -> tuple:
        """Assigns the most used k - F virtual registers to physical registers.
        The remaining ones are assigned to a memory location. 
        F physical registers are reserved handle spill. Where F is the number of
        feasible registers.
        """
        allocd, memory = {'r0': self.bp}, {}
        offset = -4
        total_vars = len(self.count) - (self.bp in self.count)
        j = NUM_FEASIBLE + 1 if total_vars > k else 1
        for p in self.count.most_common():
            reg, _ = p
            if reg == self.bp: continue
            if j <= k:
                allocd[reg] = f'r{j}'
                j += 1
            else:
                memory[reg] = offset
                offset -= 4
        
        return allocd, memory


    def allocate(self, num_registers):
        if num_registers < NUM_FEASIBLE:
            raise ValueError(f"number of register must be at least {NUM_FEASIBLE}.")

        self.result = []
        allocd, memory = self.assign(num_registers)
        self.loc = {}  # keeps track of vr assigned to feasible registers

        for instr in self.instructions:
            new_inst = instr._asdict()
            store_inst = None
            #check which of the registers needs to be spilled
            for i, param in enumerate(new_inst):
                if i == 0: #skip instruction name
                    continue
                reg = new_inst[param]

                if reg in self.loc: # reuse the same feasible register
                    new_inst[param] = self.loc[reg]
                else:
                    if reg in memory:
                        #generate spill code
                        pos = memory[reg]
                        store_inst = self.spill(new_inst, param, pos)
                    elif reg in allocd:
                        # just assign a physical register  
                        new_inst[param] = allocd[reg]
            
            self.result.append(Instruction(**new_inst))
            if store_inst:
                self.result.append(store_inst)
            
            self.loc.clear()
            self.used[0] = self.used[1] = False
            

        return self.result


class TopDownAlloc:
    
    def __init__(self, instructions) -> None:
        self.instructions = instructions
        self.count = get_reg_count(instructions)
        self.live_ranges = get_live_ranges(instructions)
        self.r1_free = True
        self.feasible = [f'r{j}' for j in range(1, NUM_FEASIBLE + 1)]


    def _alloc(self, vr):
        if len(self.free) > 0:
            reg = self.free.pop()
            self.loc[vr] = reg
            return reg
        
        if vr not in self.mem:
            #create a new entry in memory for this value
            self.mem[vr] = self.pos
            self.pos -= 4
        
        reg = 'r1' if self.r1_free else 'r2'
        self.r1_free = not self.r1_free
        return reg
        

    def _ensure(self, vr):
        if vr in self.loc:
            reg = self.loc[vr]
        
        elif vr in self.mem:
            pos = self.mem[vr]
            reg = 'r1' if self.r1_free else 'r2'
            self.r1_free = not self.r1_free 
            self.result.append(Instruction("loadAI", 'r0', pos, reg))
        else:
            reg = self._alloc()
        
        return reg
    

    def get_reg(self, inst, curr_pos):
        regs = []
        src_regs = []
        for vr in inst.get_operands():
            if not isregister(vr) or vr == 'r0':
                regs.append(vr)
            else:
                reg = self._ensure(vr)
                regs.append(reg)
                src_regs.append(vr)

        for vr in src_regs:
            _, live_end = self.live_ranges[vr]
            if curr_pos > live_end and vr in self.loc:
                reg = self.loc[vr]
                # we do not need this register anymore
                self.free.append(reg)
                del self.loc[vr]
        
        reg = vr = inst.dst
        if vr != 'r0' and isregister(vr): #disregard r0 for allocation
            # use r1 as destination  if vr was spilled 
            reg = self.feasible[0] if vr in self.mem else self._alloc(vr)
        
        spill = None
        if reg in self.feasible:
            pos = self.mem[vr]
            spill = Instruction("storeAI", reg, 'r0', pos)
        
        regs.append(reg)

        return regs, spill


    def allocate(self, k):
        self.mem = {}
        self.loc = {}
        
        self.free = [f'r{j}' for j in range(NUM_FEASIBLE + 1, k + 1)]
        reg_count = self.count.items()
        live_ranges = self.live_ranges.values()
        max_live = get_max_live(live_ranges)       
        tmp = [[*reg, *lr] for reg, lr in zip(reg_count, live_ranges)]

        self.pos = -4
        for e in sorted(tmp, key=cmp_to_key(range_cmp)):
            if max_live <= k - NUM_FEASIBLE:
                break
            vr = e[0]
            self.mem[vr] = self.pos
            self.pos -= 4
            max_live -= 1
        
        self.result = []
        for j, inst in enumerate(self.instructions):
            regs, spill = self.get_reg(inst, j)
            self.result.append(Instruction(inst.opcode, *regs))

            if spill is not None:
                self.result.append(spill)
        
        return self.result


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
        allocator = SimpleAlloc(instructions)
        result = allocator.allocate(args.registers)
    elif args.algorithm == 't':
        allocator = TopDownAlloc(instructions)
        result = allocator.allocate(args.registers)
    elif args.algorithm == 'b':
        allocator = BottomUpAlloc(instructions, args.registers)
        result = allocator.allocate()
    else:
        result = custom_allocator(instructions, args.registers)

    for i in result:
        print(i)


if __name__ == '__main__':
    main()

# Local Register Allocator

Local register allocator for the ILOC intermediate representation described in "Engineering a Compiler-Elsevier Science & Technology (2011)" by Keith Cooper & Linda Torczon. The following strategies are implemented: 
 - Simple top-down
 - Live range based top down allocator
 - bottom-up allocator
 - Linear scan

For a more in-depth explanation of each algorithm, please check out my [paper](./RegisterAllocation.pdf), where I explain the implementation details as well as the pros and cons of each algorithm.
## Usage
    usage: alloc.py [-h] registers {s,t,b,o} filename

	Brian Uribe - ILOC register allocator

	positional arguments:
	  registers   number of registers for the target machine  
	  {s,t,b,o}   algorithm used to allocated registers       
	              b: bottom-up approach
	              s: simple top-down (no live ranges)
	              t: top-down with live ranges and max live   
	              o: custom allocator
	  filename    path of the file containing the ILOC program

	optional arguments:
	  -h, --help  show this help message and exit   

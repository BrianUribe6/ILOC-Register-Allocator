// CS 415 Project #1 - block3.i
//
// Reads in initial values from memory locations 1024 and 1028
//
// Example usage: sim -i 1024 1 1 < block3.i

loadI	1024	=> r0
loadI	1024	=> r8
loadI	1028	=> r9
load	r8	=> r10
load	r9	=> r11 
loadI	1032	=> r12
loadI	1036	=> r13
loadI	1040	=> r14
loadI	1044	=> r15
store	r10	=> r12
add	r10, r11	=> r16
store	r16	=> r13
add	r16, r11	=> r17
store	r17	=> r14
store	r11	=> r15
load	r12	=> r1
lshift	r1, r11	=> r18
load	r13	=> r2
mult	r18, r2	=> r19
load	r14	=> r20
mult	r19, r20	=> r21
load	r15	=> r22
mult	r21, r22	=> r23
store	r23	=> r12
output	1032

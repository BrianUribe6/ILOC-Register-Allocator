// CS 415 Project #1 - block3.i
//
// Reads in initial values from memory locations 1024 and 1028
//
// Example usage: sim -i 1024 1 1 < block3.i

loadI	1024	=> r0
loadI	1024	=> r8
loadI	1028	=> r9
load	r8	=> r10
// storeAI r10	=> r0, 8
// outputAI	r0, 8
load	r9	=> r11
// storeAI r11	=> r0, 8
// outputAI	r0, 8  
loadI	1032	=> r12
loadI	1036	=> r13
loadI	1040	=> r14
loadI	1044	=> r15
store	r10	=> r12
add	r10, r11	=> r16
// storeAI r16	=> r0, 8
// outputAI	r0, 8  
store	r16	=> r13
add	r16, r11	=> r17
// storeAI r17	=> r0, 16
// outputAI	r0, 16  
store	r17	=> r14
store	r11	=> r15
load	r12	=> r1
// storeAI r1 => r0, 22
// outputAI    r0, 22
lshift	r1, r11	=> r18
// storeAI r18	=> r0, 22
// outputAI	r0, 22 
load	r13	=> r2
mult	r18, r2	=> r19
// storeAI r19	=> r0, 16
// outputAI	r0, 16 
load	r14	=> r20
// storeAI r14	=> r0, 16
// outputAI	r0, 16 
mult	r19, r20	=> r21
// storeAI r21	=> r0, 16
// outputAI	r0, 16 
load	r15	=> r22
mult	r21, r22	=> r23
// storeAI r22 => r0, 22
// outputAI    r0, 22
store	r23	=> r12
output	1032

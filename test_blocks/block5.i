// CS 415 Project #1 - block6.i
//
// Fibonnaci numbers, using more registers (15)
// Takes as input the first two numbers in the series at memory
// locations 1024 and 1028.  These would usually be 0 and 1.
//
// Example usage: sim -i 1024 0 1 < block6.i
//                sim -i 1024 3 5 < block6.i

	loadI	1024	=> r0
	loadI	4	=> r1
	loadI	1024	=> r2
	load	r2	=> r3
	loadI	1028	=> r4
	load	r4	=> r5
	loadI	2000	=> r14
// f0
	store	r3	=> r14
// f1
	add	r3, r5	=> r15
	add	r14, r1	=> r16
	store	r5	=> r16
// f2
	add	r15, r5	=> r17
	add	r16, r1	=> r18
	store	r15	=> r18
// f3
	add	r17, r15	=> r6
	add	r18, r1	=> r19
	store	r17	=> r19
// f4
	add	r6, r17	=> r7
	add	r19, r1	=> r20
	store	r6	=> r20
// f51
	add	r7, r6	=> r8
	add	r20, r1	=> r21
	store	r7	=> r21
// f6
	add	r8, r7	=> r9
	add	r21, r1	=> r22
	store	r8	=> r22
// f7
	add	r9, r8	=> r10
	add	r22, r1	=> r23
	store	r9	=> r23
// f8
	add	r10, r9	=> r11
	add	r23, r1	=> r24
	store	r10	=> r24
// f9
	add	r11, r10	=> r12
	add	r24, r1	=> r25
	store	r11	=> r25
// f10
	add	r12, r11	=> r13
	add	r25, r1	=> r26
	store	r12	=> r26
// f11
	add	r26, r1	=> r27
	store	r13	=> r27

	output	2000
	output	2004
	output	2008
	output	2012
	output	2016
	output	2020
	output	2024
	output	2028
	output	2032
	output	2036
	output	2040
	output	2044
// end of block

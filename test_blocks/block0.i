// CS 415 Project #1 - block1.i
// 
// Just a long random computation
// Expects two inputs at locations 1024 and 1028 -
// the first is the initial value used in the computation and 
// the second is the incrementor.
//
// Example usage: sim -i 1024 1 1 < block1.i

	loadI	1024	=> r0
	loadI	1032	=> r1
	loadI	1024	=> r10
	load	r10	=> r11
	loadI	4	=> r12
	loadI	1028	=> r13
	load	r13	=> r14

	store	r11	=> r1
	add	r1, r12	=> r15
	add	r11, r14	=> r16
	store	r16	=> r15

	add	r15, r12	=> r17
	add	r16, r14	=> r18
	store	r18	=> r17

	add	r17, r12	=> r19
	add	r18, r14	=> r20
	store	r20	=> r19

	add	r19, r12	=> r21
	add	r20, r14	=> r22
	store	r22	=> r21

	add	r21, r12	=> r23
	add	r22, r14	=> r24
	store	r24	=> r23

	add	r23, r12	=> r25
	add	r24, r14	=> r26
	store	r26	=> r25

	add	r25, r12	=> r27
	add	r26, r14	=> r28
	store	r28	=> r27

	add	r27, r12	=> r29
	add	r28, r14	=> r30
	store	r30	=> r29

	add	r29, r12	=> r31
	add	r30, r14	=> r32
	store	r32	=> r31

	add	r31, r12	=> r33
	add	r32, r14	=> r34
	store	r34	=> r33

	load	r33	=> r2
	loadI	1036	=> r3
	load	r3	=> r4
	mult	r2, r4	=> r5
	loadI	1040	=> r6
	store	r5	=> r6
	loadI	1044	=> r35
	load	r35	=> r36
	loadI	1048	=> r37
	load	r37	=> r38
	mult	r36, r38	=> r39
	loadI	1052	=> r40
	store	r39	=> r40
	loadI	1056	=> r41
	load	r41	=> r42
	loadI	1060	=> r43
	load	r43	=> r44
	mult	r42, r44	=> r45
	loadI	1064	=> r46
	store	r45	=> r46
	loadI	1068	=> r47
	load	r47	=> r48
	loadI	1072	=> r49
	load	r49	=> r50
	mult	r48, r50	=> r51
	loadI	1076	=> r52
	store	r51	=> r52
	output	1040
	output	1052
	output	1064
	output	1076


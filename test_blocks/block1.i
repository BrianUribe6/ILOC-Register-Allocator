// CS 415 Project #1 - block2.i
//
// a simplified linear algebra kernel
//
// Example usage: sim < block2.i

	loadI	1024	=> r0
	loadI	2	=> r50
	loadI	1024	=> r49
	store	r50	=> r49
	loadI	3	=> r51
	loadI	1028	=> r52
	store	r51	=> r52
	loadI	5	=> r53
	loadI	1032	=> r54
	store	r53	=> r54
	loadI	2048	=> r55
	store	r53	=> r55
	loadI	6	=> r56
	loadI	4104	=> r57
	store	r56	=> r57
	loadI	1	=> r58
	loadI	8192	=> r59
	store	r58	=> r59

	loadI	2	=> r1
	loadI	1024	=> r2
	load	r2	=> r3
	sub	r3, r1	=> r4
	loadI	4	=> r5
	mult	r4, r5	=> r6
	loadI	2048	=> r7
	add	r6, r7	=> r8
	load	r8	=> r9

	loadI	1	=> r10
	loadI	1028	=> r11
	load	r11	=> r12
	sub	r12, r10	=> r13
	mult	r13, r5	=> r14
	loadI	4096	=> r15
	add	r14, r15	=> r16
	load	r16	=> r17

	loadI	8192	=> r18
	load	r18	=> r19

	mult	r19, r9	=> r20
	add	r17, r20	=> r21

	loadI	3	=> r22
	loadI	1032	=> r23
	load	r23	=> r24
	sub	r24, r22	=> r25
	mult	r25, r5	=> r26
	loadI	16384	=> r27
	add	r26, r27	=> r28
	store	r21	=> r28

	loadI	1	=> r29
	add	r3, r29	=> r60
	store	r60	=> r2
	add	r12, r29	=> r61
	store	r61	=> r11
	add	r24, r29	=> r62
	store	r62	=> r23

	output	1024
	output	1028
	output	1032
	output	16392
// end of block 2

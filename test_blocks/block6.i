loadI   1024   => r0
loadI   1      => r1 	
loadI   2      => r2 	
addI    r2, 3  => r3 	
sub     r2, r1 => r4 	
addI    r4, 3  => r5 	
mult    r3, r5 => r6 	
sub     r3, r6 => r7 	
add     r5, r7 => r8 	
mult    r4, r8 => r9 	
add     r1, r9 => r10	
store   r10    => r0
outputAI r0, 0

// live_range = {
//     r1: (2, 10)
//     r2: (3, 4)
//     r3: (4, 7)
//     r4: (5, 9)
//     r5: (6, 8)
//     r6: (7, 7)
//     r7: (8, 8)
//     r8: (9, 9)
//     r9: (10, 10)
//     r10:(11, 11)
// }

// map = {
//     r1: r4
//     r2: r3
//     r3: r2
//     r4: r3
//     r5: r1
//     r6: r4 // we are using are r4 for a new register so it is safe to delete r1 
// }

// loc = {
//     r1: -4
// }

// register = []
// active = [(4, 7) (6, 8) (5, 9)]


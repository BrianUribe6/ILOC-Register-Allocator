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

// Initialize SUM to 0
@R0
D=A

@SUM
M=D

@FACTOR
M=D

@R1
D=M

@TIMES // Stores the value of times to loop
M=D

@LOOP
D; JGT // If D (TIMES) is greater than 0, go to loop section

(STOP) // This section sets R2 to the value of SUM and jumps unconditionally to END section
    @SUM
    D=M

    @R2
    M=D

    @R2
    D=M

    @END
    0; JMP

(END) // This section outputs Data Reg value R2 and will be in a loop
    @R2
    D=M

    @END
    D; JMP

(LOOP)
    @FACTOR
    D=M

    @SUM
    M=D+M

    @TIMES
    M=M-1
    D=M

    @STOP
    D; JEQ


    

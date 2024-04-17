// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.

@8192
D=A
@end
M=D

(KBD_LISTEN)
    @R0
    D=A
    @start
    M=D

    @KBD
    D=M

    @BLACK
    D; JGT

    @WHITE
    0; JMP

(BLACK)
    @start
    D=M

    @end
    D=D-M
    
    @KBD_LISTEN
    D; JEQ

    @start
    D=M

    @SCREEN
    A=A+D
    M=-1

    @start
    M=M+1

    @BLACK
    0; JMP

(WHITE)
    @start
    D=M

    @end
    D=D-M
    
    @KBD_LISTEN
    D; JEQ

    @start
    D=M

    @SCREEN
    A=A+D
    M=0

    @start
    M=M+1

    @WHITE
    0; JMP

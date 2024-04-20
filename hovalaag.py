from tt import TT
import time
import random

tt = TT()

def clock_byte(val):
    return tt.clock_byte(val, 9)

def clock_byte_in(val):
    tt.clock_byte_in(val, 9)

def reset():
    clock_byte(4)
    clock_byte(4)

def run_instr(instr, in1, in2):
    if False:
        a      = clock_byte(((instr & 0x0000003F) <<  2) | 2)
        b      = clock_byte(((instr & 0x00000FC0) >>  4) | 2)
        c      = clock_byte(((instr & 0x0003F000) >> 10) | 2)
        d      = clock_byte(((instr & 0x00FC0000) >> 16) | 2)
    else:
        data = [((instr & 0x0000003F) <<  2) | 2,
                ((instr & 0x00000FC0) >>  4) | 2,
                ((instr & 0x0003F000) >> 10) | 2,
                ((instr & 0x00FC0000) >> 16) | 2]
        tt.clock_bytes_in(data, 9)
    w      = clock_byte_in(((instr & 0x3F000000) >> 22) | 2)
    status = clock_byte(((instr & 0xC0000000) >> 28) | 2)
    pc     = clock_byte(((in1 & 0x03F) <<  2) | 2) 
    out_lo = clock_byte(((in1 & 0xFC0) >>  4) | 2)
    out_hi = clock_byte(((in2 & 0x03F) <<  2) | 2)
    out7   = clock_byte_in(((in2 & 0xFC0) >>  4) | 2)
    
    out = (out_lo >> 2) | ((out_hi & 0xFC) << 4)
    if out >= 2048:
        out -= 4096
    return (status, pc, out)

def hello():
    # Display HELLO
    #           ALU- A- B- C- D W- F- PC O I X K----- L-----
    run_instr(0b0000_00_00_00_0_00_00_00_0_0_0_000000_000000, 0b01110110, 0) # IN1=H
    run_instr(0b0000_11_00_00_0_00_00_00_0_0_0_000000_000000, 0b11111001, 0) # A=IN1, IN1=E.
    run_instr(0b0000_11_00_00_0_10_00_00_0_0_0_000000_000000, 0b00111001, 0) # W=A, A=IN1, IN1=L
    run_instr(0b0000_11_00_00_0_10_00_00_1_0_0_000000_000000, 0b10111001, 0) # OUT1=W, W=A, A=IN1, IN1=L.
    sleep(0.5) # H
    run_instr(0b0000_11_00_00_0_10_00_00_1_0_0_000000_000000, 0b00111111, 0) # OUT1=W, W=A, A=IN1, IN1=O
    sleep(0.5) # E.
    run_instr(0b0000_11_00_00_0_10_00_00_1_0_0_000000_000000, 0, 0) # OUT1=W, W=A, A=IN1
    sleep(0.5) # L
    run_instr(0b0000_01_00_00_0_10_00_00_1_0_0_000000_000000, 0, 0) # OUT1=W, W=A, A=0
    sleep(0.5) # L.
    run_instr(0b0000_00_00_00_0_10_00_00_1_0_0_000000_000000, 0, 0) # OUT1=W, W=A
    sleep(0.5) # O
    run_instr(0b0000_00_00_00_0_00_00_00_1_0_0_000000_000000, 0, 0) # OUT1=W
    sleep(0.5) # Off

def test_alu_op(alu_op, a, b, sym, expected_result):
    #           ALU- A- B- C- D W- F- PC O I X K----- L-----
    run_instr(0b0000_00_00_00_0_00_00_00_0_0_0_000000_000000, a, 0)     # IN1=a
    run_instr(0b0000_11_11_00_0_00_00_00_0_0_1_000000_000000 + b, 0, 0) # A=IN1, B=b
    run_instr(0b0000_00_00_00_0_01_10_00_0_0_0_000000_000000 + (alu_op << 28), 0, 0)  # W=ALU
    _, pc, out = run_instr(0b0000_00_00_00_0_00_00_00_1_0_0_000000_000000, 0, 0)  # OUT1=W

    if out == expected_result:
        print("PASS: ", end="")
    else:
        print("FAIL: ", end="")
    print(f"{b} {sym} {a} = {out} (expected: {expected_result})")

def load_val_to_c(val):
    run_instr(0b0000_00_11_00_0_00_00_00_0_0_1_000000_000000 + val, 0, 0) # B=val
    run_instr(0b0010_00_00_01_0_00_00_00_0_0_0_000000_000000, 0, 0) # C=B

def test_alu():
    test_alu_op(0b0000, 7, 35, "[0]", 0)   # Zero
    test_alu_op(0b0001, 7, 35, "[-A]", -7)  # -A
    test_alu_op(0b0010, 7, 35, "[B]", 35)  # B

    #           ALU- A- B- C- D W- F- PC O I X K----- L-----
    run_instr(0b0010_00_00_10_0_00_00_00_0_0_0_000000_000000, 0, 0)  # DEC
    test_alu_op(0b0011, 7, 35, "[C]", -1)  # C

    load_val_to_c(23)
    test_alu_op(0b0011, 7, 35, "[C]", 23)  # C

    test_alu_op(0b0100, 7, 35, "[A>>1]", 3)   # A>>1
    test_alu_op(0b0101, 7, 35, "+", 42)  # A+B
    test_alu_op(0b0110, 7, 35, "-", 28)  # B-A
    test_alu_op(0b0111, 7, 35, "+", 42)  # A+B+F
    test_alu_op(0b1000, 7, 35, "-", 28)  # B-A-F

    test_alu_op(0b0110, 35, 7, "-", -28)  # B-A
    test_alu_op(0b0111, 7, 35, "+F", 43)  # A+B+F
    test_alu_op(0b0110, 35, 7, "-", -28)  # B-A
    test_alu_op(0b1000, 7, 35, "-F", 27)  # B-A-F

    test_alu_op(0b1001, 7, 35, "|", 7|35)  # A|B
    test_alu_op(0b1010, 7, 35, "&", 7&35)  # A&B
    test_alu_op(0b1011, 7, 35, "^", 7^35)  # A^B
    test_alu_op(0b1100, 7, 35, "~", ~7)  # ~A
    test_alu_op(0b1101, 7, 35, "[A]", 7)  # A
    test_alu_op(0b1110, 8, 35, "[RND]", 0)  # Random number - disabled
    test_alu_op(0b1111, 9, 42, "[1]", 1)  # 1

def test_rng():
    clock_byte(20)

    for _ in range(10):
        run_instr(0b1110_00_00_00_0_01_00_00_0_0_0_000000_000000, 0, 0)  # W=RND
        _, pc, out1 = run_instr(0b1110_00_00_00_0_01_00_00_1_0_0_000000_000000, 0, 0)  # OUT1=W, W=RND
        _, pc, out2 = run_instr(0b1110_00_00_00_0_00_00_00_1_1_0_000000_000000, 0, 0)  # OUT2=W
        print("Random numbers: ", out1, out2)



class Program:
    def __init__(self, prog, in1=None, in2=None):
        self.prog = prog
        if in1 is not None:
            self.reset(in1, in2)
        
    def reset(self, in1, in2=None):
        self.pc = 0
        self.in1 = in1.copy()
        self.in2 = in2.copy() if in2 is not None else []
        self.out1 = []
        self.out2 = [] if in2 is not None else self.in2
        self.executed = 0
        
    def execute_one(self):
        in1 = (self.in1 or [0,])[0]
        in2 = (self.in2 or [0,])[0]
        stat, pc, out = run_instr(self.prog[self.pc], in1, in2)
        self.pc = pc
        if (stat & 0x1) != 0: self.in1.pop(0)
        if (stat & 0x2) != 0: self.in2.pop(0)
        if (stat & 0x4) != 0: self.out1.append(out)
        if (stat & 0x8) != 0: self.out2.append(out)
        self.executed += 1
       
    def run_until_out1_len(self, expected_len):
        # JMP 0 to prime the inputs
        run_instr(0b0000_00_00_00_0_00_00_01_0_0_0_000000_000000, (self.in1 or [0,])[0], (self.in2 or [0,])[0])
        self.pc = 0
        
        while len(self.out1) < expected_len:
            self.execute_one()
            
        return self.out1

def test_example_loop1():
    reset()
    
    #     ALU- A- B- C- D W- F- PC O I X K----- L-----
    prog = Program([
        0b0000_11_00_00_0_00_00_00_0_0_0_000000_000000,  # A=IN1
        0b0000_00_10_00_0_00_00_00_0_0_0_000000_000000,  # B=A
        0b0101_01_01_00_0_00_00_00_0_0_0_000000_000000,  # A=B=A+B
        0b0101_01_01_00_0_00_00_00_0_0_0_000000_000000,  # A=B=A+B
        0b0101_00_00_00_0_01_00_00_0_0_0_000000_000000,  # W=A+B
        0b0000_00_00_00_0_00_00_00_1_0_0_000000_000000,  # OUT1=W
        0b0000_00_00_00_0_00_00_01_0_0_0_000000_000000,  # JMP 0
    ])

    NUM_VALUES = 10
    in1 = [random.randint(-2048 // 8,2047 // 8) for x in range(NUM_VALUES)]
    
    prog.reset(in1)
    out = prog.run_until_out1_len(NUM_VALUES)
    print(in1)
    print(out)

    for i in range(NUM_VALUES):
        assert out[i] == in1[i] * 8


def test_aoc2020_1_1():
    reset()
    
    prog = Program([
        0x0f0017e4,
        0x6d001000,
        0x60127000,
        0x0c001000,
        0x10031011,
        0x60137007,
        0x0c009004,
        0x0c003000,
        0x0c003000,
        0x030017e4,
        0x6d183000,
        0x60127000,
        0x0c013011,
        0x10021000,
        0x6c137009,
        0x10031011,
        0x0000900e,
        0x270057e4,
        0x60081000,
        0x00005000,
    ])

    in1 = [
        2000, 50, 1984, 1648, 32, 1612, 1992, 1671, 1955, 1658, 1592, 1596, 1888, 1540, 239, 1677, 1602, 1877, 1481, 2004, 1985, 1829, 1980, 1500, 1120, 1849, 1941, 1403, 1515, 1915, 1862, 2002, 1952, 1893, 1494, 1610, 1432, 1547, 1488, 1642, 1982, 1666, 1856, 1889, 1691, 1976, 1962, 2005, 1611, 1665, 1816, 1880, 1896, 1552, 1809, 1844, 1553, 1841, 1785, 1968, 1491, 1498, 1995, 1748, 1533, 1988, 2001, 1917, 0
    ]

    executed = 0
    prog.reset(in1)
    t = time.ticks_ms()
    out = prog.run_until_out1_len(2)
    t = time.ticks_ms() - t
    print(f"Executed {prog.executed} instructions in {t}ms")
    print(out)
    assert out[0] + out[1] == 2020

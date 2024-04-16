from tt import TT
import time
import random

tt = TT()

in_val = 0
out_val = 0

def print_status(val):
    print("Ready? {}  Empty? {}  Val: {}".format("Y" if val & 1 else "N", "N" if val & 2 else "Y", val >> 2))

def send_clk():
    global out_val
    tt.send_receive_byte(in_val, 29)
    out_val = tt.send_receive_byte(in_val | 1, 29)
    print_status(out_val)

def reset():
    global in_val
    in_val = 0
    for _ in range(10):
        send_clk()
    in_val = 4
    send_clk()

def send_word(val, clear_wen=True):
    global in_val
    in_val = 2 + (val << 2)
    send_clk()
    if clear_wen:
        in_val = 4
        send_clk()

def peek(idx):
    global in_val
    in_val = 4 + (idx << 4)
    send_clk()

def pop():
    global in_val
    in_val = 12
    send_clk()
    in_val = 4

def fill_and_empty():
    reset()
    
    for i in range(1,53):
        send_word(i, False)

    for i in range(1,52):
        pop()

def is_ready():
    return (out_val & 1) != 0

def is_empty():
    return (out_val & 2) == 0

def random_test():
    reset()
    
    fifo = []
    
    for i in range(1000):
        if random.randint(0,1) == 1:
            if is_ready():
                word = random.randint(0, 63)
                send_word(word)
                fifo.append(word)
        else:
            if not is_empty():
                if random.randint(0,1) == 1:
                    pop()
                    if (out_val >> 2) != fifo[0]:
                        print("Error")
                        print_status(out_val)
                        print(fifo)
                        return
                    fifo.pop(0)
                else:
                    peek_idx = random.randint(0, min(2, len(fifo)-1))
                    peek(peek_idx)
                    if (out_val >> 2) != fifo[peek_idx]:
                        print("Error (peek {})".format(peek_idx))
                        print_status(out_val)
                        print(fifo)
                        return
            else:
                if len(fifo) != 0:
                    print("Error, fifo not empty")
                    print_status(out_val)
                    print(fifo)
                    return

    print(fifo)
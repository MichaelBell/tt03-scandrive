import rp2
from rp2 import PIO

# PIO program to send a byte, optionally selecting scan first
# and optionally latching.
# Input format is:
#  - 1 bit: Scan select, scans if 1.
#  - 1 bit: Latch enable, latches if 1.
#  - 8 bits: The byte
# Input must be left aligned.
# For every byte written one byte is read out of the scanchain and pushed
#
# Output pin is data pin
# Side-set pins are: clock, latch_en, scan_select (high to low)
@rp2.asm_pio(out_shiftdir=PIO.SHIFT_LEFT, autopull=True, pull_thresh=10,
             in_shiftdir=PIO.SHIFT_LEFT, autopush=True, push_thresh=8,
             out_init=(PIO.OUT_LOW,),
             sideset_init=(PIO.OUT_LOW, PIO.OUT_LOW, PIO.OUT_LOW))
def _tt03_pio_send_byte():
    label("top")
    out(x, 1)                             # Read scan select
    jmp(not_x, "no_scan")    .side(0b000)
    
    nop()                    .side(0b001) [1]  # Scan select
    nop()                    .side(0b101) [1]
    nop()                    .side(0b001) [1]
    
    label("no_scan")
    out(x, 1)                .side(0b000) # Read latch enable
    set(y, 7)                .side(0b000) # Will write 8 bits
    
    label("send_data")
    out(pins, 1)             .side(0b000) [1]
    in_(pins, 1)             .side(0b100)
    jmp(y_dec, "send_data")  .side(0b100)
    
    jmp(not_x, "top")        .side(0b000)
    nop()                    .side(0b010) [1]
    nop()                    .side(0b010) [1]
    jmp("top")               .side(0b010)

@rp2.asm_pio(autopull=True, pull_thresh=32,
             autopush=True, push_thresh=32,
             set_init=(PIO.OUT_LOW,),
             sideset_init=(PIO.OUT_LOW, PIO.OUT_LOW, PIO.OUT_LOW))
def _tt03_pio_send_zeroes():
    out(x, 32)                             # Read scan select
    set(pins, 0)              .side(0b000)
    
    label("loop")
    nop()                     .side(0b000)
    jmp(x_dec, "loop")        .side(0b100)
    in_(x, 32)                .side(0b000)
    
class TT_PIO:
    # Note that latch_en must be pin_scan_select+1 and clock must be pin_scan_select+2
    def __init__(self, sm_idx, pin_data_out, pin_data_in, pin_scan_select):
        self.sm = rp2.StateMachine(sm_idx, _tt03_pio_send_byte, freq=10_000_000, out_base=pin_data_out, in_base=pin_data_in, sideset_base=pin_scan_select)
        self.sm_z = rp2.StateMachine(sm_idx+1, _tt03_pio_send_zeroes, freq=62_500_000, set_base=pin_data_out, sideset_base=pin_scan_select)
        self.sm.active(1)
        self.sm_z.active(1)

    @micropython.native
    def send_byte_blocking(self, d, latch=False, scan=False):
        val = (0x200 if scan else 0) | (0x100 if latch else 0) | (d & 0xFF)
        self.sm.put(val, 22)
        return self.sm.get() & 0xFF

    @micropython.native
    def send_bytes_blocking(self, d, latch=False, scan=False):
        val = (0x200 if scan else 0) | (0x100 if latch else 0) | (d[0] & 0xFF)
        self.sm.put(val, 22)
        
        for i in range(1, len(d)):
            val = (0x100 if latch else 0) | (d[i] & 0xFF)
            self.sm.put(val, 22)
            self.sm.get()
        
        return self.sm.get() & 0xFF

    @micropython.native
    def send_zeroes_blocking(self, num, latch=False, scan=False):
        val = (0x200 if scan else 0) | (0x100 if latch else 0)
        self.sm.put(val, 22)
        
        val = (0x100 if latch else 0)
        for i in range(1, num):
            self.sm.put(val, 22)
            self.sm.get()
        
        return self.sm.get() & 0xFF

    @micropython.native
    def send_clocks_blocking(self, num):
        self.sm_z.put(num-1)
        self.sm_z.get()


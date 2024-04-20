from machine import Pin
from tt_pio import TT_PIO

class TT:
    def __init__(self):
        # Pin mapping - names from FPGA's point of view
        clk = Pin(2, Pin.OUT)
        data_in = Pin(3, Pin.OUT)
        latch_en = Pin(1, Pin.OUT)
        scan_select = Pin(0, Pin.OUT)

        clk_out = Pin(5, Pin.IN)
        data_out = Pin(4, Pin.IN)

        r=Pin(18, Pin.OUT)
        g=Pin(19, Pin.OUT)
        b=Pin(20, Pin.OUT)
        r.on()
        g.on()
        b.on()

        clk.off()
        data_in.off()
        latch_en.off()
        scan_select.off()

        self.tt = TT_PIO(0, data_in, data_out, scan_select)

    # Note this does not work for design 0 or 249.
    def send_receive_byte(self, byte_in, design_num):
        self.tt.send_byte_blocking(byte_in)
        clocks = int((design_num - 1) * 8.5)
        if (design_num & 1) == 0: clocks += 1
        self.tt.send_clocks_blocking(clocks)
        self.tt.send_byte_blocking(0, latch=True)
        self.tt.send_byte_blocking(0, scan=True)
        self.tt.send_clocks_blocking(2125 - clocks - 24)
        return self.tt.send_byte_blocking(0)

    # Note this does not work for design 0, 1 or 249.
    def clock_byte(self, byte_in, design_num):
        self.tt.send_byte_blocking(byte_in)
        self.tt.send_byte_blocking(byte_in | 1)
        clocks = int((design_num - 1) * 8.5)
        if (design_num & 1) == 0: clocks += 1
        self.tt.send_clocks_blocking(clocks - 8)
        self.tt.send_byte_blocking(0, latch=True)
        self.tt.send_byte_blocking(0, latch=True)
        self.tt.send_byte_blocking(0, scan=True)
        self.tt.send_clocks_blocking(2125 - clocks - 24)
        return self.tt.send_byte_blocking(0)

    # Note this does not work for design 0 or 1.
    # Doesn't read the output
    def clock_byte_in(self, byte_in, design_num):
        self.tt.send_byte_blocking(byte_in)
        self.tt.send_byte_blocking(byte_in | 1)
        clocks = int((design_num - 1) * 8.5)
        if (design_num & 1) == 0: clocks += 1
        self.tt.send_clocks_blocking(clocks - 8)
        self.tt.send_byte_blocking(0, latch=True)
        self.tt.send_byte_blocking(0, latch=True)

    # Note this does not work for design 0 or 1.
    # Doesn't read the output
    def clock_bytes_in(self, data, design_num):
        for byte_in in data:
            self.tt.send_byte_blocking(byte_in)
            self.tt.send_byte_blocking(byte_in | 1)
        clocks = int((design_num - 1) * 8.5)
        if (design_num & 1) == 0: clocks += 1
        clocks += 8 - 16 * len(data)
        assert(clocks > 0)
        self.tt.send_clocks_blocking(clocks)
        for _ in data:
            self.tt.send_byte_blocking(0, latch=True)
            self.tt.send_byte_blocking(0, latch=True)

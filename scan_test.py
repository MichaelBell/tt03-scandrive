from machine import Pin
import time

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

data_in.off()

i = 0
while data_out.value() == 1:
    clk.on()
    clk.off()
    i += 1
    if (i & 7) == 0: time.sleep(0.002)
print(i)

data_in.on()

i = 0
while data_out.value() == 0:
    clk.on()
    clk.off()
    i += 1
    if (i & 7) == 0: time.sleep(0.002)
print(i)


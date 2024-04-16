# TT03 MicroPython external scanchain driver

This has been tested with a Tiny2040 (it seemed appropriate), but should work just fine with a normal Pico.  You may want to remove the code that sets pins 18-20 on (that turns the RGB LED off on the Tiny2040).

For this to work, you need to either take the debounce caps off the demo board, or wire directly to the carrier board (supplying appropriate power).

## Wiring

| Signal      | Tiny2040 | TT3 demo board | TT3 carrier board |
| ----------- | -------- | -------------- | ----------------- |
| Scan select | 0        | in2            | io23              |
| Latch en    | 1        | in3            | io24              |
| Clk in      | 2        | in0            | io21              |
| Data in     | 3        | in1            | io22              |
| Data out    | 4        | out1           | io30              |
| Clk out     | 5        | out0           | io29              |

## Instructions

Instantiate the Tiny Tapeout driver:

```
from tt import TT
tt = TT()
```

Send the byte 0x11 to deisgn 18 (a 4 bit adder):
```
tt.send_receive_byte(0x11, 18)
```
if all is working, that should print 2 (= 1 + 1).

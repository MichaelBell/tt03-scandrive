import tt
import time

scan = tt.TT()

for i in range(256):
    scan.tt.send_clocks_blocking(4000)
    time.sleep_us(10)
    scan.tt.send_byte_blocking(i, latch=True)
    scan.tt.send_byte_blocking(0, scan=True)
    time.sleep_us(10)
    scan.tt.send_clocks_blocking(2125-16)
    time.sleep_us(10)
    result = scan.tt.send_byte_blocking(0x0)
    if i ^ 0xFF != result:
        print("Error: {:02x}: {:02x}".format(i, result))

#    print(scan.tt.send_byte_blocking(0x0))

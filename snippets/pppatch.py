import struct

stock = None
with open("Falcon_SmcCode.bin", "rb") as f:
    stock = bytearray(f.read())

with open("Falcon_SmcExploit.bin", "rb") as f:
    while True:
        address = f.read(4)
        if len(address) != 4:
            break
        address = struct.unpack(">I", address)[0]
        length = struct.unpack(">I", f.read(4))[0]
        print(f"address {address:04x}, length {length:04x}")
        stock[address:address+length] = f.read(length)

with open("Falcon_Patched.bin", "wb") as f:
    f.write(stock)

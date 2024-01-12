import socket

# connection settings and connect packet
print("Welcome to Shitty Classic Client pick a playername\n")
name = input("Pick Playername\n")
ip = input("Whats The Server IP Adress\n")
port = input("Whats The Server Port\n")
pvn_hex = input("Whats The Server Protocol Numbber \n")
if pvn_hex.startswith('x'):
    pvn_hex = pvn_hex[1:]
pvn_int = int(pvn_hex, 16)
pvn = bytes([pvn_int])
packet = bytearray()
packet += b"\x00"
packet += pvn
packet += name.ljust(64).encode("ascii")
packet += "-".ljust(64).encode("ascii")
packet += b"\x00"

# TCP Socket Horrors
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((ip, int(port)))
client.send(packet)

while True:
    # chat handler
    message = input("Type a Message\n")
    packet2 = bytearray()
    packet2 += b"\x0d"
    packet2 += bytes([0xFF])
    packet2 += message.ljust(64).encode("ascii")

    # TCP Socket Horrors 2
    client.send(packet2)
    print("Sent Message!!")
    if "/stop" in message:
        client.close()
        break
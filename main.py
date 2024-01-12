import socket


#connection settings and connect packet
print("Welcome to Shitty Classic Client pick a playername\n")
name = input("Pick Playername\n")
ip = input("Whats The Server IP Adress\n")
port = input("Whats The Server Port\n")
pvn = input("Whats The Server Protocol Hex example: x06 being pvn 6 \n")
if pvn.startswith('x'):
    pvn = pvn[1:]
packet = bytearray()
packet += b"\x00"
packet += bytes.fromhex(pvn)
packet += name.ljust(64).encode("ascii")
packet += "-".ljust(64).encode("ascii")
packet += b"\x00"

#TCP Socket Horrors
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
client.connect((ip, int(port))) 
client.send(packet)

while True:
    #chat handler
    message = input("Type a Message\n")
    packet2 = bytearray()
    packet2 += b"\x0d"
    packet2 += bytes([0xFF])
    packet2 += message.ljust(64).encode("ascii")

    #TCP Socket Horrors 2
    client.send(packet2)
    print("Sent Message!!") 
    if "/stop" in message:
            client.close()
            break

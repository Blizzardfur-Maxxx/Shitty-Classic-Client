import socket
import threading

stop_thread = False

def receive_messages(client_socket):
    global stop_thread
    while not stop_thread:
        try:
            data = client_socket.recv(1024)
            if not data:
                break
            try:
                packet_id = data[0]

                if packet_id == 0x00:  # Check if packet ID is 0x00 Server Identification 
                    decoded_data = data[2:].decode("ascii")  # Assuming data format: [packet_id, length, payload]
                    print(decoded_data)

                if packet_id == 0x01:  # Check if packet ID is 0x01 Ping 
                    pass
                
                if packet_id == 0x0d:  # Check if packet ID is 0x0d Chat 
                    decoded_data = data[2:].decode("ascii")  # Assuming data format: [packet_id, length, payload]
                    print(decoded_data)

                if packet_id == 0x0e:  # Check if packet ID is 0x0e Disconnect Player 
                    decoded_data = data[2:].decode("ascii")  # Assuming data format: [packet_id, length, payload]
                    print(decoded_data)
                    
            except UnicodeDecodeError as e:
                print("Error decoding message:", str(e))
        except socket.error as e:
            print("Error receiving message:", str(e))
            break

# connection settings and connect packet
print("Welcome to Shitty Classic Client pick a playername\n")
name = input("Pick Playername\n")
ip = input("Whats The Server IP Address\n")
port = input("Whats The Server Port\n")
pvn_hex = input("Whats The Server Protocol Number \n")
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

# Start a thread to receive messages
receive_thread = threading.Thread(target=receive_messages, args=(client,))
receive_thread.start()

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
        stop_thread = True  # Set the flag to signal the receiving thread to stop
        receive_thread.join()  # Wait for the receiving thread to finish
        client.close()
        break

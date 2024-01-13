import socket
import threading

stop_thread = False

# Dexrn: Please work!!!
def plswork(value):
   scale_factor = 2 ** 5 
   scaled_value = int(value * scale_factor)
   clamped_value = max(min(scaled_value, 1023), -1024)
   return clamped_value // 32 


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
                    try:
                        decoded_data = data[1:].decode("ascii")  # Assuming data format: [packet_id, length, payload]
                        print(decoded_data)
                    except: 
                        continue

                if packet_id == 0x0e:  # Check if packet ID is 0x0e Disconnect Player 
                    try:
                        decoded_data = data[1:].decode("ascii")  # Assuming data format: [packet_id, length, payload]
                        print(decoded_data)
                    except:
                        continue

                if packet_id == 0x0c:
                    try:
                        decoded_data = data[1:].decode("ascii")  
                        print(decoded_data)
                    except:
                        continue
                    
            except UnicodeDecodeError as e:
                print("Error decoding message:", str(e))
        except socket.error as e:
            print("Error receiving message:", str(e))
            break

# connection settings and connect packet
print("Welcome to Shitty Classic Client! Pick a Player Name\n")
name = input("Pick Player Name\n")
mppass1 = input('MPPass (Default is "-")\n')
mppass = str(mppass1) if mppass1 else "-"
ip = input("Server IP Address\n")
port1 = input("Server Port (Default is 25565)\n")
port = int(port1) if port1 else 25565
pvn_hex = input("PVN\n")
if pvn_hex.startswith('x'):
    pvn_hex = pvn_hex[1:]
pvn_int = int(pvn_hex, 16)
pvn = bytes([pvn_int])
packet = bytearray()
packet += b"\x00"
packet += pvn
packet += name.ljust(64).encode("ascii")
packet += mppass.ljust(1024).encode("ascii")
packet += b"\x00"

# TCP Socket Horrors
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((ip, int(port)))
client.send(packet)

receive_thread = threading.Thread(target=receive_messages, args=(client,))
receive_thread.start()

while True:
    # chat handler
    message = input("\n")
    if "/" in message: 
        if message.startswith("/tp"):
            command = message.split()
            try:
                pname = name
                x = float(command[1])
                y = float(command[2])
                z = float(command[3])
                yaw = float(command[4])
                pitch = float(command[5])

                x_fixed = plswork(x)
                y_fixed = plswork(y)
                z_fixed = plswork(z)

                sbPacket = bytearray()
                sbPacket += b'\x08' 
                sbPacket += bytes([0xFF])
                sbPacket += x_fixed.to_bytes(2, byteorder='big', signed=True) 
                sbPacket += y_fixed.to_bytes(2, byteorder='big', signed=True)
                sbPacket += z_fixed.to_bytes(2, byteorder='big', signed=True)
                sbPacket += yaw.to_bytes(1, byteorder='big', signed=True)
                sbPacket += pitch.to_bytes(1, byteorder='big', signed=True)

                print(sbPacket)
                client.send(sbPacket)
            except IndexError:
                print("Invalid command format.")


            except ValueError:
                print("Invalid coordinates or block type. Please provide valid integers.")


    else:
        packet2 = bytearray()
        packet2 += b"\x0d"
        packet2 += bytes([0xFF])
        packet2 += message.ljust(64).encode("ascii")

        # TCP Socket Horrors 2
        client.send(packet2)
        
        if "/stop" in message:
            stop_thread = True  # Set the flag to signal the receiving thread to stop
            receive_thread.join()  # Wait for the receiving thread to finish
            client.close()
            break

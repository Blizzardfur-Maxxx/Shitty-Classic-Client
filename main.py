import socket
import threading
import os
import sys
import packets
import chat

stop_thread = False
showblockupdates = False
global cpe
global name
cpe = None
receive_thread = None

serverIdentificationPacket = 0x00
extInfoPacket = 0x10
extEntryPacket = 0x11
pingPacket = 0x01
messagePacket = 0x0D
disconnectPlayerPacket = 0x0E
setPosOrientationPacket = 0x08
despawnPlayerPacket = 0x0C
levelFinalizePacket = 0x04
setBlockPacket = 0x06
posUpdatePacket = 0x0A

def coordFix(value):
    scale_factor = 2**5
    scaled_value = int(value * scale_factor)
    clamped_value = max(min(scaled_value, 1023), -1024)
    return clamped_value // 32

def handlePackets(client_socket, cpe):
    global stop_thread
    while not stop_thread:
        try:
            data = client_socket.recv(1024)
            if not data:
                break
            try:
                packet_id = data[0]
                if packet_id == serverIdentificationPacket:
                    packets.handleServerIdentificationPacket(data)
                if packet_id == extInfoPacket and cpe == "yes":
                    packets.handleExtInfoPacket(data, client)
                if packet_id == extEntryPacket and cpe == "yes":
                    packets.handleExtEntryPacket(data, client)
                if packet_id == pingPacket:
                    packets.handlePingPacket(data)
                if packet_id == messagePacket:
                    packets.handleChatPacket(data)
                if packet_id == disconnectPlayerPacket:
                    packets.handleDisconnectPacket(data)
                if packet_id == setPosOrientationPacket:
                    packets.handleSetPosOrientationPacket(data)
                if packet_id == despawnPlayerPacket:
                    packets.handleDespawnplayerPacket(data)
                if packet_id == levelFinalizePacket:
                    packets.handleLevelFinalizePacket(data)
                if packet_id == setBlockPacket:
                    packets.handleSetBlockPacket(data, showblockupdates)
                if packet_id == posUpdatePacket:
                    packets.handlePosUpdatePacket(data)
            except UnicodeDecodeError as e:
                continue
        except socket.error as e:
            print("Socket error: ", str(e))
            stop_thread = True
            sys.exit()
        except Exception as e:
            print("Packet Error! ", str(e))

def postConnect(client):
    try:
        global stop_thread
        while True:
            message = input("> ")
            if message.startswith("c/"):
                if message.startswith("c/help"):
                    print(f"List of available client commands:")
                    print(
                        f'"c/toggleshowblockupdates": Shows a message in console when block updates happen on the server.\n'
                        f'"c/tp <x> <y> <z> <yaw> <pitch>": Teleports the player to the specified XYZ coordinates.\n'
                        f'"c/setblock <x> <y> <z> <place/destroy> <Block ID>": Attempts to place a block at the specified XYZ coordinates.\n'
                        f'"c/stop": Closes the connection and the client.'
                    )
                if message.startswith("c/toggleshowblockupdates"):
                    global showblockupdates
                    showblockupdates = not showblockupdates
                    status = "on" if showblockupdates else "off"
                    print(f"Turned {status} Show Block Updates")
                if message.startswith("c/tp"):
                    command = message.split()
                    try:
                        x = int(float(command[1]) * 32)
                        y = int(float(command[2]) * 32)
                        z = int(float(command[3]) * 32)
                        yaw = int(command[4])
                        pitch = int(command[5])

                        tpPacket = bytearray()
                        tpPacket += b"\x08"
                        tpPacket += bytes([0xFF])
                        tpPacket += x.to_bytes(2, byteorder="big", signed=True)
                        tpPacket += y.to_bytes(2, byteorder="big", signed=True)
                        tpPacket += z.to_bytes(2, byteorder="big", signed=True)
                        tpPacket += yaw.to_bytes(1, byteorder="big", signed=False)
                        tpPacket += pitch.to_bytes(1, byteorder="big", signed=False)

                        print(tpPacket)

                        client.send(tpPacket)
                    except (IndexError, ValueError) as e:
                        print(f"Invalid command format. {e}")
                        continue

                if message.startswith("c/setblock"):
                    command = message.split()
                    try:
                        x = int(command[1])
                        y = int(command[2])
                        z = int(command[3])
                        updateBlockMode = str(command[4])
                        id = int(command[5])

                        sbPacket = bytearray()
                        sbPacket += b"\x05"
                        sbPacket += x.to_bytes(2, byteorder="big", signed=True)
                        sbPacket += y.to_bytes(2, byteorder="big", signed=True)
                        sbPacket += z.to_bytes(2, byteorder="big", signed=True)
                        sbPacket += (1 if updateBlockMode.lower() == "place" else 0).to_bytes(1, byteorder="big", signed=True)
                        sbPacket += id.to_bytes(1, byteorder="big", signed=True)

                        print(sbPacket)
                        client.send(sbPacket)
                    except (IndexError, ValueError) as e:
                        print(f"Invalid command format. {e}")

                if message.startswith("c/stop"):
                    stop_thread = True
                    sys.exit()
            else:
                if not message.startswith("c/"):
                    chat.sendMessage(message, client)
    except KeyboardInterrupt:
        print("Exiting!")
        sys.exit()

client = None

def connect(pvn, name, mppass, ip, port, cpe):
    packet = bytearray()
    packet += b"\x00"
    packet += pvn
    packet += name.ljust(64).encode("ascii")
    packet += mppass.ljust(64).encode("ascii")
    packet += b"\x42" if cpe == "yes" else b"\x00"
    
    global client
    global receive_thread
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"\nConnecting to {ip}:{port} with username {name}")
    try:
        client.connect((ip, int(port)))
        client.send(packet)
        receive_thread = threading.Thread(target=handlePackets, args=(client, cpe,))
        receive_thread.start()
    except Exception as e:
        print(f"\nFailed to connect to {ip}:{port}! {e}")
    print(f"\nConnected!\nType c/help for client commands.\n")
    postConnect(client)

def main():
    print(
        "Welcome to Shitty Classic Client!\nhttps://github.com/Blizzardfur-Maxxx/Shitty-Classic-Client"
    )
    if os.path.exists("connect.txt"):
        connectFile = open("connect.txt", "r")
        name = connectFile.readline().strip()
        mppass1 = connectFile.readline().strip()
        mppass = str(mppass1) if mppass1 else "-"
        ip = connectFile.readline().strip()
        port1 = connectFile.readline().strip()
        port = int(port1) if port1 else 25565
        pvn_hex = connectFile.readline().strip()
        if pvn_hex.startswith("x"):
            pvn_hex = pvn_hex[1:]
        pvn_int = int(pvn_hex, 16)
        pvn = bytes([pvn_int])
        cpe = connectFile.readline().strip()
    else:
        while True:
            name = input("\nPlayer Name\n> ")
            if name:
                break
            else:
                print("Please enter a valid name.")
        mppass1 = input(
            '\nMPPass (Default is "-")\nNOTE: This will be shown as plaintext on screen while typing it.\n> '
        )
        mppass = str(mppass1) if mppass1 else "-"
        while True:
            ip = input("\nServer IP Address\n> ")
            if ip:
                break
            else:
                print("Please enter a valid IP address.")
        port1 = input("\nServer Port (Default is 25565)\n> ")
        port = int(port1) if port1 else 25565
        cpe = input("\nCPE? (yes/no)\n> ")
        if cpe == "yes":
            pvn_hex = "7"
            if pvn_hex.startswith("x"):
                pvn_hex = pvn_hex[1:]
            pvn_int = int(pvn_hex, 16)
            pvn = bytes([pvn_int])
        else:
            while True:
                pvn_hex = input("\nPVN\n> ")
                if pvn_hex:
                    break
                else:
                    print("Please enter a valid PVN.")
            if pvn_hex.startswith("x"):
                pvn_hex = pvn_hex[1:]
            pvn_int = int(pvn_hex, 16)
            pvn = bytes([pvn_int])
    connect(pvn, name, mppass, ip, port, cpe)

if __name__ == "__main__":
    main()

import socket
import threading
import re
import os

stop_thread = False
showblockupdates = False

def processChatMessage(message):
    if "Windows" in os.name:
        print(message)
        return

    colorMappings = {
        "&0": "\033[30m",
        "&1": "\033[34m",
        "&2": "\033[32m",
        "&3": "\033[36m",
        "&4": "\033[31m",
        "&5": "\033[35m",
        "&6": "\033[33m",
        "&7": "\033[37m",
        "&8": "\033[90m",
        "&9": "\033[94m",
        "&a": "\033[92m",
        "&b": "\033[96m",
        "&c": "\033[91m",
        "&d": "\033[95m",
        "&e": "\033[93m",
        "&f": "\033[97m",
    }

    colorPattern = re.compile(r"&[0-9a-f]")
    colorPatternSegments = colorPattern.split(message)

    coloredMessage = []
    for i in range(len(colorPatternSegments)):
        segment = colorPatternSegments[i]
        if segment in colorMappings:
            coloredMessage.append(colorMappings[segment])
        elif i > 0 and colorPatternSegments[i - 1] in colorMappings:
            coloredMessage.append(segment)
        else:
            coloredMessage.append("\033[0m" + segment)

    print("".join(coloredMessage) + "\033[0m")


# Dexrn: Please work!!!
def coordFix(value):
    scale_factor = 2**5
    scaled_value = int(value * scale_factor)
    clamped_value = max(min(scaled_value, 1023), -1024)
    return clamped_value // 32


serverIdentificationPacket = 0x00
pingPacket = 0x01
levelInitializePacket = 0x02
levelDataChunkPacket = 0x03
levelFinalizePacket = 0x04
setBlockPacket = 0x06
spawnPlayerPacket = 0x07
setPosOrientationPacket = 0x08
posOrientationUpdatePacket = 0x09
posUpdatePacket = 0x0A
orientationUpdatePacket = 0x0B
despawnPlayerPacket = 0x0C
messagePacket = 0x0D
disconnectPlayerPacket = 0x0E
updateUserTypePacket = 0x0F


def packets(client_socket):
    global stop_thread
    while not stop_thread:
        try:
            data = client_socket.recv(1024)
            if not data:
                break
            try:
                packet_id = data[0]

                if packet_id == serverIdentificationPacket:
                    try:
                        packetDataDecoded = data[2:].decode("ascii")
                        print(packetDataDecoded)
                    except:
                        continue

                if packet_id == pingPacket:
                    pass

                if packet_id == messagePacket:
                    try:
                        packetDataDecoded = data[1:].decode("ascii")
                        processChatMessage(packetDataDecoded)
                    except:
                        continue

                if packet_id == disconnectPlayerPacket:
                    try:
                        packetDataDecoded = data[1:].decode("ascii")
                        print(f"DISCONNECTED: {packetDataDecoded}")
                        stop_thread = True
                        receive_thread.join()
                        client.close()
                        break
                    except:
                        continue

                if packet_id == despawnPlayerPacket:
                    try:
                        packetDataDecoded = data[1:].decode("ascii")
                        print(packetDataDecoded)
                    except:
                        continue
                if packet_id == levelFinalizePacket:
                    try:
                        packetDataDecoded = data[1:].decode("ascii")
                        print(packetDataDecoded)
                    except:
                        continue
                if packet_id == setBlockPacket:
                    try:
                        if showblockupdates is True:
                            # Dexrn: OH MY GOD XYZ ARE 2 BYTES
                            X = int.from_bytes(data[1:3], byteorder="big")
                            Y = int.from_bytes(data[3:5], byteorder="big")
                            Z = int.from_bytes(data[5:7], byteorder="big")
                            block_ID = int.from_bytes(data[7:], byteorder="big")

                            if block_ID == 0:
                                state = "broke"
                                print(f"Player {state} block at ({X}, {Y}, {Z})")
                            else:
                                state = "placed"
                                print(f"Player {state} block {block_ID} at ({X}, {Y}, {Z})")
                    except UnicodeDecodeError:
                        continue
                if packet_id == posUpdatePacket:
                    try:
                        X = int.from_bytes(data[3:3], byteorder="big")
                        Y = int.from_bytes(data[4:4], byteorder="big")
                        Z = int.from_bytes(data[5:5], byteorder="big")

                        # print(f"Player Pos Update: {X}, {Y}, {Z}")
                    except:
                        continue

            except UnicodeDecodeError as e:
                print("Error decoding message:", str(e))
                continue
        except socket.error as e:
            print("Error receiving message:", str(e))
            continue


def postConnect(name):
    global stop_thread
    while True:
        # chat handler
        message = input("> ")
        if message.startswith("i/"):
            if message.startswith("i/help"):
                print(f"List of available client commands:")
                print(f"\"i/toggleshowblockupdates\": Shows a message in console when block updates happen on the server.")
            if message.startswith("i/toggleshowblockupdates"):
                global showblockupdates
                if showblockupdates is True:
                    print(f"Turned off Show Block Updates")
                    showblockupdates = False
                if showblockupdates is False:
                    print(f"Turned on Show Block Updates")
                    showblockupdates = True
        if message.startswith("/"):
            if message.startswith("/tp"):
                command = message.split()
                try:
                    pname = name
                    x = float(command[1])
                    y = float(command[2])
                    z = float(command[3])
                    yaw = float(command[4])
                    pitch = float(command[5])

                    x_fixed = coordFix(x)
                    y_fixed = coordFix(y)
                    z_fixed = coordFix(z)
                    yaw_fixed = coordFix(yaw)
                    pitch_fixed = coordFix(pitch)

                    tpPacket = bytearray()
                    tpPacket += b"\x08"
                    tpPacket += bytes([0xFF])
                    tpPacket += x_fixed.to_bytes(2, byteorder="big", signed=True)
                    tpPacket += y_fixed.to_bytes(2, byteorder="big", signed=True)
                    tpPacket += z_fixed.to_bytes(2, byteorder="big", signed=True)
                    tpPacket += yaw.to_bytes(1, byteorder="big", signed=True)
                    tpPacket += pitch.to_bytes(1, byteorder="big", signed=True)

                    print(tpPacket)
                    client.send(tpPacket)
                except IndexError:
                    print("Invalid command format.")

                except ValueError:
                    print(
                        "Invalid coordinates or block type. Please provide valid integers."
                    )

            if message.startswith("/setblock"):
                command = message.split()
                try:
                    pname = name
                    x = int(command[1])
                    y = int(command[2])
                    z = int(command[3])
                    mode = int(command[4])
                    id = int(command[5])

                    sbPacket = bytearray()
                    sbPacket += b"\x05"
                    sbPacket += x.to_bytes(2, byteorder="big", signed=True)
                    sbPacket += y.to_bytes(2, byteorder="big", signed=True)
                    sbPacket += z.to_bytes(2, byteorder="big", signed=True)
                    sbPacket += mode.to_bytes(1, byteorder="big", signed=True)
                    sbPacket += id.to_bytes(1, byteorder="big", signed=True)

                    print(sbPacket)
                    client.send(sbPacket)
                except IndexError:
                    print("Invalid command format.")

                except ValueError:
                    print(
                        "Invalid coordinates or block type. Please provide valid integers."
                    )

            if message.startswith("/stop"):
                stop_thread = (
                    True  
                )
                receive_thread.join()  
                client.close()
                break

        else:
            if not message.startswith("i/"):
                packet2 = bytearray()
                packet2 += b"\x0d"
                packet2 += bytes([0xFF])
                packet2 += message.ljust(64).encode("ascii")

                # TCP Socket Horrors 2
                client.send(packet2)


client = None
receive_thread = None


# TCP Socket Horrors
def connect(pvn, name, mppass, ip, port):
    packet = bytearray()
    packet += b"\x00"
    packet += pvn
    packet += name.ljust(64).encode("ascii")
    # magic value no changey
    packet += mppass.ljust(64).encode("ascii")
    packet += b"\x00"
    global client
    global receive_thread
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"\nConnecting to {ip}:{port} with username {name}")
    try:
        client.connect((ip, int(port)))
        client.send(packet)
        receive_thread = threading.Thread(target=packets, args=(client,))
        receive_thread.start()
    except:
        print(f"\nFailed to connect to {ip}:{port}!")
    print(f"\nConnected!\nType i/help for client commands.\n")
    postConnect(name)


# connection settings and connect packet
def main():
    print(
        "Welcome to Shitty Classic Client!\nhttps://github.com/Blizzardfur-Maxxx/Shitty-Classic-Client"
    )
    while True:
        name = input("\nPlayer Name\n> ")
        if name:
            break
        else:
            print("Please enter a valid name.")
    mppass1 = input('\nMPPass (Default is "-")\nNOTE: This will be shown as plaintext on screen while typing it.\n> ')
    mppass = str(mppass1) if mppass1 else "-"
    while True:
        ip = input("\nServer IP Address\n> ")
        if ip:
            break
        else:
            print("Please enter a valid IP address.")
    port1 = input("\nServer Port (Default is 25565)\n> ")
    port = int(port1) if port1 else 25565
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
    connect(pvn, name, mppass, ip, port)


if __name__ == "__main__":
    main()

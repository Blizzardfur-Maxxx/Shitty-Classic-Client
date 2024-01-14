import main as mainClient
import chat
import re

def handleServerIdentificationPacket(data):
    packetDataDecoded = data[2:].decode("ascii")
    print(packetDataDecoded)

def handlePingPacket(data):
    pass

def handleChatPacket(data):
    packetDataDecoded = data[1:].decode("ascii")
    chat.processChatMessage(packetDataDecoded)

def handleDisconnectPacket(data):
    packetDataDecoded = data[1:].decode("ascii")
    print(f"DISCONNECTED: {packetDataDecoded}")
    mainClient.client.close()

def handleDespawnplayerPacket(data):
    packetDataDecoded = data[1:].decode("ascii")
    print(packetDataDecoded)

def handleLevelFinalizePacket(data):
    packetDataDecoded = data[1:].decode("ascii")
    print(packetDataDecoded)

def handleSetBlockPacket(data, showblockupdates):
    if showblockupdates is True:
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

def handlePosUpdatePacket(data):
    X = int.from_bytes(data[3:3], byteorder="big")
    Y = int.from_bytes(data[4:4], byteorder="big")
    Z = int.from_bytes(data[5:5], byteorder="big")

    # print(f"Player Pos Update: {X}, {Y}, {Z}")

def handleSetPosOrientationPacket(data):
    pass

def handleExtInfoPacket(data, client):
    packetDataDecoded = data[1:].decode("ascii")
    print(packetDataDecoded)
    sendExtInfoPacket(client)

def sendExtInfoPacket(client):
    extInfo = bytearray()
    extInfo += b"\x10"
    extInfo += "Shitty Classic Client".ljust(64).encode("ascii")
    extInfo += (0).to_bytes(2, byteorder="big", signed=True)
    client.send(extInfo)

def handleExtEntryPacket(data, client):
    packetDataDecoded = data[1:].decode("ascii")
    # supportedExtensions = re.sub(r'[^\x20-\x7E]', '', packetDataDecoded)
    # supportedExtensions = ' '.join(supportedExtensions.split())
    # print(f"Supported Extensions: {supportedExtensions}")
    # Dexrn: I don't think we have to send because we don't use any extensions.
    # sendExtEntryPacket(client)

def sendExtEntryPacket(client):
    extEntry = bytearray()
    extEntry += b"\x11"
    extEntry += "LongerMessages".ljust(64).encode("ascii")
    extEntry += (1).to_bytes(2, byteorder="big", signed=True)
    client.send(extEntry)

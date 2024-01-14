import main as client
import chat

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
            client.receive_thread.join()
            client.client.close()
def handleDespawnplayerPacket(data):
            packetDataDecoded = data[1:].decode("ascii")
            print(packetDataDecoded)
def handleLevelFinalizePacket(data):
            packetDataDecoded = data[1:].decode("ascii")
            print(packetDataDecoded)
def handleSetBlockPacket(data, showblockupdates):
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
def handlePosUpdatePacket(data):
            X = int.from_bytes(data[3:3], byteorder="big")
            Y = int.from_bytes(data[4:4], byteorder="big")
            Z = int.from_bytes(data[5:5], byteorder="big")

            # print(f"Player Pos Update: {X}, {Y}, {Z}")
def handleSetPosOrientationPacket(data):
    pass
import os
import re

def sendMessage(message, client):
    packet2 = bytearray()
    packet2 += b"\x0d"
    packet2 += bytes([0xFF])
    packet2 += message.ljust(64).encode("ascii")

    # TCP Socket Horrors 2
    client.send(packet2)

def processChatMessage(message):
    if "Windows" in os.name or "nt" in os.name:
        colorPattern = re.compile(r"&[0-9a-f]")
        message_without_colors = colorPattern.sub("", message)
        print(message_without_colors)
        return
    else:
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

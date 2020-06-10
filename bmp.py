import re

from collections import namedtuple
from serial.tools import list_ports

Device = namedtuple("Device", "vid pid description")
bmp = Device(0x1d50, 0x6018, "Black Magic Probe")

for port in list(list_ports.comports()):
    if port.vid == bmp.vid and port.pid == bmp.pid:
        with open("launch.json", "r") as f:
            conf = f.readlines()
            for i, line in enumerate(conf):
                if "BMPGDBSerialPort" in line:
                    # Regex black magic... Get it?
                    conf[i] = re.sub(r"(?<=: ).+(?=,)", '"' +
                                     port.device + '"', line)
        with open("launch.json", "w") as f:
            f.writelines(conf)
        break

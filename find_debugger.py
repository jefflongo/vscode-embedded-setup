from argparse import ArgumentParser
from collections import namedtuple
from json import dump, load
from serial.tools import list_ports


def update_bmp(device_path):
    # Find and replace current BMPGDBSerialPort device path in debug configurations
    with open(".vscode/launch.json", 'r') as file:
        data = load(file)
        for i, conf in enumerate(data["configurations"]):
            if ("BMPGDBSerialPort" in conf):
                data["configurations"][i]["BMPGDBSerialPort"] = device_path
    with open(".vscode/launch.json", 'w') as file:
        dump(data, file, indent=4)

    # Find and replace device path in flash task
    with open(".vscode/tasks.json", "r") as file:
        data = load(file)
        for i, task in enumerate(data["tasks"]):
            if ("label" in task and "args" in task and task["label"] == "flash"):
                for j, arg in enumerate(task["args"]):
                    if ("target" in arg):
                        data["tasks"][i]["args"][j] = "'target extended-remote " + \
                            device_path + "'"
                        break
                break
    with open(".vscode/tasks.json", 'w') as file:
        dump(data, file, indent=4)


def update_stlink(device_path):
    # Find and replace device path in flash task
    with open(".vscode/tasks.json", "r") as file:
        data = load(file)
        for i, task in enumerate(data["tasks"]):
            if ("label" in task and "args" in task and task["label"] == "flash"):
                for j, arg in enumerate(task["args"]):
                    if ("port" in arg):
                        data["tasks"][i]["args"][j] = "port=" + device_path
                        break
                break
    with open(".vscode/tasks.json", 'w') as file:
        dump(data, file, indent=4)


if __name__ == "__main__":
    Device = namedtuple("Device", "vid pid description")
    bmp = Device(0x1d50, 0x6018, "Black Magic Probe")
    stlink = Device(None, None, "ST-Link")
    devices = {
        "bmp": bmp,
        "stlink": stlink
    }

    parser = ArgumentParser()
    parser.add_argument("-d", "--device", dest="dev", required=True)
    args = parser.parse_args()

    if (args.dev is None or args.dev not in devices):
        parser.error("invalid device")

    target = devices[args.dev]

    for port in list(list_ports.comports()):
        if port.vid == target.vid and port.pid == target.pid:
            if (target is bmp):
                update_bmp(port.device)
            elif (target is stlink):
                update_stlink(port.device)
            break

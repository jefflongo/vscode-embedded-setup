from argparse import ArgumentParser
from collections import namedtuple
from json import dump, load
from os import chdir, path
from serial.tools import list_ports
from sys import argv


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
    Debugger = namedtuple("Debugger", "vid pid, description")
    bmp = [
        Debugger(0x1d50, 0x6018, "Black Magic Probe")
    ]
    stlink = [
        Debugger(0x0483, 0x3744, "ST-Link v1"),
        Debugger(0x0483, 0x3748, "ST-Link v2"),
        Debugger(0x0483, 0x374b, "ST-Link v2.1"),
        Debugger(0x0483, 0x3752, "ST-Link v2.1"),
        Debugger(0x0483, 0x374d, "ST-Link v3 Loader"),
        Debugger(0x0483, 0x374e, "ST-Link v3"),
        Debugger(0x0483, 0x374f, "ST-Link v3"),
        Debugger(0x0483, 0x3753, "ST-Link v3")
    ]
    debuggers = {
        "bmp": bmp,
        "stlink": stlink
    }

    parser = ArgumentParser()
    parser.add_argument("--debugger", dest="family", required=True)
    args = parser.parse_args()

    if (args.family is None or args.family not in debuggers):
        parser.error("invalid device")

    family = debuggers[args.family]

    for port in list(list_ports.comports()):
        for model in family:
            if (port.vid == model.vid and port.pid == model.pid):
                chdir(path.dirname(path.realpath(argv[0])))
                if (family is bmp):
                    update_bmp(port.device)
                elif (family is stlink):
                    update_stlink(port.device)
                quit()

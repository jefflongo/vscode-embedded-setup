from argparse import ArgumentParser
from json import dump
from os import path, rename, mkdir
from sys import argv

TASKS_VERSION = "2.0.0"
LAUNCH_VERSION = "0.2.0"
C_CPP_PROPERTIES_VERSION = 4

debugger_options = ["bmp", "jlink", "stlink"]
hal_options = ["hal", "ll", "both"]


def generate_launch(args):
    launch = {
        "name": "Launch",
        "cwd": "${workspaceRoot}",
        "executable": "${workspaceFolder}/build/" + args.app + ".elf",
        "request": "launch",
        "type": "cortex-debug",
    }
    attach = {
        "name": "Attach",
        "cwd": "${workspaceRoot}",
        "executable": "${workspaceFolder}/build/" + args.app + ".elf",
        "request": "attach",
        "type": "cortex-debug",
    }

    if (args.debugger == "bmp"):
        launch["servertype"] = "bmp"
        attach["servertype"] = "bmp"

        launch["BMPGDBSerialPort"] = ""
        attach["BMPGDBSerialPort"] = ""

        launch["interface"] = "swd"
        attach["interface"] = "swd"

    elif (args.debugger == "jlink"):
        launch["servertype"] = "jlink"
        attach["servertype"] = "jlink"

        serverpath = input("Full path to JLinkGDBServerCL executable: ")
        launch["serverpath"] = serverpath
        attach["serverpath"] = serverpath

        device = input("Full device name (i.e. STM32G431KB): ").upper()
        launch["device"] = device
        attach["device"] = device

        launch["interface"] = "swd"
        attach["interface"] = "swd"

        launch["serialNumber"] = ""
        attach["serialNumber"] = ""

    elif (args.debugger == "stlink"):
        launch["servertype"] = "openocd"
        attach["servertype"] = "openocd"

        launch["configFiles"] = [
            "interface/stlink.cfg",
            "target/" + args.family[:7].lower() + ".cfg"
        ]
        attach["configFiles"] = [
            "interface/stlink.cfg",
            "target/" + args.family[:7].lower() + ".cfg"
        ]

        launch["servertype"] = "openocd"
        attach["servertype"] = "openocd"

    launch["preLaunchTask"] = "build"
    attach["preLaunchTask"] = "build"

    parent = {
        "version": LAUNCH_VERSION,
        "configurations": [
            launch,
            attach
        ]
    }
    with open("../.vscode/launch.json", 'w') as file:
        dump(parent, file, indent=4)


def generate_tasks(args):
    build = {
        "label": "build",
        "type": "shell",
        "windows": {
            "command": "mingw32-make"
        },
        "command": "make",
        "group": {
            "kind": "build",
            "isDefault": True
        }
    }
    tasks = [build]

    if (args.debugger is not None and args.debugger == "bmp"):
        bmp = {
            "label": "bmp",
            "type": "shell",
            "options": {
                "cwd": "${workspaceFolder}"
            },
            "command": "python",
            "args": [
                "bmp.py"
            ]
        }
        tasks.append(bmp)

    parent = {
        "version": TASKS_VERSION,
        "tasks": tasks
    }
    with open("../.vscode/tasks.json", 'w') as file:
        dump(parent, file, indent=4)


def generate_c_cpp_properties(args):
    defines = [
        "DEBUG",
        "_DEBUG",
        "UNICODE",
        "_UNICODE",
    ]
    if (args.hal is not None):
        if (args.hal == "hal" or args.hal == "both"):
            defines.append("USE_HAL_DRIVER")
        if (args.hal == "ll" or args.hal == "both"):
            defines.append("USE_FULL_LL_DRIVER")
    if (args.family is not None):
        defines.append(args.family[:9].upper() + args.family[-2:].lower())
    conf = {
        "name": "STM32",
        "defines": defines
    }

    parent = {
        "configurations": [conf],
        "version": C_CPP_PROPERTIES_VERSION
    }
    with open("../.vscode/c_cpp_properties.json", 'w') as file:
        dump(parent, file, indent=4)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--app", dest="app",
                        help="name of executable <app>.elf")
    parser.add_argument("--debugger", dest="debugger",
                        help="type of debugger [" + ", ".join(debugger_options) + "] (jlink requires JLink tools installed, stlink requires openocd installed)")
    parser.add_argument("--family", dest="family",
                        help="STM32 family (i.e. STM32G431xx)")
    parser.add_argument("--hal", dest="hal",
                        help="HAL libraries to be included [" + ", ".join(hal_options) + "]")
    args = parser.parse_args()

    # Validate args
    if (len(argv) == 1):
        parser.error("no arguments supplied")

    if (args.debugger is not None and args.debugger not in debugger_options):
        parser.error("invalid debugger selected")

    if (args.hal is not None and args.hal not in hal_options):
        parser.error("invalid HAL option selected")

    if (args.family is not None and
        (args.family[:5].upper() != "STM32" or
         args.family[-2:].lower() != "xx" or
         len(args.family) != 11)):
        parser.error("invalid family selected")

    # Setup and move files and directories
    if (args.debugger is not None and args.debugger == "bmp" and path.exists("../bmp.py") == False):
        rename("bmp.py", "../bmp.py")
    if (path.exists("../.clang-format") == False):
        rename(".clang-format", "../.clang-format")
    if (path.exists("../build") == False):
        mkdir("../build")
    if (path.exists("../.vscode") == False):
        mkdir("../.vscode")

    # Generate vscode JSON files
    generate_c_cpp_properties(args)
    generate_tasks(args)
    if (args.debugger is not None and args.app is not None and args.family is not None):
        generate_launch(args)

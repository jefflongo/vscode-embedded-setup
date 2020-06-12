# VSCode STM32 Configurator

Simple scripts to generate an STM32 vscode environment.

I found myself creating variations of STM32 development environments in vscode depending on the debugger and STM32 MCU I happened to be using at the time. `setup.py` is used to generate a vscode environment with proper defines and include paths for intellisense, launch/attach debug configurations for various supported debuggers, and built in tasks to build your project/flash a target.

Supported Debuggers:
- Black Magic Probe
- JLink
- ST-Link

To get started, download [vscode](https://code.visualstudio.com/) and install the following extensions:
- [Cortex-Debug](https://marketplace.visualstudio.com/items?itemName=marus25.cortex-debug)
- [C/C++ Tools](https://marketplace.visualstudio.com/items?itemName=ms-vscode.cpptools)

The generated environment assumes the following dependencies on PATH:
- [Python](https://www.python.org/) (>=3)
- [ARM Toolchain](https://developer.arm.com/tools-and-software/open-source-software/developer-tools/gnu-toolchain/gnu-rm/downloads)
- make (or [mingw32-make](https://osdn.net/projects/mingw/releases/) if Windows)
- [OpenOCD](https://xpack.github.io/openocd/install/) (if using st-link)
- [STM32CubeProgrammer](https://www.st.com/en/development-tools/stm32cubeprog.html) (if using flash task with st-link)
- [JLink Tools](https://www.segger.com/downloads/jlink/#J-LinkSoftwareAndDocumentationPack) (if using jlink)

## Usage
Clone this repo into your project directory and run `python setup.py --help` to see configuration options. The script performs the following actions:
- moves the `.clang-format` file into the project directory
- creates a `build` folder in the project directory
- creates the `.vscode` environment folder in the project directory and generates the following three files:
  - `c_cpp_properties.json` - contains the project defines and include path
  - `tasks.json` - contains a task to build the project (assumes makefile project) and a task to flash the target for the selected debugger. NOTE: Black Magic Probe and ST-Link require the serial port to be specified. A `find` task is generated which should be run once per debugger plug-in before debugging/flashing.
  - `launch.json` - contains debug configurations to either launch a debug session or attach to a target device using vscode's GDB wrapper.
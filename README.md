# pygame-ce-runtime

This project builds an arm64 runtime to distribute [pygame-ce][2] games. The
main goal is to run pygame-ce games on Linux based handheld game consoles.

The runtime is a portable Python virtual environment with all required
dependencies to run pygame-ce games packed as a SquashFS image. You can
distribute the runtime together with your game code as a single package.

## Requeriments

* Docker
* Docker compose
* make

## Build the runtime

    make build-runtime

The build process starts a Debian based arm64 Python container and runs the 
[`build-runtime.sh`](build-runtime.sh) script on it. The script will install
operational system dependencies required to run pygame-ce, create a Python 
virtual environment, install pygame-ce and pack the runtime into a SquashFS
image.

The output artifact is located at `build/pygame-ce_<PYGAME_VERSION>_python_<PYTHON_VERSION>.squashfs`.

## Using the runtime

The runtime must be shipped together with your game code. You will need a
script to mount the runtime, enable Python virtual environment and run your
python code using Python on the runtime. Example:

    mount pygame-ce_2.5.6_python_3.12.8.squashfs /runtime
    source /runtime/bin/activate
    export PYTHONHOME=/runtime
    export PYTHONPATH=/runtime/lib/python3.12
    /runtime/bin/python your_game.py

An example game and a [PortMaster][1] compatible startup script is located
at example folder. You don't need PortMaster but leveraging on it will make
your game run on any supported device. To generate an zip package with the
runtime, example game and startup script, run:

    make build-package

The output artifact is located at `build/MyGame.zip`. Unzip the artifact
on PortMaster directory of your CFW of choice and you are ready to play!

## Customize the runtime

You can customize the runtime by adding the following files to the `build` folder:

* `pre-install.sh`: script to run before the runtime is built
* `post-install.sh`: script to run after the runtime is built, right before it is packed into a SquashFS image
* `requirements.txt`: additional Python dependencies to install on the runtime

## Limitations

I built this project for my personal use, and testing is limited to my access
to different devices and CFW. The current runtime uses Python 3.12.8 and
pygame-ce 2.5.6, and was successfully tested on an Anbernic RG35XX-H device
running Knulli Gladiator.

Donations to acquire SD cards and other devices are welcome.

[1]: https://portmaster.games/index.html
[2]: https://github.com/pygame-community/pygame-ce

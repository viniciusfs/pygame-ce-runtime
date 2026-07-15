# pygame-ce-runtime

This project builds an arm64 runtime to distribute [pygame-ce][2] games. The
main goal is to run pygame-ce games on Linux based handheld game consoles.

The runtime is a portable Python virtual environment with all required
dependencies to run pygame-ce games packed as a SquashFS image. You can
distribute the runtime together with your game code as a single package.

## Download a prebuilt runtime

If you don't want to build the runtime yourself, prebuilt images are
published on the [releases page][3]. Each release ships two SquashFS
variants:

* `pygame-ce_<PYGAME_VERSION>_python_<PYTHON_VERSION>.squashfs` — compressed
  with **xz** (smaller). Use this if your device kernel supports it.
* `pygame-ce_<PYGAME_VERSION>_python_<PYTHON_VERSION>_gzip.squashfs` —
  compressed with **gzip**. Use this if mounting the xz image fails with a
  `wrong fs type / bad superblock` error, which usually means the kernel
  lacks xz SquashFS support.

The `MyGame.zip` package on each release bundles the xz runtime, the example
game and the PortMaster startup script.

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

The output artifacts are located in the `build` folder. One SquashFS image
is produced per compression listed in the `COMP` variable of
[`build-config`](build-config) (defaults to `xz gzip`); the xz image keeps
the un-suffixed name and other compressions get a `_<comp>` suffix. See
[Download a prebuilt runtime](#download-a-prebuilt-runtime) for when to use
each one.

### Choosing the base image

The Docker base image is set by the `BASE_IMAGE` variable in `build-config`.
It must be an official `python:<PYTHON_VERSION>-*` image, since the build
reuses the prebuilt Python it ships. The default is
`python:3.12.8-bullseye` (GLIBC 2.31), chosen because a runtime built
against an older GLIBC also runs on newer systems — this single image works
both on devices with an old libc (for example MinUI, GLIBC 2.33) and on
newer CFWs such as Knulli. If you specifically want to build against a newer
base you can override it:

    BASE_IMAGE=python:3.12.8-bookworm

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

You can customize the runtime by adding any of the following files to the
`custom` folder (already present in the repository):

* `pre-install.sh`: script to run before the runtime is built
* `post-install.sh`: script to run after the runtime is built, right before it is packed into a SquashFS image
* `requirements.txt`: additional Python dependencies to install on the runtime

For example, to bundle an extra Python dependency into the runtime:

    echo "requests==2.32.3" >> custom/requirements.txt
    make build-runtime

These files live in `custom/` (not `build/`) on purpose: `build/` only holds
generated artifacts and is wiped by `make clean`, while your customization
files in `custom/` are git-ignored and left untouched between builds.

## Limitations

I built this project for my personal use, and testing is limited to my access
to different devices and CFW. The current runtime uses Python 3.12.8 and
pygame-ce 2.5.6, and was successfully tested on an Anbernic RG35XX-H device
running Knulli Gladiator.

Donations to acquire SD cards and other devices are welcome.

[1]: https://portmaster.games/index.html
[2]: https://github.com/pygame-community/pygame-ce
[3]: https://github.com/viniciusfs/pygame-ce-runtime/releases

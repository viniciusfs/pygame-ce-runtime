#!/bin/bash
# PortMaster startup script example for pygame-ce runtime

PACKAGE="MyGame"
ENTRYPOINT="src/run.py"
RUNTIME="pygame-ce_2.5.6_python_3.12.8"

XDG_DATA_HOME=${XDG_DATA_HOME:-$HOME/.local/share}
export XDG_RUNTIME_DIR=/var/run
if [ ! -d "/var/run" ]; then
  mkdir -p "/var/run"
  chmod 700 "/var/run"
fi

if [ -d "/opt/system/Tools/PortMaster/" ]; then
  controlfolder="/opt/system/Tools/PortMaster"
elif [ -d "/opt/tools/PortMaster/" ]; then
  controlfolder="/opt/tools/PortMaster"
elif [ -d "$XDG_DATA_HOME/PortMaster/" ]; then
  controlfolder="$XDG_DATA_HOME/PortMaster"
else
  controlfolder="/roms/ports/PortMaster"
fi

source $controlfolder/control.txt
[ -f "${controlfolder}/mod_${CFW_NAME}.txt" ] && source "${controlfolder}/mod_${CFW_NAME}.txt"
get_controls

GAMEDIR="/$directory/ports/$PACKAGE"
cd "${GAMEDIR}"

> "${GAMEDIR}/log.txt" && exec > >(tee "${GAMEDIR}/log.txt") 2>&1

CONFDIR="$GAMEDIR/conf"
mkdir -p "$CONFDIR"
bind_directories "$HOME/.config/pygame-ce-runtime/$PACKAGE" "$CONFDIR"

export PYGAME_DIR="$HOME/pygame-ce-runtime"
mkdir -p "${PYGAME_DIR}"

if [[ "$PM_CAN_MOUNT" != "N" ]]; then
  $ESUDO umount "${PYGAME_DIR}"
fi

$ESUDO mount "$GAMEDIR/runtime/${RUNTIME}.squashfs" "${PYGAME_DIR}"

export SDL_GAMECONTROLLERCONFIG="$sdl_controllerconfig"
$GPTOKEYB "python" &

pm_platform_helper "${PYGAME_DIR}/bin/python"

source "${PYGAME_DIR}/bin/activate"
export PYTHONHOME="${PYGAME_DIR}"
export PYTHONPATH="${PYTHONHOME}/lib/python3.12"
export PYTHONPYCACHEPREFIX="${GAMEDIR}/${RUNTIME}.cache"

export SDL_VIDEODRIVER=mali # compatible with anbernic rg35xx-h

"${PYGAME_DIR}/bin/python" "${GAMEDIR}/${ENTRYPOINT}"

if [[ "$PM_CAN_MOUNT" != "N" ]]; then
  $ESUDO umount "${PYGAME_DIR}"
fi

pm_finish

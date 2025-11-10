#!/usr/bin/env bash

: "${PYTHON_VERSION:?PYTHON_VERSION is required}"
: "${PYGAME_VERSION:?PYGAME_VERSION is required}"

export PY_VER=${PYTHON_VERSION%.*}

cd $HOME

# install dependencies
apt update && apt install -y build-essential git rsync squashfs-tools \
  libfreetype6-dev libportmidi-dev python3-dev python3-numpy \
  libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev

# run pre-install script
if [[ -f /local/build/pre-install.sh ]]; then
  bash /local/build/pre-install.sh
fi

# create runtime
python -m venv --copies /runtime
source /runtime/bin/activate
git clone --branch ${PYGAME_VERSION} https://github.com/pygame-community/pygame-ce.git
cd pygame-ce && python -m pip install .

# install additional requirements
if [[ -f /local/build/requirements.txt ]]; then
  python -m pip install -r /local/build/requirements.txt
fi

deactivate

# copy python library
cp /usr/local/lib/libpython${PY_VER}.so.1.0 /runtime/lib/
rsync -av /usr/local/lib/python${PY_VER}/ /runtime/lib/python${PY_VER}/
find /runtime -name "__pycache__" -type d -exec rm -rf {} +

# run post-install script
if [[ -f /local/build/post-install.sh ]]; then
  bash /local/build/post-install.sh
fi

# create squashfs from runtime
mksquashfs /runtime /pygame-ce_${PYGAME_VERSION}_python_${PYTHON_VERSION}.squashfs -comp xz -b 1M
mv /pygame-ce_${PYGAME_VERSION}_python_${PYTHON_VERSION}.squashfs /local/build/pygame-ce_${PYGAME_VERSION}_python_${PYTHON_VERSION}.squashfs

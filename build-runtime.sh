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
if [[ -f /local/custom/pre-install.sh ]]; then
  bash /local/custom/pre-install.sh
fi

# create runtime
python -m venv --copies /runtime
source /runtime/bin/activate
git clone --branch ${PYGAME_VERSION} https://github.com/pygame-community/pygame-ce.git
cd pygame-ce && python -m pip install .

# install additional requirements
if [[ -f /local/custom/requirements.txt ]]; then
  python -m pip install -r /local/custom/requirements.txt
fi

deactivate

# copy python library
cp /usr/local/lib/libpython${PY_VER}.so.1.0 /runtime/lib/
rsync -av /usr/local/lib/python${PY_VER}/ /runtime/lib/python${PY_VER}/
find /runtime -name "__pycache__" -type d -exec rm -rf {} +

# run post-install script
if [[ -f /local/custom/post-install.sh ]]; then
  bash /local/custom/post-install.sh
fi

# create one squashfs image per compression listed in COMP.
# xz is smallest; gzip is more compatible with limited device kernels.
mkdir -p /local/build
COMP="${COMP:-xz}"
for comp in $COMP; do
  # keep the historical xz image un-suffixed for backward compatibility
  suffix=""
  if [[ "$comp" != "xz" ]]; then
    suffix="_${comp}"
  fi
  name="pygame-ce_${PYGAME_VERSION}_python_${PYTHON_VERSION}${suffix}.squashfs"
  mksquashfs /runtime "/${name}" -comp "${comp}" -b 1M -noappend
  mv "/${name}" "/local/build/${name}"
done

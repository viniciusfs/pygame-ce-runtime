#!/usr/bin/env bash

cd $HOME

apt update && apt install -y build-essential git rsync squashfs-tools \
  libfreetype6-dev libportmidi-dev python3-dev python3-numpy \
  libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev

python -m venv /runtime
source /runtime/bin/activate

git clone --branch 2.5.6 https://github.com/pygame-community/pygame-ce.git
cd pygame-ce && python -m pip install .

rm /runtime/bin/python
cp /usr/local/bin/python /runtime/bin/python
cp /usr/local/lib/libpython3.12.so.1.0 /runtime/lib/
rsync -av /usr/local/lib/python3.12/ /runtime/lib/python3.12/
find /runtime -name "__pycache__" -type d -exec rm -rf {} +

deactivate

mksquashfs /runtime /local/build/pygame-ce_2.5.6_python_3.12.8.squashfs -comp xz -b 1M

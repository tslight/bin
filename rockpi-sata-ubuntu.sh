#!/bin/bash
AUTHOR='Akgnah <setq@radxa.com>'
VERSION='0.14'
PI_MODEL=`tr -d '\0' < /proc/device-tree/model`
RPI_DEB="https://s3.setq.io/rockpi/deb/raspi-sata-${VERSION}.deb"
SSD1306="https://s3.setq.io/rockpi/pypi/Adafruit_SSD1306-v1.6.2.zip"
PIG_ZIP="https://s3.setq.io/rockpi/tar/pigpio-v77.zip"

confirm() {
  printf "%s [Y/n] " "$1"
  read resp < /dev/tty
  if [ "$resp" == "Y" ] || [ "$resp" == "y" ] || [ "$resp" == "yes" ]; then
    return 0
  fi
  if [ "$2" == "abort" ]; then
    echo -e "Abort.\n"
    exit 0
  fi
  return 1
}

apt_check() {
  packages="python3-rpi.gpio python3-setuptools python3-pip python3-pil python3-dev python3-pigpio make gcc unzip net-tools"
  need_packages=""

  idx=1
  for package in $packages; do
    if ! apt list --installed 2> /dev/null | grep "^$package/" > /dev/null; then
      pkg=$(echo "$packages" | cut -d " " -f $idx)
      need_packages="$need_packages $pkg"
    fi
    ((++idx))
  done

  if [ "$need_packages" != "" ]; then
    echo -e "\nPackage(s) $need_packages is required.\n"
    confirm "Would you like to apt-get install the packages?" "abort"
    apt-get update
    apt-get install --no-install-recommends $need_packages -y
  fi
}

deb_install() {
  TEMP_DEB="$(mktemp)"
  curl -sL "$RPI_DEB" -o "$TEMP_DEB"
  dpkg -i "$TEMP_DEB"
  rm -f "$TEMP_DEB"
}

dtb_enable() {
  ln -sf /boot/firmware/usercfg.txt /boot/config.txt
  python3 /usr/bin/rockpi-sata/misc.py open_w1_i2c
}

pig_install() {
  TEMP_ZIP="$(mktemp)"
  TEMP_DIR="$(mktemp -d)"
  curl -sL "$PIG_ZIP" -o "$TEMP_ZIP"
  unzip "$TEMP_ZIP" -d "$TEMP_DIR" > /dev/null
  make -C "${TEMP_DIR}/pigpio-v77"
  make -C "${TEMP_DIR}/pigpio-v77" install
  rm -rf "$TEMP_ZIP" "$TEMP_DIR"

cat > /lib/systemd/system/pigpiod.service << EOF
[Unit]
Description=Daemon required to control GPIO pins via pigpio
[Service]
ExecStart=/usr/local/bin/pigpiod -l
ExecStop=/bin/systemctl kill pigpiod
Type=forking
[Install]
WantedBy=multi-user.target
EOF
}

pip_fixpath() {
  path="/usr/local/lib/python$(python3 -V | cut -c8-10)/dist-packages"
  if [ ! -d $path ]; then
    mkdir -p $path
  fi
}

pip_install() {
  pip_fixpath

  TEMP_ZIP="$(mktemp)"
  TEMP_DIR="$(mktemp -d)"
  curl -sL "$SSD1306" -o "$TEMP_ZIP"
  unzip "$TEMP_ZIP" -d "$TEMP_DIR" > /dev/null
  cd "${TEMP_DIR}/Adafruit_SSD1306-v1.6.2/"
  python3 setup.py install && cd -
  rm -rf "$TEMP_ZIP" "$TEMP_DIR"
}

main() {
  if [[ "$PI_MODEL" =~ "Raspberry" ]]; then
    apt_check
    pip_install
    pig_install
    deb_install
    dtb_enable
  else
    echo 'nothing'
  fi
}

main

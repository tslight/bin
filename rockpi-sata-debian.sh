#!/bin/bash
AUTHOR='Akgnah <setq@radxa.com>'
VERSION='0.10'
PI_MODEL=`tr -d '\0' < /proc/device-tree/model`
PI_DEB="https://s3.setq.io/rockpi/deb/rockpi-penta-${VERSION}.deb"
SSD1306="https://s3.setq.io/rockpi/pypi/Adafruit_SSD1306-v1.6.2.zip"

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
  packages="libmraa rockpi4-dtbo unzip gcc python3-dev python3-setuptools python3-pip python3-pil"
  need_packages="`echo ${PI_MODEL,,} | tr -d '[:space:]'`-rk-u-boot-latest"

  if [[ "$PI_MODEL" =~ '4C+' ]]; then
    need_packages=""
  fi

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
    apt-get install --no-install-recommends $need_packages -y < /dev/tty
  fi
}

deb_install() {
  TEMP_DEB="$(mktemp)"
  curl -sL "$PI_DEB" -o "$TEMP_DEB"
  dpkg -i "$TEMP_DEB"
  rm -f "$TEMP_DEB"
}

dtb_enable() {
  python3 /usr/bin/rockpi-penta/misc.py open_pwm_i2c
}

pip_install() {
  TEMP_ZIP="$(mktemp)"
  TEMP_DIR="$(mktemp -d)"
  curl -sL "$SSD1306" -o "$TEMP_ZIP"
  unzip "$TEMP_ZIP" -d "$TEMP_DIR" > /dev/null
  cd "${TEMP_DIR}/Adafruit_SSD1306-v1.6.2"
  python3 setup.py install && cd -
  rm -rf "$TEMP_ZIP" "$TEMP_DIR"
}

main() {
  if [[ "$PI_MODEL" =~ "ROCK" ]]; then
    apt_check
    pip_install
    deb_install
    dtb_enable
  else
    echo 'nothing'
  fi
}

main

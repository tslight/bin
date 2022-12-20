#!/bin/bash
AUTHOR='Akgnah <setq@radxa.com>'
VERSION='0.14'
MODEL=`tr -d '\0' < /proc/device-tree/model`
DISTRO=`cat /etc/os-release | grep ^ID= | sed -e 's/ID\=//g'`
#
# quad-sata-hat install script
#
RASPBIAN_URL='https://s3.setq.io/rockpi/sh/quad-sata/raspbian.sh'
UBUNTU_URL='https://s3.setq.io/rockpi/sh/quad-sata/ubuntu.sh'
DEBIAN_PLUS='https://cos.setf.me/rockpi/sh/penta-sata/debian.sh'

echo
echo '*** Quad SATA Hat Install for Raspberry Pi 3B+/4B+'
echo
echo '*** Tested distributions:'
echo '***   Raspbian buster 32-bit/64-bit(testing)'
echo '***   Ubuntu Server 20.04 armhf and arm64'
echo
echo '*** Please report problems to setq@radxa.com and we will try to fix.'
echo

if [[ "$MODEL" =~ '4C+' ]]; then
  curl -sL $DEBIAN_PLUS | sudo -E bash -
elif [ -f /etc/rpi-issue ]; then
  curl -sL $RASPBIAN_URL | sudo -E bash -
elif [ "$DISTRO" == "raspbian" ]; then
  curl -sL $RASPBIAN_URL | sudo -E bash -
elif [ "$DISTRO" == "ubuntu" ]; then
  curl -sL $UBUNTU_URL | sudo -E bash -
else
  echo '*** The script is not available on your system'
  echo '*** Please visit https://rock.sh/rockpi-sata to download and install manually.'
  exit 0
fi

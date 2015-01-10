# Flashing HDMI2USB VID:PID into Atlys board

A brand new Atlys Board gets listed by `lsusb` as 'Digilent Development board JTAG' with VID:PID as 1443:0007
We want to flash the EEPROM onboard the Atlys, so that on powering up, it always shows up as "OpenMoko Device, TimVideos' HDMI2USB (FX2) - Unconfigured device" with VID:PID as 1D50:60B5

## Steps:

  *  Change to flcli executable directory. If you are in directory of this file use this command:

        `cd ../../../../../apps/flcli/lin.x86/dbg`


  *  Now use this command to flash the Atlys' EEPROM

        `sudo ./flcli -v 1D50:60B5 -i 1443:0007 --eeprom=../../../../libs/libfpgalink/firmware/fx2/eeprom/hdmi2usb_unconfigured_device.iic`

Thats it!! You have flashed your Atlys to appear as different device. Power cycle the board and use lsusb to confirm

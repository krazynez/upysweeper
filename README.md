## µpysweeper

<p style="text-decoration: underline;">pysweeper without a GUI</p>


[upysweeper.webm](https://github.com/krazynez/upysweeper/assets/39999447/4c89660e-a884-4c87-b0d7-9eb16161cb8d)



<p><b>Note:</b> If the serial output dumps to screen and you get a green light then no light just turn your PSP over and with the power cable still plugged in turn on the PSP. It should autoboot into Despertar del Cementerio</p>

<br>

## Setup & Install

1. Make sure you have `pyserial` and `pycryptodome` installed.

    1. `pip install -r requirements.txt`

2. `python3 ./upysweeper.py` or `./upysweeper.py`


##### Options:
    ./upysweeper.py -p SERIAL_PORT -bt BATTERY_TYPE

    example:
        ./upysweeper.py -p /dev/ttyUSB0 -bt Autoboot 


##### Battery types
 - "Service" which is `0xFFFFFFFF` and set as default

 - "Autoboot" which is `0x00000000`

 - "Normal" which is `0x34127856` (just random)

 - "Custom" `0x12345678` or `12345678`  allow custom serial to be used

##### Embedded flag

* `-e` if defined will just be set to true

* This is to tell upysweeper to not run a test for an echo it has been only tested on the Milk-V Duo with a custom image.

* PIN GP2 (RX) _schematic(PIN 5)_ 

* PIN GP3 (TX) _schematic (PIN 4)_


![img](https://milkv.io/assets/images/pinout-c46d0577677fbfe3695fde269cbc37ac.webp)


### Original work

<ul>
<li><a href="https://github.com/khubik2/pysweeper">khubik2's pysweeper repo</p></li>
</ul>

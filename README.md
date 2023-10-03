## µpysweeper

<p>pysweeper without a GUI</p>




## Setup & Install

1. Make sure you have `pyserial` and `pycryptodome` installed.

    1. `pip install -r requirements.txt`

2. `python3 ./upysweeper.py` or `./upysweeper.py`


##### Options:
    ./upysweeper.py -p SERIAL_PORT -bt BATTERY_TYPE

    example:
        ./upysweeper.py -p /dev/ttyUSB0 -bt Autoboot 


##### Battery types
 - Default Battery type is service mode `0xFFFFFFFF`

 - "Autoboot" which is `0x00000000`

 - "Normal" which is `0x34127856` (just random)

 - "Custom" `0x12345678` or `12345678`  allow custom serial to be used 


### Original work

<ul>
<li><a href="https://github.com/khubik2/pysweeper">khubik2's pysweeper repo</p></li>
</ul>

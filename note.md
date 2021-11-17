# design overview
![ioexpander-12bit](https://user-images.githubusercontent.com/9379328/141942652-2a314a86-7227-4a5d-a972-0f51ffb5c1e4.png)

| Pin | QFN | TSSOP |VDD Rail| Function |Pin assign changeable|
|---|---|---|---|---|---|
|VDD|1 |20 |VDD | VDD|N|
|VDD2|14 |7 |VDD2 | VDD2|N|
|GND|11 |10 |GND | GND |N|
|SDA|9 |12 |VDD | I2C SDA|N|
|SCL|8 |13 |VDD | I2C SDL|N|
|IO0|2 |19 |VDD | Port0 bit0|Y|
|IO1|3 |18 |VDD | Port0 bit1|Y|
|IO2|4 |17 |VDD | Port0 bit2|Y|
|IO3|5 |16 |VDD | Port0 bit3|Y|
|IO4|6 |15 |VDD |Slave address selection 2 (bit6 (8-bit addressing))|Y[^1]/N|
|IO5|7 |14 |VDD |Slave address selection 3 (bit7 (8-bit addressing))|Y[^1]/N|
|IO6|10 |11 |VDD | Unused; leave open|Y|
|IO7|12 |9 |VDD2 | Port0 bit4|Y|
|IO8|13 |8 |VDD2 | Port0 bit5|Y|
|IO9|15 |6 |VDD2 | Port1 bit5|Y|
|IO10|16 |5 |VDD2 | Port1 bit4|Y|
|IO11|17 |4 |VDD2 | Port1 bit3|Y|
|IO12|18 |3 |VDD2 | Port1 bit2|Y|
|IO13|19 |2 |VDD2 | Port1 bit1|Y|
|IO14|20 |1 |VDD2 | Port1 bit0|Y|

[^1]: when there is no problem to have less slave address choices, it can be up to 2-port 7-bit GPO expander, or 2-port 6-bit multi rail GPO expander. up to you :)

# I2c slave addresses

`SLA_3/GPIO5` and `SLA_2/GPIO4` pins are internally  pulled down, address select pins.
As this is an SLG46826 design the chip reserves 4 address per selection.

|SLA_3 | SLA_2 | *7-bit* Addresses | *8-bit* Addresses |
|---|----|----|---|
|0 | 0 | **`0x08`** `0x09` `0x0a` `0x0b` | **`0x10`** `0x12` `0x14` `0x16` |
|0 | 1 | **`0x28`** `0x29` `0x2a` `0x2b` | **`0x50`** `0x52` `0x54` `0x56` |
|1 | 0 | **`0x48`** `0x49` `0x4a` `0x4b` | **`0x90`** `0x92` `0x94` `0x96` |
|1 | 1 | **`0x68`** `0x69` `0x6a` `0x6b` | **`0xD0`** `0xD2` `0xD4` `0xD6` |

# Registers to use

register `0x7A` is to send IO state for both P0 and P1. MSB 2 bits are port selector bits.

`0x76[7:2]` is to read P0 _output_ state. `0x79[5:0]` is to read P1 _output_ state.

|register | bit | purpose |
|---|---|---|
|`0x76` | 7 | read P05 |
| | 6 | P04 |
| | 5 | P03 |
| | 4 | P02 |
| | 3 | P01 |
| | 2 | P00 |
| | 1..0 | reserved |
|`0x79` | 7..6 | reserved |
| | 5 | read P15 |
| | 4 | P14 |
| | 3 | P13 |
| | 2 | P12 |
| | 1 | P11 |
| | 0 | P10 |
|`0x7A` | 7..6 | port selection |
| | |`00` : P0 |
| | |`01` : P1 |
| | |`1x` : reserved |
| | 5 | write bit5 |
| | 4 | bit4 |
| | 3 | bit3 |
| | 2 | bit2 |
| | 1 | bit1 |
| | 0 | bit0 |

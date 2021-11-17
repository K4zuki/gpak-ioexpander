# design overview
![ioexpander-12bit](https://user-images.githubusercontent.com/9379328/141942652-2a314a86-7227-4a5d-a972-0f51ffb5c1e4.png)

| Pin | QFN | TSSOP |Function| VDD Rail|
|---|---|---|---|---|
|VDD|1 |20 |VDD | VDD|
|VDD2|14 |7 |VDD2 | VDD2|
|GND|11 |10 |GND | GND |
|SDA|9 |12 |VDD | I2C SDA|
|SCL|8 |13 |VDD | I2C SDL|
|IO0|2 |19 |VDD | Port0 bit0|
|IO1|3 |18 |VDD | Port0 bit1|
|IO2|4 |17 |VDD | Port0 bit2|
|IO3|5 |16 |VDD | Port0 bit3|
|IO4|6 |15 |VDD |Slave address selection 2 (bit6 (8-bit addressing))|
|IO5|7 |14 |VDD |Slave address selection 3 (bit7 (8-bit addressing))|
|IO6|10 |11 |VDD | Unused; leave open|
|IO7|12 |9 |VDD2 | Port0 bit4|
|IO8|13 |8 |VDD2 | Port0 bit5|
|IO9|15 |6 |VDD2 | Port1 bit5|
|IO10|16 |5 |VDD2 | Port1 bit4|
|IO11|17 |4 |VDD2 | Port1 bit3|
|IO12|18 |3 |VDD2 | Port1 bit2|
|IO13|19 |2 |VDD2 | Port1 bit1|
|IO14|20 |1 |VDD2 | Port1 bit0|

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

# Ideas
## lose slave address choice/tricky software requirement vs. multi rail/extend bit width

If you dont mind to lose slave address, one may use IO4 and 5 for output pins for Port0. This change allows to have one more
bit per port, also have different VDD levels for each port i.e. Port0 uses VDD while Port1 is VDD2 level
(keep VDD >= VDD2 relationship!).
But when this idea is applied, output state reading registers and bit assignment will be different so that driver software will be a bit tricky.

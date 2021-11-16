# design overview
![ioexpander-12bit](https://user-images.githubusercontent.com/9379328/141942652-2a314a86-7227-4a5d-a972-0f51ffb5c1e4.png)

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
|`0x76` | 7 | P05 |
| | 6 | P04 |
| | 5 | P03 |
| | 4 | P02 |
| | 3 | P01 |
| | 2 | P00 |
| | 1..0 | reserved |
|`0x79` | 7..6 | reserved |
| | 5 | P15 |
| | 4 | P14 |
| | 3 | P13 |
| | 2 | P12 |
| | 1 | P11 |
| | 0 | P10 |
|`0x7A` | 7..6 | port selection |
| | |`00` : P0 |
| | |`01` : P1 |
| | |`1x` : reserved |
| | 5 | bit5 |
| | 4 | bit4 |
| | 3 | bit3 |
| | 2 | bit2 |
| | 1 | bit1 |
| | 0 | bit0 |

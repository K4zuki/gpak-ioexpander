from smbus2 import SMBus, i2c_msg
import time

ioexpander_address = 0x08  # 7-bit addressing
WRITE_REG = 0x7A
P0_REG = 0x76
P1_REG = 0x79


class Bit:
    val = 0

    def __init__(self, read, write):
        self.reading_bit = read
        self.writing_bit = write


class Port:
    write_address = WRITE_REG
    read_address = 0
    mask = 0
    bit0 = Bit(0, 0)
    bit1 = Bit(1, 1)
    bit2 = Bit(2, 2)
    bit3 = Bit(3, 3)
    bit4 = Bit(4, 4)
    bit5 = Bit(5, 5)

    def __init__(self, _bus, address):
        self.address = address
        self.bus = _bus
        self.bits = [self.bit0,
                     self.bit1,
                     self.bit2,
                     self.bit3,
                     self.bit4,
                     self.bit5]

    def get_bit(self, bit):
        assert 6 > bit >= 0
        return self.bits[bit].val

    def set_bit(self, bit, value):
        assert 6 > bit >= 0
        self.bits[bit].val = value

    def send(self):

        self.bits = [self.bit0,
                     self.bit1,
                     self.bit2,
                     self.bit3,
                     self.bit4,
                     self.bit5]

        data = 0
        for _bit in self.bits:
            data = data | (_bit.val << _bit.writing_bit)
        data = (data & 0x3F) | (self.mask << 6)
        clock = data | 0xC0

        msg_clock = i2c_msg.write(self.address, [self.write_address, clock])
        msg_data = i2c_msg.write(self.address, [self.write_address, data])

        self.bus.i2c_rdwr(msg_clock, msg_data)
        self.bus.i2c_rdwr(msg_clock)

    def write(self, data):
        assert 256 > data >= 0
        [self.set_bit(sft, 0x01 & (data >> sft)) for sft in range(6)]
        self.send()

    def read(self):
        data = self.bus.read_byte_data(self.address, self.read_address)
        for bit in self.bits:
            bit.val = 0x01 & (data >> bit.reading_bit)
        return data


class Mux:
    def __init__(self, bus, address):
        self.address = address
        self.bus = bus  # type: SMBus

        self.port0 = Port(self.bus, self.address)
        self.port0.read_address = P0_REG
        self.port0.mask = 1
        self.port0.bit0 = Bit(2, 0)
        self.port0.bit1 = Bit(3, 1)
        self.port0.bit2 = Bit(4, 2)
        self.port0.bit3 = Bit(5, 3)
        self.port0.bit4 = Bit(6, 4)
        self.port0.bit5 = Bit(7, 5)

        self.port1 = Port(self.bus, self.address)
        self.port1.read_address = P1_REG
        self.port1.mask = 2

        self.cross_points = {
            1: {  # ROW
                1: (self.port1, 0),  # COL
                2: (self.port1, 2),
                3: (self.port1, 4),
                4: (self.port0, 1),
                5: (self.port0, 3),
                6: (self.port0, 5),
            },
            2: {  # ROW
                1: (self.port1, 1),  # COL
                2: (self.port1, 3),
                3: (self.port1, 5),
                4: (self.port0, 4),
                5: (self.port0, 2),
                6: (self.port0, 0),
            }
        }

    def connect(self, row, column):
        port, bit = self.cross_points[row][column]
        port.set_bit(bit, 1)
        port.send()

    def disconnect(self, row, column):
        port, bit = self.cross_points[row][column]
        port.set_bit(bit, 0)
        port.send()

    def disconnect_all(self):
        self.port0.write(0x00)
        self.port1.write(0x00)


def main():
    with SMBus(1) as bus:
        mux = Mux(bus, ioexpander_address)
        for row in [1, 2]:
            for col in [1, 2, 3, 4, 5, 6]:
                print("connect", row, col)
                mux.connect(row, col)
                time.sleep(0.5)
                print("disconnect", row, col)
                mux.disconnect(row, col)
                time.sleep(0.5)


if __name__ == '__main__':
    main()

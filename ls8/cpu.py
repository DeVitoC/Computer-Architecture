"""CPU functionality."""

import sys

HLT = 1


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.sp = len(self.ram) - 1
        self.instructions = {
            0b10000010: self.ldi,
            0b01000111: self.prn,
            0b10100010: self.alu,
            0b10100000: self.alu,
            HLT: self.hlt,
            0b01000101: self.push,
            0b01000110: self.pop,
            0b01010000: self.call,
            0b00010001: self.ret,
        }

    def load(self):
        """Load a program into memory."""

        address = 0
        program = []

        with open(sys.argv[1], 'r') as reader:
            line = reader.readline()
            while line != "":
                words = line.split(" ")
                num_str = f"0b{words[0]}"
                num = int(num_str, 2)
                program.append(num)
                line = reader.readline()

        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def alu(self, reg_a, reg_b, op):
        """ALU operations."""

        if op == 0b10100000:
            self.reg[reg_a] += self.reg[reg_b]
        if op == 0b10100010:
            self.ram[reg_a] *= self.ram[reg_b]
        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        while True:
            ir = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            self.instructions[ir](operand_a, operand_b, ir)

            instruct = ((ir & 0b11000000) >> 6) + 1
            self.pc += instruct

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, value, address):
        self.ram[address] = value

    def ldi(self, address, value, *args):
        self.ram_write(value, address)

    def prn(self, address, *args):
        print(f"{self.ram_read(address)}")

    def hlt(self, *args):
        sys.exit()

    def push(self, address, *args):
        self.sp -= 1
        self.ram[self.sp] = self.ram[address]
        # self.sp -= 1

    def pop(self, address, *args):
        # self.sp += 1
        self.ram[address] = self.ram[self.sp]
        self.sp += 1

    def call(self, address, *args):
        pass

    def ret(self, address, *args):
        pass

    def jmp(self, address, *args):
        self.pc = address
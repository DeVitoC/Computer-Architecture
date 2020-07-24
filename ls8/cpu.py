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
        self.fl = 0 # LGE
        self.reg[7] = 0xF4
        self.instructions = {
            0b10000010: self.ldi, # Load
            0b01000111: self.prn, # Print
            0b10100010: self.alu, # Multiply
            0b10100000: self.alu, # ADD
            0b10101000: self.alu, # AND
            0b01100110: self.alu, # Decrement
            0b10100011: self.alu, # Divide
            0b01100101: self.alu, # Increment
            0b10100100: self.alu, # Modulo (division remainder)
            0b01101001: self.alu, # NOT binary operation
            0b10101010: self.alu, # OR binary operation
            0b10101100: self.alu, # Shift Left
            0b10101101: self.alu, # Shift Right
            0b10100001: self.alu, # Subtract
            0b10101011: self.alu, # Binary XOR
            HLT: self.hlt, # Halt
            0b01000101: self.push, # Push to stack
            0b01000110: self.pop, # Pop from stack
            0b01010000: self.call, # Call subroutine
            0b00010001: self.ret, # Return
            0b10100111: self.cmp, # Compare equal or greater/lesser
            0b01010010: self.int, # Interrupt
            0b00010011: self.iret, # Interrupt return
            0b01010101: self.jeq, # Jump if equal
            0b01011010: self.jge, # Jump if greater or equal
            0b01010111: self.jgt, # Jump if greater than
            0b01011001: self.jle, # Jump if less than or equal
            0b01011000: self.jlt, # Jump if less than
            0b01010110: self.jne, # Jump if not equal
            0b01010100: self.jmp, # Jump
            0b10000011: self.ld, # Load
            0b00000000: self.nop, # No operation
            0b01001000: self.pra, # Print alpha character
            0b10000100: self.st, # Store contents of second register in first
        }

    def load(self):
        """Load a program into memory."""

        address = 0
        program = []

        with open(sys.argv[1], 'r') as reader:
            line = reader.readline()
            while line != "":
                words = line.split(" ")
                first_word = words[0].rstrip()
                if not first_word.isnumeric():
                    line = reader.readline()
                    continue
                num_str = f"0b{first_word}"
                num = int(num_str, 2)
                program.append(num)
                line = reader.readline()

        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def alu(self, reg_a, reg_b, op):
        """ALU operations."""

        if op == 0b10100000: # Addition
            self.reg[reg_a] += self.reg[reg_b]
        elif op == 0b10100010: # Multiplication
            self.ram[reg_a] *= self.ram[reg_b]
        elif op == 0b10101000: # AND Binary operation
            self.ram[reg_a] = self.ram[reg_a] & self.ram[reg_b]
        elif op == 0b01100110: # Decrement
            self.ram[reg_a] -= 1
        elif op == 0b10100011: # Divide
            if self.ram[reg_b] == 0:
                print("Cannot divide by 0")
                self.hlt()
            self.ram[reg_a] = self.ram[reg_a] // self.ram[reg_b]
        elif op == 0b01100101: # Increment
            self.ram[reg_a] += 1
        elif op == 0b10100100: # Modulo
            self.ram[reg_a] % self.ram[reg_b]
        elif op == 0b01101001: # NOT Binary operation
            self.ram[reg_a] = ~self.ram[reg_a]
        elif op == 0b10101010: # OR binary operation
            self.ram[reg_a] = self.ram[reg_a] | self.ram[reg_b]
        elif op == 0b10101100: # Binary shift left
            self.ram[reg_a] = self.ram[reg_a] << self.ram[reg_b]
        elif op == 0b10101101: # Binary shift Right
            self.ram[reg_a] = self.ram[reg_a] >> self.ram[reg_b]
        elif op == 0b10100001: # Subtract
            self.ram[reg_a] -= self.ram[reg_b]
        elif op == 0b10101011: # Binary XOR
            self.ram[reg_a] = self.ram[reg_a] ^ self.ram[reg_b]
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

            instruct = ((ir & 0b11000000) >> 6) + 1
            self.pc += instruct
            self.instructions[ir](operand_a, operand_b, ir)



    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, value, address):
        self.ram[address] = value

    def ldi(self, address, value, *args):
        # self.ram_write(value, address)
        self.reg[address] = value

    def prn(self, address, *args):
        print(f"{self.reg[address]}")

    def hlt(self, *args):
        sys.exit()

    def push(self, address, *args):
        self.reg[7] -= 1
        self.ram[self.reg[7]] = self.reg[address]

    def pop(self, address, *args):
        self.reg[address] = self.ram[self.reg[7]]
        self.reg[7] += 1

    def call(self, address, *args):
        return_to = self.pc + 2
        self.push(return_to)
        self.pc = self.ram[self.pc + 1]

    def ret(self, address, *args):
        self.pop(address)
        self.pc = self.ram[address]

    def jmp(self, address, *args):
        self.pc = self.reg[address]

    def cmp(self, address1, address2, *args):
        if self.reg[address1] == self.reg[address2]:
            self.fl = 0b00000001
        elif self.reg[address1] < self.reg[address2]:
            self.fl = 0b00000100
        elif self.reg[address1] > self.reg[address2]:
            self.fl = 0b00000010

    def int(self, address, *args):
        pass

    def iret(self, *args):
        pass

    def jeq(self, address, *args):
        if self.fl == 0b00000001:
            self.jmp(address)

    def jge(self, address, *args):
        if self.fl == 0b00000001 or self.fl == 0b00000010:
            self.jmp(address)

    def jgt(self, address, *args):
        if self.fl == 0b00000010:
            self.jmp(address)

    def jle(self, address, *args):
        if self.fl == 0b00000100 or self.fl == 0b00000001:
            self.jmp(address)

    def jlt(self, address, *args):
        if self.fl == 0b00000100:
            self.jmp(address)

    def jne(self, address, *args):
        if self.fl != 0b00000001:
            self.jmp(address)

    def ld(self, address1, address2, *args):
        self.ram_write(address1, address2)

    def nop(self, *args):
        return

    def pra(self, address, *args):
        pass

    def st(self, address1, address2, *args):
        self.reg[address1] = self.reg[address2]



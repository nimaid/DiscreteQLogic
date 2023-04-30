#!/usr/bin/env python3

from enum import Enum

import helpers
import assembler


# ~~~~~~~~ Start Hardware Definition ~~~~~~~~
# A class to implement an ALU object
class ALU:
    def __init__(self, bits):
        # Bit width
        self.bits = bits
        
        # Flag bits out
        self.cout = None
        self.eqz = None
        self.nez = None
        self.ltz = None
        self.gtz = None
        self.lez = None
        self.gez = None
        
        # Unset status
        self.unset = True
    
    
    # A class to implement the ALU operations
    class Instruction(Enum):
        ADD = 0
        NAND = 1
    
    
    def invert(self, X):
        # Overflow inputs if needed
        X %= 2 ** self.bits
        
        # Get binary string
        binstring = "{0:b}".format(X)
        
        # Invert each bit
        out = ""
        for bit in binstring:
            if bit == "0":
                out += "1"
            else:
                out += "0"
        
        # Pad with 1's to fill the zeros that were missing at the start
        out = out.rjust(self.bits, "1")
        
        # Convert back to an integer
        out = int(out, 2)
        
        return out
    
    
    def add(self, A, B, cin):
        # Overflow inputs if needed
        A %= 2 ** self.bits
        B %= 2 ** self.bits
        
        # Take the sum
        sum = A + B
        
        # Add the carry in
        if cin:
            sum += 1
        
        # Test if we have a carry out
        if sum >= 2 ** self.bits:
            cout = True
        else:
            cout = False
        
        # Overflow the output
        sum %= 2 ** self.bits
        
        return sum, cout
    
    
    def calc(self, f, X, Y, cin=False):
        # Overflow inputs if needed
        X %= 2 ** self.bits
        Y %= 2 ** self.bits
        
        
        # Convert `f` to bool if needed
        if type(f) is not bool:
            command = f
            if command == self.Instruction.ADD:
                f = True
            elif command == self.Instruction.NAND:
                f = False
            else:
                raise Exception("\"{}\" is not a valid ALU command!".format(command))
        
        # Add to get the carry no matter what
        sum, cout = self.add(X, Y, cin)
        
        # Select output
        if f:
            # Add
            out = sum
        else:
            # NAND
            out = self.invert(X & Y)
        
        # Set flags
        self.cout = cout
        
        self.eqz = (out == 0)
        self.nez = (not self.eqz)
        
        self.ltz = (out >= (2** (self.bits - 1) ))
        self.gez = (not self.ltz)
        
        
        self.lez = (self.ltz or self.eqz)
        self.gtz = (not self.lez)
        
        if self.unset:
            self.unset = False
        
        return out
    
    
    def bit_width(self):
        return self.bits
    
    
    def flags(self):
        if self.unset:
            raise Exception("ALU has not had any calculations run yet, no flags available!")
        return {"cout" : self.cout,
                "eqz"  : self.eqz,
                "nez"  : self.nez,
                "ltz"  : self.ltz,
                "gtz"  : self.gtz,
                "lez"  : self.lez,
                "gez"  : self.gez}



# A class to implement a simple register
class Register:
    def __init__(self, bits):
        self.bits = bits
        
        self.value = None
        
        # Unset status
        self.unset = True
    
    
    def set(self, value):
        # Overflow inputs if needed
        value %= 2 ** self.bits
        
        self.value = value
        
        if self.unset:
            self.unset = False
    
    
    def get(self):
        if self.unset:
            raise Exception("The register has not been set yet, no value to get!")
        
        return self.value



# A class to implement a RAM, with an internal MAR
class RAM:
    def __init__(self, data_bits, address_bits):
        self.data_bits = data_bits
        self.address_bits = address_bits
        
        self.words = 2**self.address_bits
        self.registers = [Register(self.data_bits) for _ in range(self.words)]
        
        self.address = Register(self.address_bits)
    
    def set_address(self, address):
        # Overflow inputs if needed
        address %= 2 ** self.address_bits
        
        self.address.set(address)
        
        
    def write(self, value):
        # Overflow inputs if needed
        value %= 2 ** self.data_bits
        
        self.registers[self.address.get()].set(value)
    
    def read(self):
        return self.registers[self.address.get()].get()



# A class to implement the program ROM, with an integrated program counter register
class ProgramROM:
    def __init__(self, data_bits, address_bits):
        self.data_bits = data_bits
        self.address_bits = address_bits
        
        self.words = 2**self.address_bits
        self.clear()
        
        self.pc = Register(self.address_bits)
        self.pc.set(0)
        
        self.asm = None
    
    
    # Clear ROM
    def clear(self):
        self.instructions = [None for _ in range(self.words)]
    
    
    # Parse a text file into instructions
    def program(self, file_in):
        # Erase
        self.clear()
        
        # Make assembler for file
        self.asm = assembler.Assembler(file_in)
        
        # Run assembly
        self.asm.run()
        
        # Program commands into ROM
        for instruction in self.asm.assembled_objects():
            self.instructions[instruction["address"]] = instruction
    
    
    def set_address(self, address):
        # Overflow inputs if needed
        address %= 2 ** self.address_bits
        
        self.pc.set(address)
    
    
    def increment(self):
        self.set_address(self.pc.get() + 1)
    
    
    def read(self):
        return self.instructions[self.pc.get()]
# ~~~~~~~~ End Hardware Definition ~~~~~~~~


# ~~~~~~~~ Begin System Setup ~~~~~~~~
bitwidth = 8

# Make a helpful decimal converter for printing and such
dec2 = helpers.Dec2(bitwidth)

# Make an ALU
alu = ALU(bitwidth)

# Make the registers
reg_A = Register(bitwidth)
reg_B = Register(bitwidth)
    
# Make the RAM
ram = RAM(data_bits=bitwidth, address_bits=(bitwidth*2))

# Make the ROM
rom = ProgramROM(data_bits=bitwidth, address_bits=(bitwidth*2))
# Program it
rom.program("../FET-80 Development/Test Code/Pointers.FET80")

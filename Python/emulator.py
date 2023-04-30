#!/usr/bin/env python3

from enum import Enum


# ~~~~~~~~ Start Helper Definitions ~~~~~~~~
# A helper class to convert decimals to more useful formats
class Dec2:
    def __init__(self, bits):
        self.bits = bits
    
    # A helper function to turn integers into fixed-length binary strings
    def binary_string(self, n):
        # Get binary string
        binstring = "{0:b}".format(n)
        # Return padded
        return binstring.rjust(self.bits, "0")

    # A helper function to correct integers to represent their actual value in 2's complement
    def twos_compliment(self, n):
        if n >= (2 ** (self.bits-1) ):
            n -= (2 ** self.bits )
        return n

# Define parser class to parse assembly files into a usable format
class AssemblyParser:
    # Opens the input file / stream and gets ready to parse it
    def __init__(self, file_in):
        # Read source file
        with open(file_in, "r") as f:
            self.source = f.readlines()
        
        # Strip source of newlines, whitespace, and comments
        self.stripped = []
        for x in self.source:
            stripped_line = x.replace("\n", "").replace("\r", "")
            stripped_line = stripped_line.replace("\t", " ").strip()
            
            comment_index = stripped_line.find("#")
            if comment_index != -1:
                # Remove comment from index onwards
                final_line = stripped_line[:comment_index].strip()
            else:
                # No comments to remove
                final_line = stripped_line
            
            if len(final_line) > 0:
                self.stripped.append(final_line)
        
        # Set current line to -1
        self.current_line_idx = -1
        
        # Set current program address (line, no loop commands) to -1
        self.current_address = -1
    
    
    # A class to implement the various types of instruction codes
    class InstructionCode(Enum):
        T_INSTRUCTION = 0
        M_INSTRUCTION = 1
        C_INSTRUCTION = 2
        J_INSTRUCTION = 3
        D_INSTRUCTION = 4
        L_INSTRUCTION = 5
    
    
    # Helper function to "reset" the parser
    def reset(self):
        self.current_line_idx = -1
        self.current_address = -1
    
    
    # Are there more lines in the input?
    def hasMoreLines(self):
        if self.current_line_idx == -1:
            # If not advanced to first instruction
            return True
        elif self.current_line_idx < len(self.stripped)-1:
            # If our current index is less than the last possible
            return True
        else:
            return False
    
    
    # Skips over white space and comments if necessary.
    # Reads the next instruction from the input, and makes it the current instruction.
    # This routine should be called only if hasMoreLines is true.
    # Initially, there is no current instruction.
    def advance(self):
        # All white space and comments were pre-skipped during __init__
        # The "current instruction" is just an index to a list of stripped lines
        if self.hasMoreLines():
            self.current_line_idx += 1
            # Also increment the address counter ONLY if it is not a loop instruction
            if self.instructionType() != self.InstructionCode.L_INSTRUCTION:
                self.current_address += 1
        else:
            raise Exception("No more lines left in program!")
    
    
    # A helper function to get the current instruction
    def instruction(self):
        if  self.current_line_idx == -1:
            raise Exception("No advance() command issued yet!")
            
        return self.stripped[self.current_line_idx]
    
    
    # Helper function to get the current instruction address
    def address(self):
        return self.current_address
    
    # Returns the type of the current instruction:
    # T_INSTRUCTION for a `MOV` command
    # M_INSTRUCTION for a `MEM` command
    # C_INSTRUCTION for an `ADD` or `NAND` command
    # J_INSTRUCTION for a jump command (`JMP`, `JC`, `JNC`, `JEQZ`, `JNEZ`, `JGTZ`, `JLTZ`, `JGEZ`, `JLEZ`)
    # D_INSTRUCTION for a `NOP` command
    # L_INSTRUCTION for `(xxx)`, where xxx is a symbol
    def instructionType(self):
        first_char = self.instruction()[0]
        first_word = self.instruction().split(" ")[0].upper()
        if first_char == "(":
            return self.InstructionCode.L_INSTRUCTION
        elif first_word == "MOV":
            return self.InstructionCode.T_INSTRUCTION
        elif first_word == "MEM":
            return self.InstructionCode.M_INSTRUCTION
        elif first_word in ["ADD", "NAND"]:
            return self.InstructionCode.C_INSTRUCTION
        elif first_word in ["JMP", "JC", "JNC", "JEQZ", "JNEZ", "JGTZ", "JLTZ", "JGEZ", "JLEZ"]:
            return self.InstructionCode.J_INSTRUCTION
        elif first_word == "NOP":
            return self.InstructionCode.D_INSTRUCTION
        else:
            raise Exception("Current command isn't a known instruction type, no symbol to extract!")
    
    
    
    
    
# ~~~~~~~~ End Helper Definitions ~~~~~~~~


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
    # A class to implement the various opcodes
    class Opcode(Enum):
        NOP = 0
        MOV = 1
        MEM = 2
        ADD = 3
        NAND = 4
        JMP = 5
        JC = 6
        JNC = 7
        JEQZ = 8
        JNEZ = 9
        JGTZ = 10
        JLTZ = 11
        JGEZ = 12
        JLEZ = 13
    
    def __init__(self, data_bits, address_bits):
        self.data_bits = data_bits
        self.address_bits = address_bits
        
        self.words = 2**self.address_bits
        self.instructions = [{"foo" : "bar"} for _ in range(self.words)]
        
        self.pc = Register(self.address_bits)
        self.pc.set(0)
    
    #TODO: Parse a text file into commands
    #def program(self, file_in):
        
    
# ~~~~~~~~ End Hardware Definition ~~~~~~~~


# ~~~~~~~~ Begin Hardware Setup ~~~~~~~~
bitwidth = 8

# Make a helpful decimal converter for printing and such
dec2 = Dec2(bitwidth)

# Make an ALU
alu = ALU(bitwidth)

# Make the registers
reg_A = Register(bitwidth)
reg_B = Register(bitwidth)
    
# Make the RAM
ram = RAM(data_bits=bitwidth, address_bits=(bitwidth*2))

# Make demo assembly parser for testing
asmparser = AssemblyParser("../FET-80 Development/Test Code/XOR.FET80")
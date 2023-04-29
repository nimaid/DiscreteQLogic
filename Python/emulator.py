#!/usr/bin/env python3


# A class to represent an ALU object
class ALU:
    def __init__(self, bits):
        self.bits = bits
        
        self.f = None
        
        self.cycles = 0
        self.unset = True
    
    
    def set_flags(self, f):
        if type(f) != bool:
            raise Exception("Flag 'f' must be True or False, not {}".format(f))
        self.f = f
        
        self.unset = False
    
    
    def set_op(self, op):
        op = op.upper()
        if op == "ADD":
            self.set_flags(
                f  = True
            )
        elif op == "NAND":
            self.set_flags(
                f  = False
            )
        else:
            raise Exception("\"{}\" is not a valid opcode!".format(op))
    
    
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
    
    
    def calc(self, X, Y, cin=False):
        if self.unset:
            raise Exception("set_flags() must be called before calc()!")
        
        # Overflow inputs if needed
        X %= 2 ** self.bits
        Y %= 2 ** self.bits
        
        
        # Add to get the carry no matter what
        sum, cout = self.add(X, Y, cin)
        
        # Select output
        if self.f:
            # Add
            out = sum
        else:
            # NAND
            out = self.invert(X & Y)
        
        self.unset = True
        self.cycles += 1
        return out, cout
    
    
    def get_bit_width(self):
        return self.bits
    
    
    def get_cycles(self):
        return self.cycles
    
    
    def reset_cycles(self):
        self.cycles = 0





'''
# ALU Example Operations
alu = ALU(8)
print("ALU initialized, bit width is {}.".format(alu.get_bit_width()))

# A helper function to turn integers into fixed-length binary strings for display
def dec2binstr(n):
    # Get binary string
    binstring = "{0:b}".format(n)
    # Return padded
    return binstring.rjust(alu.get_bit_width(), "0")

# A helper function to correct integers to represent their actual value in 2's complement
def dec2twoC(n):
    if n >= (2 ** (alu.get_bit_width()-1) ):
        n -= (2 ** alu.get_bit_width() )
    return n


# NAND Example
A = 0b00001111
B = 0b00111100
# NAND is a fundamental operation of the ALU (carry is ignored)
def alu_nand(A, B):
    alu.set_op("NAND")
    output, carry = alu.calc(
        X = A,
        Y = B)
    return output
# Print computation
alu.reset_cycles()
print("~~~ NAND Example ~~~")
print("A:\t{}".format(dec2binstr( A )))
print("B:\t{}".format(dec2binstr( B )))
print("Out:\t{}".format(dec2binstr( alu_nand(A, B) )))
print("Cycles:\t{}".format( alu.get_cycles() ))

# NOT Example
input = 0b00001111
# To negate, we simply use the NAND function with both inputs set to the same input
def alu_not(input):
    alu.set_op("NAND")
    output, carry = alu.calc(
        X = input,
        Y = input)
    return output
# Print computation
alu.reset_cycles()
print("~~~ NOT Example ~~~")
print("In:\t{}".format(dec2binstr( input )))
print("Out:\t{}".format(dec2binstr( alu_not(input) )))
print("Cycles:\t{}".format( alu.get_cycles() ))

# AND Example
A = 0b00001111
B = 0b00111100
# To AND, we must do a NAND, then negate the output
def alu_and(A, B):
    nand = alu_nand(
        A = A,
        B = B)
    output = alu_not(nand)
    return output
# Print computation
alu.reset_cycles()
print("~~~ AND Example ~~~")
print("A:\t{}".format(dec2binstr( A )))
print("B:\t{}".format(dec2binstr( B )))
print("Out:\t{}".format(dec2binstr( alu_and(A, B) )))
print("Cycles:\t{}".format( alu.get_cycles() ))

# OR Example
A = 0b00001111
B = 0b00111100
# To OR, we must first invert both inputs, then do a NAND
def alu_or(A, B):
    not_A = alu_not(A)
    not_B = alu_not(B)
    output = alu_nand(
        A = not_A,
        B = not_B)
    return output
# Print computation
alu.reset_cycles()
print("~~~ OR Example ~~~")
print("A:\t{}".format(dec2binstr( A )))
print("B:\t{}".format(dec2binstr( B )))
print("Out:\t{}".format(dec2binstr( alu_or(A, B) )))
print("Cycles:\t{}".format( alu.get_cycles() ))

# NOR Example
A = 0b00001111
B = 0b00111100
# To NOR, we first take an OR, then invert it
def alu_nor(A, B):
    or_out = alu_or(
        A = A,
        B = B)
    output = alu_not(or_out)
    return output
# Print computation
alu.reset_cycles()
print("~~~ NOR Example ~~~")
print("A:\t{}".format(dec2binstr( A )))
print("B:\t{}".format(dec2binstr( B )))
print("Out:\t{}".format(dec2binstr( alu_nor(A, B) )))
print("Cycles:\t{}".format( alu.get_cycles() ))

# XOR Example
A = 0b00001111
B = 0b00111100
# To XOR, we have to use 4 NAND gates in 3 layers
# First, we run each input through a NAND
# Next, we run each input to the first gates of 2 more NANDs, and the second inputs are hooked to the output of the first NAND
# Finally, we run the outputs from those last 2 NANDs into a final NAND
def alu_xor(A, B):
    nand1 = alu_nand(
        A = A,
        B = B)
    nand2A = alu_nand(
        A = A,
        B = nand1)
    nand2B = alu_nand(
        A = B,
        B = nand1)
    output = alu_nand(
        A = nand2A,
        B = nand2B)
    return output
# Print computation
alu.reset_cycles()
print("~~~ XOR Example ~~~")
print("A:\t{}".format(dec2binstr( A )))
print("B:\t{}".format(dec2binstr( B )))
print("Out:\t{}".format(dec2binstr( alu_xor(A, B) )))
print("Cycles:\t{}".format( alu.get_cycles() ))

# XNOR Example
A = 0b00001111
B = 0b00111100
# To XNOR, we must do an XOR, then negate the output
def alu_xnor(A, B):
    xor = alu_xor(
        A = A,
        B = B)
    output = alu_not(xor)
    return output
# Print computation
alu.reset_cycles()
print("~~~ XNOR Example ~~~")
print("A:\t{}".format(dec2binstr( A )))
print("B:\t{}".format(dec2binstr( B )))
print("Out:\t{}".format(dec2binstr( alu_xnor(A, B) )))
print("Cycles:\t{}".format( alu.get_cycles() ))

# Add Example
A = 0b00001111
B = 0b00111100
# Add is a fundamental operation of the ALU (no carry in used for demonstration)
def alu_add(A, B, cin=False):
    alu.set_op("ADD")
    output, carry = alu.calc(
        X = A,
        Y = B,
        cin = cin)
    return output, carry
# Print computation
alu.reset_cycles()
print("~~~ Add Example ~~~")
print("A:\t{} ({})".format(dec2binstr( A ), dec2twoC(A) ))
print("B:\t{} ({})".format(dec2binstr( B ), dec2twoC(B) ))
sum, cout = alu_add(A, B)
if cout:
    carry_string = "carry"
else:
    carry_string = "no carry"
print("Out:\t{} ({}) + {}".format(dec2binstr( sum ), dec2twoC(sum), carry_string ))
print("Cycles:\t{}".format( alu.get_cycles() ))

# Subtract Example
A = 0b00001111
B = 0b00111100
# To subtract, we invert the positive input, then ADD it with the negative input, and finally invert the output
def alu_sub(A, B, cin=False):
    not_A = alu_not(A)
    add, carry = alu_add(
        A = not_A,
        B = B,
        cin = cin)
    output = alu_not(add)
    return output, carry
# Print computation
alu.reset_cycles()
print("~~~ Subtract Example ~~~")
print("A:\t{} ({})".format(dec2binstr( A ), dec2twoC(A) ))
print("B:\t{} ({})".format(dec2binstr( B ), dec2twoC(B) ))
sub, cout = alu_sub(A, B)
if cout:
    carry_string = "carry"
else:
    carry_string = "no carry"
print("Out:\t{} ({}) + {}".format(dec2binstr( sub ), dec2twoC(sub), carry_string ))
print("Cycles:\t{}".format( alu.get_cycles() ))
'''


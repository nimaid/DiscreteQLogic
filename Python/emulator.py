#!/usr/bin/env python3

# A class to represent an ALU object
class ALU:
    def __init__(self, bits):
        self.bits = bits
        
        self.nx = None
        self.ny = None
        self.f = None
        self.no = None
        
        self.unset = True
        
    def set_flags(self, nx, ny, f, no):
        if type(nx) != bool:
            raise Exception("Flag 'nx' must be True or False, not {}".format(nx))
        self.nx = nx
        
        if type(ny) != bool:
            raise Exception("Flag 'ny' must be True or False, not {}".format(ny))
        self.ny = ny
        
        if type(f) != bool:
            raise Exception("Flag 'f' must be True or False, not {}".format(f))
        self.f = f
        
        if type(no) != bool:
            raise Exception("Flag 'no' must be True or False, not {}".format(no))
        self.no = no
        
        self.unset = False
    
    def set_op(self, op):
        op = op.upper()
        if op == "ADD":
            self.set_flags(
                nx = False,
                ny = False,
                f  = True,
                no = False
            )
        elif op == "SUB":
            self.set_flags(
                nx = True,
                ny = False,
                f  = True,
                no = True
            )
        elif op == "SUBR":
            self.set_flags(
                nx = True,
                ny = False,
                f  = True,
                no = True
            )
        elif op == "AND":
            self.set_flags(
                nx = False,
                ny = False,
                f  = False,
                no = False
            )
        elif op == "NAND":
            self.set_flags(
                nx = False,
                ny = False,
                f  = False,
                no = True
            )
        elif op == "OR":
            self.set_flags(
                nx = True,
                ny = True,
                f  = False,
                no = True
            )
        elif op == "NOR":
            self.set_flags(
                nx = True,
                ny = True,
                f  = False,
                no = False
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
    
    def calc(self, X, Y, cin):
        if self.unset:
            raise Exception("set_flags() must be called before calc()!")
        
        # Overflow inputs if needed
        X %= 2 ** self.bits
        Y %= 2 ** self.bits
        
        # Invert X
        if self.nx:
            X = self.invert(X)
        
        # Invert Y
        if self.ny:
            Y = self.invert(Y)
        
        # Add to get the carry no matter what
        sum, cout = self.add(X, Y, cin)
        
        # Select output
        if self.f:
            # Add
            out = sum
        else:
            # AND
            out = X & Y
        
        # Invert out (active low, MUX output inverted)
        if self.no == False:
            out = self.invert(out)
        
        self.unset = True
        return out, cout
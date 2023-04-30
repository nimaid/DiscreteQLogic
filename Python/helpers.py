#!/usr/bin/env python3

import os
import sys


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
    
    
    # A helper to overflow integers to be in range
    def overflow(self, n):
        return n % 2 ** self.bits
    
    
    # A helper function which tries to find strings formatted correctly, and converts them to an appropriate integer
    def int_from_formatted(self, n):
        # Strip all whitespace
        n = n.replace("\t", "").replace("\r", "").replace("\n", "").replace(" ", "")
        # First, test if it is supposed to be a hex or binary string
        if len(n) >= 3 and n[0] == "0":
            # It starts with a zero and has at least 3 chars
            if n[1].lower() == "x":
                # It's supposed to be a hex string
                try:
                    value = int(n[2:], 16)
                    value = self.overflow(value)
                    return value
                except ValueError:
                    # Okay, that didn't work
                    pass
            elif n[1].lower() == "b":
                # It's supposed to be a binary string
                try:
                    value = int(n[2:], 2)
                    value = self.overflow(value)
                    return value
                except ValueError:
                    # Okay, that didn't work
                    pass

        # Next, test if it is a literal integer (first char is a digit or minus)
        if n[0].isdigit() or n[0] == "-":
            # It is supposed to be a literal integer, read it in and overflow it
            try:
                value = int(n)
                value = self.overflow(value)
                return value
            except ValueError:
                # Okay, that didn't work
                pass
        
        # If we got to this point, it is not a valid integer, and we will return False
        return False



# Used for the argument parser
def file_path(string):
    if os.path.isfile(string):
        return string
    else:
        raise FileNotFoundError(string)

if __name__ == '__main__':
    print("This module is not meant to be run on it's own!")
    sys.exit()  # next section explains the use of sys.exit
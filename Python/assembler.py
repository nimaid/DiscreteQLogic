#!/usr/bin/env python3

import os
import sys
import argparse
from enum import Enum

import helpers


# A class to provide assembly-related codes
class AsmCodes:
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
    
    
    # A class to implement the various sources
    class Src(Enum):
        A = 0
        B = 1
        M = 2
        DV = 3
    
    
    # A class to implement the various destinations
    class Dest(Enum):
        A = 0
        B = 1
        M = 2
    
    
    # A class to implement the various instruction types
    class InstructionType(Enum):
        T_INSTRUCTION = 0
        M_INSTRUCTION = 1
        C_INSTRUCTION = 2
        J_INSTRUCTION = 3
        D_INSTRUCTION = 4
        L_INSTRUCTION = 5



# A class to store FET-80 specific parameters
class Fet80Params:
    # Bit widths
    DataWidth = 8
    AddressWidth = DataWidth * 2
    
    # Assembler constants
    AsmConstants = [ {"name" : "R0", "value" : 0},
                     {"name" : "R1", "value" : 1},
                     {"name" : "R2", "value" : 2},
                     {"name" : "R3", "value" : 3},
                     {"name" : "R4", "value" : 4},
                     {"name" : "R5", "value" : 5},
                     {"name" : "R6", "value" : 6},
                     {"name" : "R7", "value" : 7},
                     {"name" : "R8", "value" : 8},
                     {"name" : "R9", "value" : 9},
                     {"name" : "R10", "value" : 10},
                     {"name" : "R11", "value" : 11},
                     {"name" : "R12", "value" : 12},
                     {"name" : "R13", "value" : 13},
                     {"name" : "R14", "value" : 14},
                     {"name" : "R15", "value" : 15},
                     {"name" : "SCREEN", "value" : 0xFFD0},
                     {"name" : "IO0", "value" : 0xFFF0},
                     {"name" : "IO1", "value" : 0xFFF1},
                     {"name" : "IO2", "value" : 0xFFF2},
                     {"name" : "IO3", "value" : 0xFFF3},
                     {"name" : "IO4", "value" : 0xFFF4},
                     {"name" : "IO5", "value" : 0xFFF5},
                     {"name" : "IO6", "value" : 0xFFF6},
                     {"name" : "IO7", "value" : 0xFFF7},
                     {"name" : "IO8", "value" : 0xFFF8},
                     {"name" : "IO9", "value" : 0xFFF9},
                     {"name" : "IO10", "value" : 0xFFFA},
                     {"name" : "IO11", "value" : 0xFFFB},
                     {"name" : "IO12", "value" : 0xFFFC},
                     {"name" : "IO13", "value" : 0xFFFD},
                     {"name" : "IO14", "value" : 0xFFFE},
                     {"name" : "IO15", "value" : 0xFFFF} ]
    
    # First free memory location (after virtual registers)
    FirstFreeMemLoc = 16
    
    # Screen size
    ScreenSize = { "x" : 16,
                   "y" : 16 }


# Define parser class to parse assembly files into a usable format
class AsmParser:
    # Opens the input file / stream and gets ready to parse it
    def __init__(self, file_in):
        # Read source file
        with open(file_in, "r") as f:
            self.set_source(f.readlines())
        
        # Set current line to -1
        self.current_line_idx = -1
        
        # Set current program address (line, no loop commands) to -1
        self.current_address = -1
    
    
    # Helper to set the stripped source text of the parser (list of strings)
    def set_source(self, source_text):
        self.source = source_text
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
            if self.instructionType() != AsmCodes.InstructionType.L_INSTRUCTION:
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
            return AsmCodes.InstructionType.L_INSTRUCTION
        elif first_word == "MOV":
            return AsmCodes.InstructionType.T_INSTRUCTION
        elif first_word == "MEM":
            return AsmCodes.InstructionType.M_INSTRUCTION
        elif first_word in ["ADD", "NAND"]:
            return AsmCodes.InstructionType.C_INSTRUCTION
        elif first_word in ["JMP", "JC", "JNC", "JEQZ", "JNEZ", "JGTZ", "JLTZ", "JGEZ", "JLEZ"]:
            return AsmCodes.InstructionType.J_INSTRUCTION
        elif first_word == "NOP":
            return AsmCodes.InstructionType.D_INSTRUCTION
        else:
            raise Exception("Current command isn't a known instruction type, no symbol to extract!")
    
    
    # Helper function to get the current instruction, split at the chosen delimiter
    def instruction_split(self, text=None, delimiter=" "):
        if text is None:
            text = self.instruction()
        
        if type(text) == list:
            final_list = []
            for part in text:
                final_list += list(filter(None, part.split(delimiter)))
            return final_list
        else:
            return list(filter(None, text.split(delimiter)))
    
    
    # If the current instruction is `(xxx)`, returns the symbol `xxx`.
    # If the current instruction is `JMP xxx` or `MEM xxx`, returns the symbol or decimal xxx (as a string).
    # Should be called only if instructionType is M_INSTRUCTION, J_INSTRUCTION, or L_INSTRUCTION
    def symbol(self):
        current_instruction_type = self.instructionType()
        if current_instruction_type in [AsmCodes.InstructionType.M_INSTRUCTION, AsmCodes.InstructionType.J_INSTRUCTION]:
            # Will always be in the format `OP xxx`, can just take last portion
            split_instruction = self.instruction_split()
            if len(split_instruction) != 2:
                raise Exception("This instruction requires exactly 1 argument: \"{}\"".format(self.instruction()))
            return split_instruction[1]
        elif current_instruction_type == AsmCodes.InstructionType.L_INSTRUCTION:
            # Remove ( and ) in (xxx)
            return self.instruction().replace("(", "").replace(")", "")
        else:
            raise Exception("Current command isn't a valid instruction, no symbol to extract!")
    
    
    # Returns the symbolic `src` part of the current instruction (3 possibilities or an int.)
    # Should only be called if instructionType is T_INSTRUCTION or C_INSTRUCTION
    def src(self):
        if self.instructionType() in [AsmCodes.InstructionType.T_INSTRUCTION, AsmCodes.InstructionType.C_INSTRUCTION]:
            # Will always be in the format `OP xxx, yyy`, can just take the last portion
            split_instruction = self.instruction_split()
            split_instruction = self.instruction_split(split_instruction, ",")
            if len(split_instruction) != 3:
                raise Exception("This instruction requires exactly 2 arguments: \"{}\"".format(self.instruction()))
            return split_instruction[2]
        else:
            raise Exception("Current command isn't a valid instruction, no symbol to extract!")
    
    
    # Returns the symbolic `dest` part of the current instruction (3 possibilities)
    # Should only be called if instructionType is T_INSTRUCTION or C_INSTRUCTION
    def dest(self):
        if self.instructionType() in [AsmCodes.InstructionType.T_INSTRUCTION, AsmCodes.InstructionType.C_INSTRUCTION]:
            # Will always be in the format `OP xxx, yyy`, can just take the middle part
            split_instruction = self.instruction_split()
            split_instruction = self.instruction_split(split_instruction, ",")
            if len(split_instruction) != 3:
                raise Exception("This instruction requires exactly 2 arguments: \"{}\"".format(self.instruction()))
            return split_instruction[1]
        else:
            raise Exception("Current command isn't a valid instruction, no symbol to extract!")
    
    
    # Returns the symbolic `opcode` part of the current instruction
    # This can be called for any valid instruction
    def opcode(self):
        # We just return the first part, always
        split_instruction = self.instruction_split()
        return split_instruction[0].upper()



# Define SymbolTable class for use in the pre-assembler
class SymbolTable:
    # Creates a new empty symbol table.
    def __init__(self):
        self.table = dict()
    
    # Adds <symbol,address> to the table
    def addEntry(self, symbol, address):
        self.table[symbol] = address
    
    # Does the symbol table contain the given symbol?
    def contains(self, symbol):
        if symbol in self.table.keys():
            return True
        else:
            return False
    
    # Returns the address associated with the symbol.
    def getAddress(self, symbol):
        return self.table[symbol]



# A class to assemble the commands to simple instructions and resolve symbols
class Assembler:
    def __init__(self, file_in):
        
        self.asm = AsmParser(file_in)
        self.reset()
        
        self.dec_data = helpers.Dec2(Fet80Params.DataWidth)
        self.dec_address = helpers.Dec2(Fet80Params.AddressWidth)
    
    
    # A helper to reset the assembler
    def reset(self):
        self.asm.reset()
        
        # Make new symbol table
        self.asmtable = SymbolTable()
        
        # Initialize symbol table with predefined constants
        for s in Fet80Params.AsmConstants:
            self.asmtable.addEntry(s["name"], s["value"])
        # Relevantly, set the first free RAM address
        self.free_mem_loc = Fet80Params.FirstFreeMemLoc
        
        self.assembled_code_objects = None
    
    
    # Preliminary pass to replace `@` indirect memory addressing with 2 commands
    def resolve_indirect_memory(self):
        fixed_indirect_memory = False
        new_source = list()
        while(self.asm.hasMoreLines()):
            self.asm.advance()
            
            # We need to check T, M, and C instructions for using `@` (valid)
            # We also should check for J instructions illegally using it here
            # Ignore NOP I guess
            
            if self.asm.instructionType() in [AsmCodes.InstructionType.T_INSTRUCTION, AsmCodes.InstructionType.C_INSTRUCTION]:
                src_indirect = ( self.asm.src()[0] == "@" )
                dest_indirect = ( self.asm.dest()[0] == "@" )
                if src_indirect and dest_indirect:
                    raise Exception("Only one memory location can be used per command!")
                if src_indirect:
                    new_source.append("MEM {}".format(self.asm.src()[1:]))
                    new_source.append("{} {}, M".format(self.asm.opcode(), self.asm.dest()))
                    fixed_indirect_memory = True
                elif dest_indirect:
                    new_source.append("MEM {}".format(self.asm.dest()[1:]))
                    new_source.append("{} M, {}".format(self.asm.opcode(), self.asm.src()))
                    fixed_indirect_memory = True
                else:
                    new_source.append(self.asm.instruction())
            elif self.asm.instructionType() == AsmCodes.InstructionType.M_INSTRUCTION:
                symbol_indirect = ( self.asm.symbol()[0] == "@" )
                if symbol_indirect:
                    new_source.append("MEM {}".format(self.asm.symbol()[1:]))
                    new_source.append("MEM M")
                    fixed_indirect_memory = True
                else:
                    new_source.append(self.asm.instruction())
            elif self.asm.instructionType() == AsmCodes.InstructionType.J_INSTRUCTION:
                if self.asm.symbol()[0] == "@":
                    raise Exception("Cannot use `@` in a jump instruction: \"{}\"".format(self.asm.instruction()))
                new_source.append(self.asm.instruction())
            else:
                new_source.append(self.asm.instruction())
        
        self.asm.set_source(new_source)
        self.asm.reset()
        
        return fixed_indirect_memory
    
    
    # Performs multiple levels of resolving indirect memory until it is all flat
    def resolve_all_indirect_memory(self):
        more_indirect_memory = True
        while more_indirect_memory:
            more_indirect_memory = self.resolve_indirect_memory()
    
    
    # Pre-assemble pass, add all L-instructions to the symbol table
    def resolve_loops(self):
        while(self.asm.hasMoreLines()):
            self.asm.advance()
            if self.asm.instructionType() == AsmCodes.InstructionType.L_INSTRUCTION:
                if self.asm.symbol()[0] == "@" or self.asm.symbol() in ["A", "B", "M"]:
                    raise Exception("\"{}\" is not a valid symbol name!".format(self.asm.symbol()))
                # If it's an L-instruction, make a new symbol that is the index of the next line in the program
                self.asmtable.addEntry(self.asm.symbol(), self.asm.address()+1)
        self.asm.reset()
    
    
    # Assembles the objects for the final codes
    def assemble_objects(self):
        self.assembled_code_objects = list()
        while(self.asm.hasMoreLines()):
            self.asm.advance()
            
            # Init the instruction output dict
            instruction = { "type" : self.asm.instructionType(),
                            "address" : self.asm.address(),
                            "opcode" : None,
                            "value" : None,
                            "src" : None,
                            "dest" : None }
            
            if instruction["type"] in [AsmCodes.InstructionType.T_INSTRUCTION, AsmCodes.InstructionType.C_INSTRUCTION]:
                # Always a `MOV`, `ADD`, or `NAND` instruction
                # Format: `MOV dest, src`
                # `src` can be a direct value
                
                if self.asm.opcode() == "MOV":
                    instruction["opcode"] = AsmCodes.Opcode.MOV
                elif self.asm.opcode() == "ADD":
                    instruction["opcode"] = AsmCodes.Opcode.ADD
                elif self.asm.opcode() == "NAND":
                    instruction["opcode"] = AsmCodes.Opcode.NAND
                
                if self.asm.dest() == "A":
                    instruction["dest"] = AsmCodes.Dest.A
                elif self.asm.dest() == "B":
                    instruction["dest"] = AsmCodes.Dest.B
                elif self.asm.dest() == "M":
                    instruction["dest"] = AsmCodes.Dest.M
                else:
                    # Not a valid option
                    raise Exception("{} is not a valid destination!".format(self.asm.dest()))
                
                if self.asm.src() == "A":
                    instruction["src"] = AsmCodes.Src.A
                elif self.asm.src() == "B":
                    instruction["src"] = AsmCodes.Src.B
                elif self.asm.src() == "M":
                    instruction["src"] = AsmCodes.Src.M
                elif self.asmtable.contains(self.asm.src()):
                    # It's a symbol
                    instruction["value"] = self.asmtable.getAddress(self.asm.src())
                    instruction["src"] = AsmCodes.Src.DV
                else:
                    # It may be a direct value
                    value = self.dec_data.int_from_formatted(self.asm.src())
                    if type(value) == bool:
                         raise Exception("\"{}\" from \"{}\"is not a valid destination or integer!".format(self.asm.src(), self.asm.instruction()))
                    instruction["value"] = value
                    instruction["src"] = AsmCodes.Src.DV
                    
                self.assembled_code_objects.append(instruction)
            elif instruction["type"] in [AsmCodes.InstructionType.M_INSTRUCTION, AsmCodes.InstructionType.J_INSTRUCTION]:
                # Always either a `MEM` or a type of `JMP` instruction
                # Format: `MEM symbol`
                # We must resolve either the symbol or direct value
                # Additionally, `MEM` can have a non-direct `src`, like `A` or even `M`
                # Hex and binary values are allowed with 0x and 0b
                
                if self.asm.opcode() == "MEM":
                    instruction["opcode"] = AsmCodes.Opcode.MEM
                elif self.asm.opcode() == "JMP":
                    instruction["opcode"] = AsmCodes.Opcode.JMP
                elif self.asm.opcode() == "JC":
                    instruction["opcode"] = AsmCodes.Opcode.JC
                elif self.asm.opcode() == "JNC":
                    instruction["opcode"] = AsmCodes.Opcode.JNC
                elif self.asm.opcode() == "JEQZ":
                    instruction["opcode"] = AsmCodes.Opcode.JEQZ
                elif self.asm.opcode() == "JNEZ":
                    instruction["opcode"] = AsmCodes.Opcode.JNEZ
                elif self.asm.opcode() == "JGTZ":
                    instruction["opcode"] = AsmCodes.Opcode.JGTZ
                elif self.asm.opcode() == "JGTZ":
                    instruction["opcode"] = AsmCodes.Opcode.JGTZ
                elif self.asm.opcode() == "JLTZ":
                    instruction["opcode"] = AsmCodes.Opcode.JLTZ
                elif self.asm.opcode() == "JGEZ":
                    instruction["opcode"] = AsmCodes.Opcode.JGEZ
                elif self.asm.opcode() == "JLEZ":
                    instruction["opcode"] = AsmCodes.Opcode.JLEZ
                
                # Now we need to set the value
                # Before anything, if it's `MEM`, check for non-direct values
                # First, we will check to see if it is already in the symbol table
                # If not, we will then check to see if it is a direct value,
                # Finally, if it is a valid symbol name, add a new symbol to the table
                
                symbol_value = self.dec_address.int_from_formatted(self.asm.symbol())
                
                # If it's MEM and also a valid non-direct symbol, just pass `src`
                if instruction["type"] == AsmCodes.InstructionType.M_INSTRUCTION:
                    if self.asm.symbol() in ["A", "B", "M"]:
                        if self.asm.symbol() == "A":
                            instruction["src"] = AsmCodes.Src.A
                        elif self.asm.symbol() == "B":
                            instruction["src"] = AsmCodes.Src.B
                        elif self.asm.symbol() == "M":
                            instruction["src"] = AsmCodes.Src.M
                        self.assembled_code_objects.append(instruction)
                        continue
                # If not skipped, it's a direct value
                instruction["src"] = AsmCodes.Src.DV
                
                # Check the symbol table first
                if self.asmtable.contains(self.asm.symbol()):
                    # Use the symbol value
                    instruction["value"] = self.asmtable.getAddress(self.asm.symbol())
                # Check if it's a direct value then
                elif type(symbol_value) != bool:
                    instruction["value"] = symbol_value
                # Finally, just add it to the symbol table if it is valid
                else:
                    if (self.asm.symbol() in ["A", "B", "M"]) or self.asm.symbol()[0] =="@":
                        raise Exception("\"{}\" is not a valid symbol name!".format(self.asm.symbol()))
                    self.asmtable.addEntry(self.asm.symbol(), self.free_mem_loc)
                    self.free_mem_loc += 1
                    instruction["value"] = self.asmtable.getAddress(self.asm.symbol())
                self.assembled_code_objects.append(instruction)
            elif instruction["type"] == AsmCodes.InstructionType.D_INSTRUCTION:
                # It is a `NOP`
                instruction["opcode"] = AsmCodes.Opcode.NOP
                self.assembled_code_objects.append(instruction)
        self.asm.reset()
    
    
    # Main loop, where the assembly actually occurs
    def run(self):
        self.resolve_all_indirect_memory()
        self.resolve_loops()
        self.assemble_objects()
    
    
    # A helper to get the assembled objects
    def assembled_objects(self):
        if self.assembled_code_objects is None:
            raise Exception("Assembler hasn't been run yet!")
        return self.assembled_code_objects
    
    
    # A helper function to return the processed assembly in it's human-readable symbolic form
    def processed_assembly(self):
        processed_asm = list()
        for line in self.assembled_objects():
            if line["opcode"] == AsmCodes.Opcode.NOP:
                opcode_text = "NOP"
            elif line["opcode"] == AsmCodes.Opcode.MOV:
                opcode_text = "MOV"
            elif line["opcode"] == AsmCodes.Opcode.MEM:
                opcode_text = "MEM"
            elif line["opcode"] == AsmCodes.Opcode.ADD:
                opcode_text = "ADD"
            elif line["opcode"] == AsmCodes.Opcode.NAND:
                opcode_text = "NAND"
            elif line["opcode"] == AsmCodes.Opcode.JMP:
                opcode_text = "JMP"
            elif line["opcode"] == AsmCodes.Opcode.JC:
                opcode_text = "JC"
            elif line["opcode"] == AsmCodes.Opcode.JNC:
                opcode_text = "JNC"
            elif line["opcode"] == AsmCodes.Opcode.JEQZ:
                opcode_text = "JEQZ"
            elif line["opcode"] == AsmCodes.Opcode.JNEZ:
                opcode_text = "JNEZ"
            elif line["opcode"] == AsmCodes.Opcode.JGTZ:
                opcode_text = "JGTZ"
            elif line["opcode"] == AsmCodes.Opcode.JLTZ:
                opcode_text = "JLTZ"
            elif line["opcode"] == AsmCodes.Opcode.JGEZ:
                opcode_text = "JGEZ"
            elif line["opcode"] == AsmCodes.Opcode.JLEZ:
                opcode_text = "JLEZ"
            
            if line["src"] == AsmCodes.Src.DV:
                source_text = str(line["value"])
            elif line["src"] == AsmCodes.Src.A:
                source_text = "A"
            elif line["src"] == AsmCodes.Src.B:
                source_text = "B"
            elif line["src"] == AsmCodes.Src.M:
                source_text = "M"
            
            if line["dest"] == AsmCodes.Dest.A:
                dest_text = "A"
            elif line["dest"] == AsmCodes.Dest.B:
                dest_text = "B"
            elif line["dest"] == AsmCodes.Dest.M:
                dest_text = "M"
            
            if line["type"] == AsmCodes.InstructionType.D_INSTRUCTION:
                line_text = "{}".format(opcode_text)
            elif line["type"] in [AsmCodes.InstructionType.T_INSTRUCTION, AsmCodes.InstructionType.C_INSTRUCTION]:
                line_text = "{} {}, {}".format(opcode_text, dest_text, source_text)
            elif line["type"] in [AsmCodes.InstructionType.M_INSTRUCTION, AsmCodes.InstructionType.J_INSTRUCTION]:
                line_text = "{} {}".format(opcode_text, source_text)
                
            processed_asm.append(line_text)
        return processed_asm



def main(asm_file):
    # Get .fet80 filename
    asm_file = os.path.realpath(asm_file)
    asm_file_nopath = os.path.split(asm_file)[1]

    # Make assembler
    asm = Assembler(asm_file)
    
    # Run assembly
    asm.run()
    
    # Print processed assembly for debugging
    #TODO: something useful
    print("~~~~~~~~ Processed Assembly for \"{}\" ~~~~~~~~".format(asm_file_nopath))
    for i, line in enumerate(asm.processed_assembly()):
        print("{}:\t{}".format(i, line))
    
    return 0
    
if __name__ == '__main__':
    # Parse arguments
    argparser = argparse.ArgumentParser(
        description="Assembles a .f80asm file into machine code (.f80bin)",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    argparser.add_argument("-f", "--file", type=helpers.file_path, required=True,
        help="the .f80asm file to assemble")
    args = vars(argparser.parse_args())
    
    # Run main
    exit_code = main(args["file"])
    sys.exit(exit_code)
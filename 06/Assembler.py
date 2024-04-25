#! /usr/bin/env python3

from sys import argv
from temp.Code import Code
from temp.Table import SymbolTable

in_file = argv[1]
out_file = in_file.replace('asm', 'hack')

global instructionNumber
instructionNumber = 0
global freeRegister
freeRegister = 16

class Parser:

    def __init__(self, in_file, out_file):
        self.code = Code()
        self.st = SymbolTable()
        self.addDefaultEntrySymbolTable()
        self.instructions = self.loadInstructionsFromFile()
        self.cleanInstructions()
        self.convertDS()
        self.categorizeInstructions()
        self.addIndexToInstructions()
        self.addReferenceToAInstructions()
        self.addDestFields()
        self.addJumpFields()
        self.addCompFields()
        self.translateJump2Binary()
        self.translateDest2Binary()
        self.translateComp2Binary()
        self.addCInstructionBinaryTranslation()
        #self.addLabelsSymbolTable()
        self.convertReferencesToAddresses()
        self.translateAInstructionAddresses2Binary()
        self.writeOutputFile()

    # Load instructions from input file to object
    def loadInstructionsFromFile(self):
        with open(in_file) as fp:
            return fp.readlines()

    # Remove comments or empty lines from loaded instructions, and then strip the instructions of leading/trailling whitespaces
    def cleanInstructions(self):
        temp = filter(lambda x: not (x.startswith('//') or x == '\n'), self.instructions)
        def cleanInLineComments(instruction):
            inLineComment = instruction.find('/')
            if inLineComment != -1:
                instruction = instruction[:inLineComment]
                return instruction
            else:
                return instruction
        temp = map(cleanInLineComments, temp)
        temp = list(map(lambda x: x.strip(), temp))
        self.instructions = temp

    # Convert individual instructions to dict data structure
    def convertDS(self):
        temp = list(map(lambda x: {
            'instruction': x
        }, self.instructions))
        '''
        index = 0
        temp = []
        for instruction in self.instructions:
            temp.append({
                'index': index,
                'instruction': instruction
            })
            index += 1
        '''
        self.instructions = temp

    # Add indexes to A and C Instruction
    def addIndexToInstructions(self):
        index = 0
        for instruction in self.instructions:
            if instruction['type'] == 'A_INSTRUCTION' or instruction['type'] == 'C_INSTRUCTION':
                instruction['index'] = index
                index += 1

    # Categorize instructions
    def categorizeInstructions(self):
        def determineCategory(instruction):
            global instructionNumber
            if instruction['instruction'].startswith('@'):
                instruction['type'] = 'A_INSTRUCTION'
                instructionNumber += 1
            elif instruction['instruction'].startswith('('):
                instruction['type'] = 'L_INSTRUCTION'
                self.st.addEntry(instruction['instruction'].replace('(', '').replace(')', ''), instructionNumber)
            else:
                instruction['type'] = 'C_INSTRUCTION'
                instructionNumber += 1
            return instruction
        self.instruction = list(map(determineCategory, self.instructions))

    # Load L_INSTRUCTIONS to symbol table
    def addLabelsSymbolTable(self):
        def addLabels(instruction):
            global instructionNumber
            if instruction['type'] == 'L_INSTRUCTION':
                self.st.addEntry(instruction['instruction'].replace('(', '').replace(')', ''), instructionNumber )
                return instruction
            else:
                return instruction
        self.instructions = list(map(addLabels, self.instructions))

    # Get symbols for A_INSTRUCTION
    def addReferenceToAInstructions(self):
        def addReference(instruction):
            if instruction['type'] == 'A_INSTRUCTION':
                instruction['reference'] = instruction['instruction'].replace('@', '')
                return instruction
            return instruction
        self.instructions = list(map(addReference, self.instructions))

    # Add Addresses for A_INSTRUCTIONS
    #IMPORTANT: Should be run in second pass only
    def convertReferencesToAddresses(self):
        def convertReferences(instruction):
            global freeRegister
            if instruction['type'] == 'A_INSTRUCTION':
                if self.st.contains(instruction['reference']):
                    instruction['address'] = self.st.getAddress(instruction['reference'])
                    return instruction
                elif self.st.contains(instruction['reference']) == False and (not instruction['reference'][0].isdigit()):
                    self.st.addEntry(instruction['reference'], freeRegister)
                    freeRegister += 1
                    instruction['address'] = self.st.getAddress(instruction['reference'])
                    return instruction
                else:
                    instruction['address'] = instruction['instruction'].replace('@', '')
                    return instruction
            else:
                return instruction
        self.instructions = list(map(convertReferences, self.instructions))

    # Add binary addresses for A_INSTRUCTIONS
    def translateAInstructionAddresses2Binary(self):
        def translateAddress(instruction):
            if instruction['type'] == 'A_INSTRUCTION':
                instruction['binary_instruction'] = f'{bin(int(instruction["address"])).removeprefix("0b"):0>16}'
                return instruction
            else:
                return instruction
        self.instructions = list(map(translateAddress, self.instructions))

    # Add dest field to C_INSTRUCTIONS
    def addDestFields(self):
        def getDest(instruction):
            if instruction['type'] == 'C_INSTRUCTION':
                equal = instruction['instruction'].find('=')
                if equal != -1:
                    instruction['dest'] = instruction['instruction'][:equal]
                    instruction['dest'] = ''.join(sorted(instruction['dest']))
                    return instruction
                else:
                    instruction['dest'] = None
            return instruction
        self.instructions = list(map(getDest, self.instructions))

    # Add comp field to C_INSTRUCTIONS
    def addCompFields(self):
        def getComp(instruction):
            if instruction['type'] == 'C_INSTRUCTION':
                equal = instruction['instruction'].find('=')
                semi = instruction['instruction'].find(';')
                if equal == -1 and semi == -1:
                    instruction['comp'] = instruction['instruction']
                elif equal != -1 and semi == -1:
                    instruction['comp'] = instruction['instruction'][equal+1:]
                elif equal == -1 and semi != -1:
                    instruction['comp'] = instruction['instruction'][:semi]
                elif equal != -1  and semi != -1:
                    instruction['comp'] = instruction['instruction'][equal+1:semi]
                return instruction
            return instruction
        self.instructions = list(map(getComp, self.instructions))

    # Add jump field to C_INSTRUCTIONS
    def addJumpFields(self):
        def getJump(instruction):
            if instruction['type'] == 'C_INSTRUCTION':
                semi = instruction['instruction'].find(';')
                if semi != -1:
                    instruction['jump'] = instruction['instruction'][semi+1:]
                    return instruction
                else:
                    instruction['jump'] = None
            return instruction
        self.instructions = list(map(getJump, self.instructions))

    # Add binary translation of jump field to C_INSTRUCTION
    def translateJump2Binary(self):
        def translateJump(instruction):
            if instruction['type'] == 'C_INSTRUCTION':
                instruction['binary_jump'] = self.code.jump(instruction['jump'])
                return instruction
            else:
                return instruction
        self.instructions = list(map(translateJump, self.instructions))

    # Add binary translation of dest field to C_INSTRUCTION
    def translateDest2Binary(self):
        def translateDest(instruction):
            if instruction['type'] == 'C_INSTRUCTION':
                instruction['binary_dest'] = self.code.dest(instruction['dest'])
                return instruction
            else:
                return instruction
        self.instructions = list(map(translateDest, self.instructions))

    # Add binary translation of dest field to C_INSTRUCTION
    def translateComp2Binary(self):
        def translateComp(instruction):
            if instruction['type'] == 'C_INSTRUCTION':
                instruction['binary_comp'] = self.code.comp(instruction['comp'])
                return instruction
            else:
                return instruction
        self.instructions = list(map(translateComp, self.instructions))

    # Add the entire binary instruction translation to C_INSTRUCTIONS
    def addCInstructionBinaryTranslation(self):
        def addBinaryTranslation(instruction):
            if instruction['type'] == 'C_INSTRUCTION':
                instruction['binary_instruction'] = '111' + instruction['binary_comp'] + instruction['binary_dest'] + instruction['binary_jump']
                return instruction
            else:
                return instruction
        self.instructions = list(map(addBinaryTranslation, self.instructions))

    # Add default labels to symbol table
    def addDefaultEntrySymbolTable(self):
        for i in range(16):
            self.st.addEntry('R' + str(i), i)
        self.st.addEntry('SCREEN', 16384)
        self.st.addEntry('KEYBOARD', 24576)
        self.st.addEntry('SP', 0)
        self.st.addEntry('LCL', 1)
        self.st.addEntry('ARG', 2)
        self.st.addEntry('THIS', 3)
        self.st.addEntry('THAT', 4)


    # Write binary instructions to outputfile
    def writeOutputFile(self):
        def getBinaryInstruction(instruction):
            if instruction['type'] == 'A_INSTRUCTION' or instruction['type'] == 'C_INSTRUCTION':
                return instruction['binary_instruction']
            else:
                return None
        temp = list(filter(lambda x: x != None, (map(getBinaryInstruction, self.instructions))))
        with open(out_file, "w") as fp:
            for instruction in temp:
                fp.write(instruction + '\n')

def main():
    def pretty(d, indent=0):
        for item in d:
            for key, value in item.items():
                print('\t' * indent + str(key))
                if isinstance(value, dict):
                    pretty(value, indent+1)
                else:
                    print('\t' * (indent+1) + str(value))
            print('--------------------')

    parser = Parser(in_file, out_file)

if __name__ == '__main__':
    main()



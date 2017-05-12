import re

from instructions import R_TYPE, J_TYPE, I_TYPE, REGISTERS

label_table = {}


def disassembly_R(line, instruction_bin):
    result = []

    line['rs'] = instruction_bin[6:11]
    line['rt'] = instruction_bin[11:16]
    line['rd'] = instruction_bin[16:21]
    line['shamt'] = instruction_bin[21:26]
    line['func'] = instruction_bin[26:32]

    for instruction_name, instruction in R_TYPE.items():
        if instruction['func'] == int(line['func'], 2):
            result.append(instruction_name)
            break
    else:
        raise Exception('no such register')

    for i in R_TYPE[result[0]]['args']:
        if i == 'shamt':
            result.append(hex(int(line[i], 2)))
        else:
            for reg_name, value in REGISTERS.items():
                if int(line[i], 2) == value:
                    result.append(reg_name)
                    break
            else:
                raise Exception('no such register')
    return result


def disassembly_I(line, instruction_bin):
    result = []
    line['opcode'] = instruction_bin[0:6]
    line['rs'] = instruction_bin[6:11]
    line['rt'] = instruction_bin[11:16]
    line['imm'] = instruction_bin[16:]
    for instruction_name, instruction in I_TYPE.items():
        if instruction['opcode'] == int(line['opcode'], 2):
            result.append(instruction_name)
    for i in I_TYPE[result[0]]['args']:

        if i == 'imm':
            result.append(hex(int(line[i], 2)))
        else:
            for reg_name, value in REGISTERS.items():
                if int(line[i], 2) == value:
                    result.append(reg_name)
                    break
            else:
                raise Exception('no such register')

    return result


def disassembly_J(line, instruction_bin):
    result = []
    line['target'] = instruction_bin[6:]
    for instruction_name, instruction in J_TYPE.items():
        if instruction['opcode'] == int(line['opcode'], 2):
            result.append(instruction_name)
    result.append(hex(int(line['target'], 2)))

    return result


def disassembly_line(address, instruction_hex):
    instruction_bin = bin(int(instruction_hex, 16))[2:].zfill(32)
    line = {'opcode': instruction_bin[0:6]}

    if line['opcode'] == '000000':
        result = disassembly_R(line, instruction_bin)
    elif line['opcode'] == '000010' or line['opcode'] == '000011':
        result = disassembly_J(line, instruction_bin)
    else:
        result = disassembly_I(line, instruction_bin)

    if result[0] in ('j', 'bne', 'beq', 'jal'):
        if result[0] in ('beq', 'bne'):
            temp_int = int(result[-1], 16)
            if temp_int > 0x7fff:
                temp_int -= 0x10000
            index = address + temp_int + 1
            if index in label_table:
                label_table[index].append(address)
            else:
                label_table[index] = [address]
        elif result[0] in ('j', 'jal'):

            index = int(result[-1], 16)
            if index in label_table:
                label_table[index].append(address)
            else:
                label_table[index] = [address]

    return result


def make_label(result):
    print(label_table)
    for count, (index, addresses) in enumerate(label_table.items()):
        result[index].insert(0, 'label_' + str(count) + ": ")
        for address in addresses:
            result[address][-1] = 'label_' + str(count)


def disassambly(file_address):
    pre_result = []
    result = []
    with open(file_address, 'r') as f:
        for index, l in enumerate(f.readlines()):
            instruction_hex = l.strip('\n')
            if instruction_hex != '' and not instruction_hex.isspace():
                pre_result.append(disassembly_line(index, instruction_hex))

    make_label(pre_result)

    for index, i in enumerate(pre_result):
        result.append(' '.join(i))

    return result


def dis_coe(file_address):
    pre_result = []
    result = []
    with open(file_address, 'r') as f:
        coe_str = f.read().rsplit('=', maxsplit=1)
        hexes = re.split(r'[,;\s]\s*', coe_str[1])
        print(hexes)
        hexes_1 = list(map(lambda x: x.strip('\n'), hexes))
        print(hexes_1)
        hexes_pure = list(filter(None, hexes_1))
        print(hexes_pure)
        for index, l in enumerate(hexes_pure):
            instruction_hex = l
            if instruction_hex != '' and not instruction_hex.isspace():
                pre_result.append(disassembly_line(index, instruction_hex))

    make_label(pre_result)

    for index, i in enumerate(pre_result):
        result.append(' '.join(i))

    return result


def main():
    result = []

    with open('233', 'r') as f:
        for index, l in enumerate(f.readlines()):
            instruction_hex = l.strip('\n')
            if instruction_hex != '' and not instruction_hex.isspace():
                result.append(disassembly_line(index, instruction_hex))

    print(label_table)
    make_label(result)
    print(result)
    for index, i in enumerate(result):
        print(index + 1, ' '.join(i))


if __name__ == "__main__":
    main()

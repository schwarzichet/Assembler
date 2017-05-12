import re

from instructions import R_TYPE, I_TYPE, J_TYPE, R_instruction, J_instruction, I_instruction
from instructions import label_table


def parser(instruction_string, address):
    results = {'address': address, 'instruction_string': instruction_string}
    parts = re.split(r'[(),\s]\s*', instruction_string)
    parts = list(filter(None, parts))
    results['name'] = parts[0]

    name = results['name']
    for type_name, instruction_type in {'R': R_TYPE, 'I': I_TYPE, 'J': J_TYPE}.items():
        if name in instruction_type:
            results['type'] = type_name
            for item in instruction_type[name].items():
                if item[0] != 'args':
                    results[item[0]] = item[1]
                else:
                    if len(parts) != len(item[1]) + 1:
                        parts.insert(2, '0')

                    for index, arg in enumerate(item[1]):
                        results[arg] = parts[index + 1]
            break
    else:
        raise Exception('no such instruction : {}'.format(name))

    return results


def add_to_label_table(instruction_string, address):
    if ':' in instruction_string:
        label, inst_without_label = instruction_string.split(':')
        label_table[label] = address
    else:
        inst_without_label = instruction_string
    return inst_without_label


def make_instruction(dictionary):
    if dictionary['type'] == 'R':
        return R_instruction(dictionary)
    elif dictionary['type'] == 'I':
        return I_instruction(dictionary)
    elif dictionary['type'] == 'J':
        return J_instruction(dictionary)
    else:
        return Exception('unknown instruction type {}'.format(dictionary['type_name']))


def filter_comment(line):
    instruction_comment = re.split(r'#|//', line, maxsplit=1)
    return instruction_comment[0]


def assemble(file_address):
    address = 0
    instructions_pure = []
    result = []
    with open(file_address, 'r', encoding='utf8', errors='ignore') as f:
        for line in f.readlines():
            instruction_string = filter_comment(line.strip('\n'))
            if instruction_string != '' and not instruction_string.isspace():
                instructions_pure.append(add_to_label_table(instruction_string, address))
                address += 1

    for index, i in enumerate(instructions_pure):
        dictionary = parser(i, index)
        instruction = make_instruction(dictionary)

        result.append(hex(int(instruction.to_binary(), 2))[2:].zfill(8).upper())
    print('done', flush=True)
    return result


def to_coe(file_address):
    result = ["memory_initialization_radix=16;", "memory_initialization_vector="]
    hexes = assemble(file_address)
    print(hexes)
    for i in range(len(hexes)):
        if i != len(hexes) - 1:
            hexes[i] += ','
        if (i + 1) % 8 == 0:
            hexes[i] += '\n'

    result.append(''.join(hexes) + ';')
    return result


def main():
    address = 0
    instructions_pure = []
    with open('test.asm', 'r', encoding='utf8', errors='ignore') as f:
        for line in f.readlines():

            instruction_string = filter_comment(line.strip('\n'))
            if instruction_string != '' and not instruction_string.isspace():
                instructions_pure.append(add_to_label_table(instruction_string, address))
                address += 1

    print(label_table)

    result = []
    for index, i in enumerate(instructions_pure):
        # print(index, i)
        dictionary = parser(i, index)
        instruction = make_instruction(dictionary)

        print(str(index + 1).zfill(2), hex(int(instruction.to_binary(), 2))[2:].zfill(8), i)
        result.append(hex(int(instruction.to_binary(), 2))[2:].zfill(8))
        # print(hex(int(instruction.to_binary(), 2))[2:].zfill(8))

        # with open('correct', 'r', encoding='utf8', errors='ignore') as f:
        #     i = 0
        #     for line in f.readlines():
        #         if result[i] != line.strip('\n').lower():
        #             print(i)
        #         i += 1


if __name__ == '__main__':
    main()

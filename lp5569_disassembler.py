class LP5569Disassembler:
    VARS = ['ra', 'rb', 'rc', 'rd']
    FORMATS = {
        'ramp': ''
    }
    def __init__(self):
        pass

    def disassemble(self, program):
        disassembly = []
        pc = 0
        prog = program
        while len(prog) > 0:
            word = prog[0:2]
            if word[0] & 0x80 == 0:
                # ramp, wait, set_pwm, or rst instruction
                prescale = (word[0] & 0x40 != 0)
                sign = word[0] & 0x1
                step_time = (word[0] & 0x3F) >> 1
                if not prescale and step_time == 0 and sign == 0 and word[1] == 0:
                    disassembly.append({
                        'pc': pc,
                        'instruction': 'rst'
                    })
                elif prescale and step_time == 0 and sign == 0 and word[1] != 0:
                    disassembly.append({
                        'pc': pc,
                        'instruction': 'set_pwm',
                        'arguments': [word[1]]
                    })
                elif sign == 0 and word[1] == 0:
                    disassembly.append({
                        'pc': pc,
                        'instruction': 'wait',
                        'prescale': prescale,
                        'arguments': [step_time]
                    })
                else:
                    disassembly.append({
                        'pc': pc,
                        'instruction': 'ramp',
                        'prescale': prescale,
                        'sign': sign,
                        'arguments': [step_time, word[1]]
                    })
            else:
                # other instruction
                if word[0] == 0b10000100:
                    # ramp or set_pwm with variable
                    prescale = (((word[1] & 0x20) >> 5) != 0)
                    sign = (word[1] & 0x10) >> 4
                    step_time = (word[1] & 0xC) >> 2
                    num_increments = (word[1] & 0x3)
                    if word[0] & 0x40 == 0:
                        # ramp with a variable
                        disassembly.append({
                            'pc': pc,
                            'instruction': 'ramp',
                            'prescale': prescale,
                            'sign': sign,
                            'arguments': [self.VARS[step_time], self.VARS[num_increments]]
                        })
                    else:
                        # set_pwm with a variable
                        disassembly.append({
                            'pc': pc,
                            'instruction': 'set_pwm',
                            'arguments': [self.VARS[num_increments]]
                        })
                elif word[0] == 0b10011110:
                    disassembly.append({
                        'pc': pc,
                        'instruction': 'load_start',
                        'arguments': [word[1]]
                    })
                elif word[0] == 0b10011100:
                    if word[1] & 0x80 == 0:
                        disassembly.append({
                            'pc': pc,
                            'instruction': 'map_start',
                            'arguments': [word[1]]
                        })
                    else:
                        disassembly.append({
                            'pc': pc,
                            'instruction': 'load_end',
                            'arguments': [word[1] & 0x7F]
                        })
                elif word[0] == 0b10011101:
                    if word[1] & 0x80 == 0:
                        if word[1] == 0:
                            disassembly.append({
                                'pc': pc,
                                'instruction': 'map_clr'
                            })
                        else:
                            disassembly.append({
                                'pc': pc,
                                'instruction': 'map_sel',
                                'arguments': [word[1]]
                            })
                    else:
                        if word[1] == 0b10000000:
                            disassembly.append({
                                'pc': pc,
                                'instruction': 'map_next'
                            })
                        elif word[1] == 0b11000000:
                            disassembly.append({
                                'pc': pc,
                                'instruction': 'map_prev'
                            })
                        elif word[1] == 0b10000001:
                            disassembly.append({
                                'pc': pc,
                                'instruction': 'load_next'
                            })
                        elif word[1] == 0b11000001:
                            disassembly.append({
                                'pc': pc,
                                'instruction': 'load_prev'
                            })
                elif word[0] == 0b10011111:
                    if word[1] & 0x80 == 0:
                        disassembly.append({
                            'pc': pc,
                            'instruction': 'load_addr',
                            'arguments': [word[1]]
                        })
                    else:
                        disassembly.append({
                            'pc': pc,
                            'instruction': 'map_addr',
                            'arguments': [word[1] & 0x7F]
                        })
                elif (word[0] & 0xA0) == 0xA0:
                    # Branch with literal
                    loop_count = ((word[0] & 0x1F) << 1) | (word[1] & 0x80) >> 7
                    step_number = word[1] & 0x7F
                    disassembly.append({
                        'pc': pc,
                        'instruction': 'branch',
                        'arguments': [loop_count, step_number]
                    })
                elif (word[0] & 0xFE) == 0b10000110:
                    # Branch with variable
                    step_number = ((word[0] & 0x1) << 6) | ((word[1] & 0xFC) >> 2)
                    loop_count = (self.VARS[word[1] & 0x3])
                    disassembly.append({
                        'pc': pc,
                        'instruction': 'branch',
                        'arguments': [loop_count, step_number]
                    })
                else:
                    # Unknown instruction
                    disassembly.append({
                        'pc': pc,
                        'instruction': 'UNKNOWN ({0:#010b} {1:#010b})'.format(word[0], word[1]),
                    })
            prog = prog[2:]
            pc += 1
        return disassembly

if __name__ == '__main__':
    prog = [
        0x9c, 0x10,
        0x9c, 0x9f,
        0x06, 0xff,
        0x02, 0x00,
        0x07, 0xff,
        0x9d, 0x80,
        0xa0, 0x02,
        0x00, 0x0a,
        0x00, 0x05,
        0x00, 0x0a,
        0x00, 0x05,
        0x00, 0x0a,
        0x00, 0x05,
        0x00, 0x0a,
        0x00, 0x05,
        0x00, 0x0a,
        0x00, 0x01,
        0x00, 0x02,
        0x00, 0x40,
        0x00, 0x04,
        0x00, 0x08,
        0x00, 0x80,
        0x00, 0x10,
        0x00, 0x20,
        0x01, 0x00,
        0x00, 0x20,
        0x00, 0x10,
        0x00, 0x80,
        0x00, 0x08,
        0x00, 0x04,
        0x00, 0x40,
        0x00, 0x02,
    ]
    da = LP5569Disassembler()
    dis_prog = da.disassemble(prog)
    for inst in dis_prog:
        print(repr(inst))
        #"{0:#04x}          {1:10s}  ".format(inst)
    print(repr(dis_prog))
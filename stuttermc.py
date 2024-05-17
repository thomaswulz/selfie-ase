import sys
import subprocess
from itertools import permutations


def generate_bits(cur, ones, zeros, result):
    if ones == 0:
        result.append('0' * (zeros - 1) + cur)
    elif zeros == 0:
        result.append('1' * (ones - 1) + cur)
    else:
        generate_bits('0' + cur, ones, zeros - 1, result)
        generate_bits('1' + cur, ones - 1, zeros, result)


def main():
    if len(sys.argv) < 2:
        print("Usage: " + sys.argv[0] + " [args] filename.btor2")
        sys.exit(1)

    filename = sys.argv[-1]

    # check if last argument looks like a model file
    if not filename.endswith(".btor2"):
        print("Error: Last argument must be a .btor2 file")
        sys.exit(1)

    # read model lines into list
    with open(filename, "r") as f:
        lines = f.read().split('\n')

    bitvec_sorts = {}

    stutter_line = 0
    stutter_nid = 0
    stutter_sid = 0

    for i in range(len(lines)):
        split = lines[i].split(' ')

        # collect bit vector sids along with their sizes
        if len(split) >= 4 and split[1] == 'sort' and split[2] == 'bitvec':
            sid = int(split[0])
            size = int(split[3])
            bitvec_sorts[sid] = size

        # find line defining stutter state
        elif len(split) >= 4 and split[1] == 'state' and split[3] == 'stutter-bits':
            nid = int(split[0])
            sid = int(split[2])

            stutter_line = i
            stutter_nid = nid
            stutter_sid = sid

        # comment out "next" line
        elif stutter_line != 0 and len(split) >= 5 and split[1] == 'next' and int(split[3]) == stutter_nid:
            lines[i] = '; ' + lines[i]
            break

    if i == len(lines) - 1:
        raise Exception("Failed to parse file, does it contain stutter bits?")

    # pass remaining args through to btormc
    btormc_args = sys.argv[1:-1]  # Exclude the last argument (filename)
    btormc_cmd = ["btormc"] + btormc_args

    # get number of stutter bits in model
    num_bits = bitvec_sorts[stutter_sid]

    # generate stutter bit vectors corresponding to all unique interleavings
    all_bits = list()
    each_bits = (num_bits + 1) // 2
    generate_bits('', each_bits, each_bits, all_bits)

    for bits in all_bits:
        # print(bits)

        # set concrete stutter bits in model
        lines[stutter_line] = f'{stutter_nid} const {stutter_sid} {bits} ; concrete stutter bits'

        # run btormc with model on stdin
        btormc_process = subprocess.Popen(btormc_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE, text=True)
        stdout, stderr = btormc_process.communicate('\n'.join(lines))

        if not stdout.startswith('sat'):
            # not sat, so just go to next bit vector
            continue

        # print the stutter bits
        print(f'{bits} stutter-bits')

        # print solver output
        print(stdout)

        # found bits that lead to sat, so we can terminate
        exit(0)

    # none of the bit vectors led to sat, so the model is unsat
    print("unsat")
    exit(1)


if __name__ == "__main__":
    main()

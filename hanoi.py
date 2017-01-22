def isDifferent(pair):
    a1, a2 = pair
    return a1 != a2


def lmap(func, *iterable):
    return list(map(func, *iterable))


def lfilter(func, *iterable):
    return list(filter(func, *iterable))


def move_no_empty(disc, peg1, peg2, d_on1, d_on2):
    args = {'disc': disc, 'peg1': peg1,
            'd_on1': d_on1, 'peg2': peg2, 'd_on2': d_on2}
    s_name = "Name: m_{disc}_{peg1}_on_{d_on1}_{peg2}_on_{d_on2}\n".format(
        **args)
    s_pre = "pre: {disc}_at_{peg1} {disc}_top {disc}_on_{d_on1} {d_on2}_at_{peg2} {d_on2}_top\n".format(
        **args)
    s_add = "add: {disc}_at_{peg2} {disc}_on_{d_on2} {d_on1}_top\n".format(
        **args)
    s_del = "del: {disc}_at_{peg1} {disc}_on_{d_on1} {d_on2}_top\n".format(
        **args)
    return (s_name + s_pre + s_add + s_del)


def move_to_empty(disc, peg1, peg2, d_on1):
    args = {'disc': disc, 'peg1': peg1,
            'd_on1': d_on1, 'peg2': peg2}
    s_name = "Name: m_{disc}_{peg1}_on_{d_on1}_{peg2}\n".format(
        **args)
    s_pre = "pre: {disc}_at_{peg1} {disc}_top {disc}_on_{d_on1} {peg2}_empty\n".format(
        **args)
    s_add = "add: {disc}_at_{peg2} {disc}_bottom {d_on1}_top\n".format(
        **args)
    s_del = "del: {disc}_at_{peg1} {disc}_on_{d_on1} {peg2}_empty\n".format(
        **args)
    return (s_name + s_pre + s_add + s_del)


def move_from_single(disc, peg1, peg2, d_on1):
    args = {'disc': disc, 'peg1': peg1,
            'd_on1': d_on1, 'peg2': peg2}
    s_name = "Name: m_{disc}_{peg1}_{peg2}_on_{d_on1}\n".format(
        **args)
    s_pre = "pre: {disc}_at_{peg1} {disc}_top {disc}_bottom {d_on1}_at_{peg2} {d_on1}_top\n".format(
        **args)
    s_add = "add: {disc}_at_{peg2} {disc}_on_{d_on1} {peg1}_empty\n".format(
        **args)
    s_del = "del: {disc}_at_{peg1} {disc}_bottom {d_on1}_top\n".format(
        **args)
    return (s_name + s_pre + s_add + s_del)

def move_from_single_to_empty(disc, peg1, peg2):
    args = {'disc': disc, 'peg1': peg1, 'peg2': peg2}
    s_name = "Name: m_{disc}_{peg1}_{peg2}\n".format(
        **args)
    s_pre = "pre: {disc}_at_{peg1} {disc}_top {disc}_bottom {peg2}_empty\n".format(
        **args)
    s_add = "add: {disc}_at_{peg2} {peg1}_empty\n".format(
        **args)
    s_del = "del: {disc}_at_{peg1} {peg2}_empty\n".format(
        **args)
    return (s_name + s_pre + s_add + s_del)

def createDomainFile(domainFileName, n):
    numbers = list(range(n))  # [0,...,n-1]
    pegs = ['a', 'b', 'c']
    # use domain_file.write(str) to write to domain_file
    domain_file = open(domainFileName, 'w')

    # Propositions
    domain_file.write("Propositions:\n")

    disc_on_disc = ["{}_on_{}".format(d1, d2)
                    for d1 in numbers
                    for d2 in numbers if d1 < d2]
    disc_loc = ["{}_at_{}".format(d, p)
                for d in numbers
                for p in pegs]
    disc_top = ["{}_top".format(d) for d in numbers]
    disc_bottom = ["{}_bottom".format(d) for d in numbers]
    pegs_empty = ["a_empty", "b_empty", "c_empty"]

    lmap(lambda s: domain_file.write(s + ' '), disc_on_disc)
    lmap(lambda s: domain_file.write(s + ' '), disc_loc)
    lmap(lambda s: domain_file.write(s + ' '), disc_top)
    lmap(lambda s: domain_file.write(s + ' '), disc_bottom)
    lmap(lambda s: domain_file.write(s + ' '), pegs_empty)

    # Actions
    domain_file.write("\nActions:\n")

    actions_move_no_empty = [move_no_empty(disc, peg1, peg2, d_on1, d_on2)
                             for disc in numbers
                             for peg1 in pegs
                             for peg2 in pegs if (peg1 != peg2)
                             for d_on1 in numbers if (disc < d_on1)
                             for d_on2 in numbers if (d_on1 != d_on2) and (disc < d_on2)]
    actions_move_to_empty = [move_to_empty(disc, peg1, peg2, d_on1)
                             for disc in numbers
                             for peg1 in pegs
                             for peg2 in pegs if (peg1 != peg2)
                             for d_on1 in numbers if (disc < d_on1)]
    actions_move_from_single = [move_from_single(disc, peg1, peg2, d_on1)
                                for disc in numbers
                                for peg1 in pegs
                                for peg2 in pegs if (peg1 != peg2)
                                for d_on1 in numbers if (disc < d_on1)]
    actions_move_from_single_to_empty = [move_from_single_to_empty(disc, peg1, peg2)
                                for disc in numbers
                                for peg1 in pegs
                                for peg2 in pegs if (peg1 != peg2)]

    lmap(domain_file.write, actions_move_no_empty)
    lmap(domain_file.write, actions_move_to_empty)
    lmap(domain_file.write, actions_move_from_single)
    lmap(domain_file.write, actions_move_from_single_to_empty)

    domain_file.close()


def createProblemFile(problemFileName, n):
    numbers = list(range(n))
    pegs = ['a', 'b', 'c']
    # use problem_file.write(str) to write to problem_file
    problem_file = open(problemFileName, 'w')

    disc_on_disc = ["{}_on_{}".format(d1, d2)
                    for d1 in numbers
                    for d2 in numbers if (d1 == d2 - 1)]
    disc_loc = ["{}_at_a".format(d) for d in numbers]
    disc_top = ["0_top"]
    disc_bottom = ["{}_bottom".format(n - 1)]
    pegs_empty = ["b_empty", "c_empty"]

    problem_file.write("Initial state: ")
    lmap(lambda s: problem_file.write(s + ' '), disc_on_disc)
    lmap(lambda s: problem_file.write(s + ' '), disc_loc)
    lmap(lambda s: problem_file.write(s + ' '), disc_top)
    lmap(lambda s: problem_file.write(s + ' '), disc_bottom)
    lmap(lambda s: problem_file.write(s + ' '), pegs_empty)

    disc_loc = ["{}_at_c".format(d) for d in numbers]
    pegs_empty = ["a_empty", "b_empty"]

    problem_file.write("\nGoal state: ")
    lmap(lambda s: problem_file.write(s + ' '), disc_on_disc)
    lmap(lambda s: problem_file.write(s + ' '), disc_loc)
    lmap(lambda s: problem_file.write(s + ' '), disc_top)
    lmap(lambda s: problem_file.write(s + ' '), disc_bottom)
    lmap(lambda s: problem_file.write(s + ' '), pegs_empty)

    problem_file.close()


import sys

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: hanoi.py n')
        sys.exit(2)

    n = int(float(sys.argv[1]))  # number of disks
    domainFileName = 'hanoi' + str(n) + 'Domain.txt'
    problemFileName = 'hanoi' + str(n) + 'Problem.txt'

    createDomainFile(domainFileName, n)
    createProblemFile(problemFileName, n)

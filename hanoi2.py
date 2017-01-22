def createDomainFile(domainFileName, n):
    numbers = list(range(n))  # [0,...,n-1]
    pegs = ['a', 'b', 'c']
    domain_file = open(domainFileName, 'w')  # use domain_file.write(str) to write to domain_file

    domain_file.write("Propositions:\n")
    for disc in numbers:
        for next_disc in numbers[disc+1:]:
            domain_file.write(str(disc)+"o"+str(next_disc)+" ")
        domain_file.write('g'+str(disc)+" t"+str(disc)+" ")
        for peg in pegs:
            domain_file.write(peg+str(disc)+" ")

    domain_file.write("ae be ce\n")
    domain_file.write("Actions:\n")


    for curr_peg in pegs:
        for next_peg in pegs:
            if curr_peg == next_peg:
                continue

            for curr_disc in numbers:
                curr_s = str(curr_disc)

                for prev_supporting in numbers[curr_disc + 1:]:
                    prev_s = str(prev_supporting)

                    for next_supporting in numbers[curr_disc + 1:]:
                        if prev_supporting == next_supporting:
                            continue

                        next_s = str(next_supporting)

                        # Move from resting on prev to resting on next
                        name = ['M', curr_s, curr_peg + prev_s, next_peg + next_s]
                        pre_props = [curr_peg + curr_s, 't' + curr_s, curr_s + 'o' + prev_s,
                                     't' + next_s, next_peg + next_s]
                        add_props = [next_peg + curr_s, curr_s + 'o' + next_s, 't' + prev_s]
                        del_props = [curr_peg + curr_s, curr_s + 'o' + prev_s, 't' + next_s]

                        write_action(name, pre_props, del_props, add_props, domain_file)

                    # Move from resting on ground to resting on next
                    name = ['M', curr_s, curr_peg, next_peg + prev_s]
                    pre_props = [curr_peg + curr_s, 't' + curr_s, 'g' + curr_s,
                                 't' + prev_s, next_peg + prev_s]
                    add_props = [next_peg + curr_s, curr_s + 'o' + prev_s, curr_peg + 'e']
                    del_props = [curr_peg + curr_s, 'g' + curr_s, 't' + prev_s]

                    write_action(name, pre_props, del_props, add_props, domain_file)

                    # Move from resting on prev to resting on ground
                    name = ['M', curr_s, curr_peg + prev_s, next_peg]
                    pre_props = [curr_peg + curr_s, curr_peg + prev_s, 't' + curr_s,
                                 curr_s + 'o' + prev_s, next_peg + 'e']
                    add_props = [next_peg + curr_s, 'g' + curr_s, 't' + prev_s]
                    del_props = [curr_peg + curr_s, curr_s + 'o' + prev_s, next_peg + 'e']

                    write_action(name, pre_props, del_props, add_props, domain_file)

                # Move from resting on ground to resting on ground
                name = ['M', curr_s, curr_peg, next_peg]
                pre_props = [curr_peg + curr_s, 'g' + curr_s, 't' + curr_s, next_peg + 'e']
                add_props = [next_peg + curr_s, curr_peg+'e']
                del_props = [curr_peg + curr_s, next_peg + 'e']

                write_action(name, pre_props, del_props, add_props, domain_file)

    domain_file.close()


# t - top. t16
# a\b\c - peg. b7
# o - on. 7o12
# g - ground. g6
# M - move. M-1-a2-b3: move disc 1 from resting on 2 in a to resting on 3 in b


def write_action(name, pre_props, del_props, add_props, file):
    file.write("Name: " + "-".join(name) + "\n")
    file.write("pre: " + " ".join(pre_props) + "\n")
    file.write("add: " + " ".join(add_props) + "\n")
    file.write("delete: " + " ".join(del_props) + "\n")


def createProblemFile(problemFileName, n):
    numbers = list(range(n))
    pegs = ['a', 'b', 'c']
    problem_file = open(problemFileName, 'w')  # use problem_file.write(str) to write to problem_file

    problem_file.write("Initial state:")
    for i in range(n):
        problem_file.write(" a"+str(i))
        if i < n-1:
            problem_file.write(" "+str(i)+'o'+str(i+1))

    problem_file.write(" be ce g"+str(n-1)+" t0\n")

    problem_file.write("Goal state:")
    for i in range(n):
        problem_file.write(" c"+str(i))
        if i < n-1:
            problem_file.write(" "+str(i)+'o'+str(i+1))

    problem_file.write(" be ae g"+str(n-1)+" t0")

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

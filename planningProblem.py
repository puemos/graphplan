from util import Pair
import copy
from propositionLayer import PropositionLayer
from planGraphLevel import PlanGraphLevel
from Parser import Parser
from action import Action

try:
    from search import SearchProblem
    from search import aStarSearch

except:
    from CPF.search import SearchProblem
    from CPF.search import aStarSearch


def isDifferent(pair):
    a1, a2 = pair
    return a1 != a2


def lmap(func, *iterable):
    return list(map(func, *iterable))


def lfilter(func, *iterable):
    return list(filter(func, *iterable))


class PlanningProblem():

    def __init__(self, domain, problem):
        """
        Constructor
        """
        p = Parser(domain, problem)
        self.actions, self.propositions = p.parseActionsAndPropositions()
        # list of all the actions and list of all the propositions
        self.initialState, self.goal = p.pasreProblem()
        # the initial state and the goal state are lists of propositions
        # creates noOps that are used to propagate existing propositions from
        # one layer to the next
        self.createNoOps()
        PlanGraphLevel.setActions(self.actions)
        PlanGraphLevel.setProps(self.propositions)
        self._expanded = 0

    def getStartState(self):
        return self.initialState

    def isGoalState(self, state):
        """
        Hint: you might want to take a look at goalStateNotInPropLayer function
        """
        return not self.goalStateNotInPropLayer(state)

    def getSuccessors(self, state):
        """
        For a given state, this should return a list of triples,
        (successor, action, stepCost), where 'successor' is a
        successor to the current state, 'action' is the action
        required to get there, and 'stepCost' is the incremental
        cost of expanding to that successor, 1 in our case.
        You might want to this function:
        For a list of propositions l and action a,
        a.allPrecondsInList(l) returns true if the preconditions of a are in l
        """

        def allPrecondsInList(action, propositions):
            for pre in action.getPre():
                if pre not in propositions:
                    return False
            return True

        successors = []
        step_cost = 1

        self._expanded += 1

        # get all possible actions
        for action in self.actions:
            if (not action.isNoOp()) and allPrecondsInList(action, state):
                # add all the positives
                successor = state + \
                    [p for p in action.getAdd() if p not in state]
                # remove all the negatives
                successor = [
                    p for p in successor if p not in action.getDelete()]

                successors.append((successor, action, step_cost))
        return successors


    def getCostOfActions(self, actions):
        return len(actions)

    def goalStateNotInPropLayer(self, propositions):
        """
        Helper function that returns true if all the goal propositions
        are in propositions
        """
        for goal in self.goal:
            if goal not in propositions:
                return True
        return False

    def createNoOps(self):
        """
        Creates the noOps that are used to propagate propositions from one layer to the next
        """
        for prop in self.propositions:
            name = prop.name
            precon = []
            add = []
            precon.append(prop)
            add.append(prop)
            delete = []
            act = Action(name, precon, add, delete, True)
            self.actions.append(act)


def maxLevel(state, problem):
    """
    The heuristic value is the number of layers required to expand all goal propositions.
    If the goal is not reachable from the state your heuristic should return float('inf')
    A good place to start would be:
    propLayerInit = PropositionLayer()          #create a new proposition layer
    for prop in state:
      #update the proposition layer with the propositions of the state
      propLayerInit.addProposition(prop)
    # create a new plan graph level (level is the action layer and the
    # propositions layer)
    pgInit = PlanGraphLevel()
    #update the new plan graph level with the the proposition layer
    pgInit.setPropositionLayer(propLayerInit)
    """
    def nextPlan(plan):
        next_plan = PlanGraphLevel()
        next_plan.expandWithoutMutex(plan)
        return next_plan, next_plan.getPropositionLayer().getPropositions()

    propLayerInit = PropositionLayer()
    # add all to the new proposition layer
    lmap(propLayerInit.addProposition, state)

    plan = PlanGraphLevel()
    plan.setPropositionLayer(propLayerInit)
    plan_propositions = plan.getPropositionLayer().getPropositions()

    # create a graph that will store all the plan levels
    graph = []
    graph.append(plan)

    # if we found we can rest
    while not problem.isGoalState(plan_propositions):
        # if fixed we won't have a solution
        if isFixed(graph, len(graph) - 1):
            return float('inf')
        # create the next plan by the prev
        plan, plan_propositions = nextPlan(plan)
        # store in the graph
        graph.append(plan)

    return len(graph) - 1


def levelSum(state, problem):
    """
    The heuristic value is the sum of sub-goals level they first appeared.
    If the goal is not reachable from the state your heuristic should return float('inf')
    """
    def nextPlan(plan):
        next_plan = PlanGraphLevel()
        next_plan.expandWithoutMutex(plan)
        return next_plan, next_plan.getPropositionLayer().getPropositions()

    propLayerInit = PropositionLayer()
    # add all to the new proposition layer
    lmap(propLayerInit.addProposition, state)

    plan = PlanGraphLevel()
    plan.setPropositionLayer(propLayerInit)
    plan_propositions = plan.getPropositionLayer().getPropositions()

    # create a graph that will store all the plan levels
    graph = []
    graph.append(plan)

    goals_levels = dict()
    goal = problem.goal

    # init goals levels
    for p in goal:
        goals_levels[p.getName()] = None

    # as long as we have for one of the goal None we didnt find the first level
    while None in goals_levels.values():
        # if fixed we won't have a solution
        if isFixed(graph, len(graph) - 1):
            return float('inf')
        # for each prop in the goal check if exist on the current plan
        # propositions
        for p in goal:
            # check that we didnt assign a value yet
            if p in plan_propositions and goals_levels[p.getName()] == None:
                # set the current level as the fist appearance of the prop
                goals_levels[p.getName()] = len(graph) - 1
        # create the next plan by the prev
        plan, plan_propositions = nextPlan(plan)
        # store in the graph
        graph.append(plan)

    return sum(goals_levels.values())


def isFixed(Graph, level):
    """
    Checks if we have reached a fixed point,
    i.e. each level we'll expand would be the same, thus no point in continuing
    """
    if level == 0:
        return False
    return len(Graph[level].getPropositionLayer().getPropositions()) == len(Graph[level - 1].getPropositionLayer().getPropositions())

if __name__ == '__main__':
    import sys
    import time
    if len(sys.argv) != 1 and len(sys.argv) != 4:
        print("Usage: PlanningProblem.py domainName problemName heuristicName(max, sum or zero)")
        exit()
    domain = 'dwrDomain.txt'
    problem = 'dwrProblem.txt'
    heuristic = lambda x, y: 0
    if len(sys.argv) == 4:
        domain = str(sys.argv[1])
        problem = str(sys.argv[2])
        if str(sys.argv[3]) == 'max':
            heuristic = maxLevel
        elif str(sys.argv[3]) == 'sum':
            heuristic = levelSum
        elif str(sys.argv[3]) == 'zero':
            heuristic = lambda x, y: 0
        else:
            print(
                "Usage: PlanningProblem.py domainName problemName heuristicName(max, sum or zero)")
            exit()

    prob = PlanningProblem(domain, problem)
    start = time.clock()
    plan = aStarSearch(prob, heuristic)
    elapsed = time.clock() - start
    if plan is not None:
        print("Plan found with %d actions in %.2f seconds" %
              (len(plan), elapsed))
    else:
        print("Could not find a plan in %.2f seconds" % elapsed)
    print("Search nodes expanded: %d" % prob._expanded)

from util import Pair
import copy
from propositionLayer import PropositionLayer
from planGraphLevel import PlanGraphLevel
from action import Action
from Parser import Parser


class GraphPlan(object):
    """
    A class for initializing and running the graphplan algorithm
    """

    def __init__(self, domain, problem):
        """
        Constructor
        """
        self.independentActions = []
        self.noGoods = []
        self.graph = []
        p = Parser(domain, problem)
        # list of all the actions and list of all the propositions
        self.actions, self.propositions = p.parseActionsAndPropositions()
        # the initial state and the goal state are lists of propositions
        self.initialState, self.goal = p.pasreProblem()
        # creates noOps that are used to propagate existing propositions from
        # one layer to the next
        self.createNoOps()
        # creates independent actions list and updates self.independentActions
        self.independent()
        PlanGraphLevel.setIndependentActions(self.independentActions)
        PlanGraphLevel.setActions(self.actions)
        PlanGraphLevel.setProps(self.propositions)

    def graphPlan(self):
        """
        The graphplan algorithm.
        The code calls the extract function which you should complete below
        """
        # initialization
        initState = self.initialState
        level = 0
        self.noGoods = []  # make sure you update noGoods in your backward search!
        self.noGoods.append([])
        # create first layer of the graph, note it only has a proposition layer
        # which consists of the initial state.
        propLayerInit = PropositionLayer()
        for prop in initState:
            propLayerInit.addProposition(prop)
        pgInit = PlanGraphLevel()
        pgInit.setPropositionLayer(propLayerInit)
        self.graph.append(pgInit)

        """
    While the layer does not contain all of the propositions in the goal state,
    or some of these propositions are mutex in the layer we,
    and we have not reached the fixed point, continue expanding the graph
    """

        while self.goalStateNotInPropLayer(self.graph[level].getPropositionLayer().getPropositions()) or \
                self.goalStateHasMutex(self.graph[level].getPropositionLayer()):
            if self.isFixed(level):
                return None  # this means we stopped the while loop above because we reached a fixed point in the graph. nothing more to do, we failed!

            self.noGoods.append([])
            level = level + 1
            pgNext = PlanGraphLevel()  # create new PlanGraph object
            # calls the expand function, which you are implementing in the
            # PlanGraph class
            pgNext.expand(self.graph[level - 1])
            # appending the new level to the plan graph
            self.graph.append(pgNext)

            # remember size of nogood table
            sizeNoGood = len(self.noGoods[level])

        # try to extract a plan since all of the goal propositions are in
        # current graph level, and are not mutex
        plan = self.extract(self.graph, self.goal, level)
        while(plan is None):  # while we didn't extract a plan successfully
            level = level + 1
            self.noGoods.append([])
            pgNext = PlanGraphLevel()  # create next level of the graph by expanding
            # create next level of the graph by expanding
            pgNext.expand(self.graph[level - 1])
            self.graph.append(pgNext)
            # try to extract a plan again
            plan = self.extract(self.graph, self.goal, level)
            if (plan is None and self.isFixed(level)):  # if failed and reached fixed point
                # if size of nogood didn't change, means there's nothing more
                # to do. We failed.
                if sizeNoGood == len(self.noGoods[level]):
                    return None
                # we didn't fail yet! update size of no good
                sizeNoGood = len(self.noGoods[level])
        return plan

    def extract(self, Graph, subGoals, level):
        """
        The backsearch part of graphplan that tries
        to extract a plan when all goal propositions exist in a graph plan level.
        """

        if level == 0:
            return []
        if subGoals in self.noGoods[level]:
            return None
        plan = self.gpSearch(Graph, subGoals, [], level)
        if plan is not None:
            return plan
        self.noGoods[level].append([subGoals])
        return None

    def gpSearch(self, Graph, subGoals, plan, level):
        if subGoals == []:
            newGoals = []
            for action in plan:
                for prop in action.getPre():
                    if prop not in newGoals:
                        newGoals.append(prop)
            newPlan = self.extract(Graph, newGoals, level - 1)
            if newPlan is None:
                return None
            else:
                return newPlan + plan

        prop = subGoals[0]
        providers = []
        for action1 in [act for act in Graph[level].getActionLayer().getActions() if prop in act.getAdd()]:
            noMutex = True
            for action2 in plan:
                if Pair(action1, action2) not in self.independentActions:
                    noMutex = False
                    break
            if noMutex:
                providers.append(action1)
        for action in providers:
            newSubGoals = [g for g in subGoals if g not in action.getAdd()]
            planClone = list(plan)
            planClone.append(action)
            newPlan = self.gpSearch(Graph, newSubGoals, planClone, level)
            if newPlan is not None:
                return newPlan
        return None

    def goalStateNotInPropLayer(self, propositions):
        """
        Helper function that receives a  list of propositions (propositions) and returns true
        if not all the goal propositions are in that list
        """
        for goal in self.goal:
            if goal not in propositions:
                return True
        return False

    def goalStateHasMutex(self, propLayer):
        """
        Helper function that checks whether all goal propositions are non mutex at the current graph level
        """
        for goal1 in self.goal:
            for goal2 in self.goal:
                if propLayer.isMutex(goal1, goal2):
                    return True
        return False

    def isFixed(self, level):
        """
        Checks if we have reached a fixed point, i.e. each level we'll expand would be the same, thus no point in continuing
        """
        if level == 0:
            return False

        if len(self.graph[level].getPropositionLayer().getPropositions()) == len(self.graph[level - 1].getPropositionLayer().getPropositions()) and \
                len(self.graph[level].getPropositionLayer().getMutexProps()) == len(self.graph[level - 1].getPropositionLayer().getMutexProps()):
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
            prop.addProducer(act)

    def independent(self):
        """
        Creates a list of independent actions
        """
        for act1 in self.actions:
            for act2 in self.actions:
                if independentPair(act1, act2):
                    self.independentActions.append(Pair(act1, act2))

    def isIndependent(self, a1, a2):
        return Pair(a1, a2) in self.independentActions

    def noMutexActionInPlan(self, plan, act, actionLayer):
        """
        Helper action that you may want to use when extracting plans,
        returns true if there are no mutex actions in the plan
        """
        for planAct in plan:
            if actionLayer.isMutex(Pair(planAct, act)):
                return False
        return True


def independentPair(a1, a2):
    if a1 == a2:
        return True

    def is_pre_or_pos_cond_of(action):
        return lambda condition: action.isPreCond(condition) or action.isPosEffect(condition)

    conds1 = a1.getDelete()
    conds2 = a2.getDelete()

    # check if one of action pre-conditions are pre of pos condition of other
    # action
    conds_a1_action_a2 = any(list(map(is_pre_or_pos_cond_of(a2), conds1)))
    conds_a2_action_a1 = any(list(map(is_pre_or_pos_cond_of(a1), conds2)))
    return (conds_a1_action_a2 is False) and (conds_a2_action_a1 is False)

if __name__ == '__main__':
    import sys
    import time
    if len(sys.argv) != 1 and len(sys.argv) != 3:
        print("Usage: GraphPlan.py domainName problemName")
        exit()
    domain = 'dwrDomain.txt'
    problem = 'dwrProblem.txt'
    if len(sys.argv) == 3:
        domain = str(sys.argv[1])
        problem = str(sys.argv[2])

    gp = GraphPlan(domain, problem)
    start = time.clock()
    plan = gp.graphPlan()
    elapsed = time.clock() - start
    if plan is not None:
        print("Plan found with %d actions in %.2f seconds" %
              (len([act for act in plan if not act.isNoOp()]), elapsed))
    else:
        print("Could not find a plan in %.2f seconds" % elapsed)

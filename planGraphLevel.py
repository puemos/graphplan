from action import Action
from actionLayer import ActionLayer
from util import Pair
from proposition import Proposition
from propositionLayer import PropositionLayer

# Helpers


def isDifferent(pair):
    a1, a2 = pair
    return a1 != a2


def lmap(func, *iterable):
    return list(map(func, *iterable))


def lfilter(func, *iterable):
    return list(filter(func, *iterable))


class PlanGraphLevel(object):
    """
    A class for representing a level in the plan graph.
    For each level i, the PlanGraphLevel consists of the actionLayer and propositionLayer at this level in this order!
    """
    independentActions = []  # updated to the independentActions of the propblem GraphPlan.py line 31
    # updated to the actions of the problem GraphPlan.py line 32 and
    # planningProblem.py line 25
    actions = []
    # updated to the propositions of the problem GraphPlan.py line 33 and
    # planningProblem.py line 26
    props = []

    @staticmethod
    def setIndependentActions(independentActions):
        PlanGraphLevel.independentActions = independentActions

    @staticmethod
    def setActions(actions):
        PlanGraphLevel.actions = actions

    @staticmethod
    def setProps(props):
        PlanGraphLevel.props = props

    def __init__(self):
        """
        Constructor
        """
        self.actionLayer = ActionLayer()    		    # see actionLayer.py
        self.propositionLayer = PropositionLayer()  # see propositionLayer.py

    def getPropositionLayer(self):
        # returns the proposition layer
        return self.propositionLayer

    def setPropositionLayer(self, propLayer):
        # sets the proposition layer
        self.propositionLayer = propLayer

    def getActionLayer(self):
        # returns the action layer
        return self.actionLayer

    def setActionLayer(self, actionLayer):
        # sets the action layer
        self.actionLayer = actionLayer

    def updateActionLayer(self, previousPropositionLayer):
        """
        Updates the action layer given the previous proposition layer (see propositionLayer.py)
        You should add an action to the layer if its preconditions are in the previous propositions layer,
        and the preconditions are not pairwise mutex.
        allAction is the list of all the action (include noOp) in the domain
        You might want to use those functions:
        previousPropositionLayer.isMutex(prop1, prop2) returns true if prop1 and prop2 are mutex at the previous propositions layer
        previousPropositionLayer.allPrecondsInLayer(action) returns true if all the preconditions of action are in the previous propositions layer
        self.actionLayer.addAction(action) adds action to the current action layer
        """
        allActions = PlanGraphLevel.actions

        def isAllPrecondsInLayer(action):
            return previousPropositionLayer.allPrecondsInLayer(action)

        def isPropositionMutex(action):
            # create all the combinations of the actions preconditions
            all_combinations = [(cond1, cond2)
                                for cond1 in action.getPre()
                                for cond2 in action.getPre()]
            # check if exists at least one mutex
            are_any_mutex = any(
                lmap(lambda conds: previousPropositionLayer.isMutex(conds[0], conds[1]),
                     lfilter(isDifferent, all_combinations)))
            # retun if rthere are no mutex
            return not are_any_mutex

        addActionToLayer = self.actionLayer.addAction

        lmap(addActionToLayer,
             lfilter(isPropositionMutex,
                     lfilter(isAllPrecondsInLayer,
                             allActions)))

    def updateMutexActions(self, previousLayerMutexProposition):
        """
        Updates the mutex list in self.actionLayer,
        given the mutex proposition from the previous layer.
        currentLayerActions are the actions in the current action layer
        You might want to use this function:
        self.actionLayer.addMutexActions(action1, action2)
        adds the pair (action1, action2) to the mutex list in the current action layer
        Note that action is *not* mutex with itself
        """
        currentLayerActions = self.actionLayer.getActions()
        # create all the combinations of the actions
        all_combinations = [(action1, action2)
                            for action1 in currentLayerActions
                            for action2 in currentLayerActions]

        def isMutexActions(actions):
            a1, a2 = actions
            return mutexActions(a1, a2, previousLayerMutexProposition)

        def isNotIn(actions):
            a1, a2 = actions
            return Pair(a1, a2) not in self.actionLayer.mutexActions

        def addMutexActions(actions):
            a1, a2 = actions
            self.actionLayer.addMutexActions(a1, a2)

        lmap(addMutexActions,
             lfilter(isNotIn,
                     lfilter(isMutexActions,
                             lfilter(isDifferent, all_combinations))))

    def updatePropositionLayer(self):
        """
        Updates the propositions in the current proposition layer,
        given the current action layer.
        don't forget to update the producers list!
        Note that same proposition in different layers might have different producers lists,
        hence you should create two different instances.
        currentLayerActions is the list of all the actions in the current layer.
        You might want to use those functions:
        dict() creates a new dictionary that might help to keep track on the propositions that you've
               already added to the layer
        self.propositionLayer.addProposition(prop) adds the proposition prop to the current layer

        """
        currentLayerActions = self.actionLayer.getActions()

        def isNotIn(prop):
            return prop not in self.propositionLayer.getPropositions()

        addProposition = self.propositionLayer.addProposition

        for action in currentLayerActions:
            for prop in action.getAdd():
                if isNotIn(prop):
                    addProposition(prop)
                prop.addProducer(action)

    def updateMutexProposition(self):
        """
        updates the mutex propositions in the current proposition layer
        You might want to use those functions:
        mutexPropositions(prop1, prop2, currentLayerMutexActions) returns true if prop1 and prop2 are mutex in the current layer
        self.propositionLayer.addMutexProp(prop1, prop2) adds the pair (prop1, prop2) to the mutex list of the current layer
        """
        currentLayerPropositions = self.propositionLayer.getPropositions()
        currentLayerMutexActions = self.actionLayer.getMutexActions()

        # create all the combinations of the propositions
        all_combinations = [(prop1, prop2)
                            for prop1 in currentLayerPropositions
                            for prop2 in currentLayerPropositions]

        def isMutexPropositions(propositions):
            p1, p2 = propositions
            return mutexPropositions(p1, p2, currentLayerMutexActions)

        def isNotIn(propositions):
            p1, p2 = propositions
            return Pair(p1, p2) not in self.propositionLayer.mutexPropositions

        def addMutexPropositions(propositions):
            p1, p2 = propositions
            return self.propositionLayer.mutexPropositions.append(Pair(p1, p2))

        lmap(addMutexPropositions,
             lfilter(isNotIn,
                     lfilter(isMutexPropositions,
                             lfilter(isDifferent, all_combinations))))

    def expand(self, previousLayer):
        """
        Your algorithm should work as follows:
        First, given the propositions and the list of mutex propositions from the previous layer,
        set the actions in the action layer.
        Then, set the mutex action in the action layer.
        Finally, given all the actions in the current layer,
        set the propositions and their mutex relations in the proposition layer.
        """
        previousPropositionLayer = previousLayer.getPropositionLayer()
        previousLayerMutexProposition = previousPropositionLayer.getMutexProps()

        self.updateActionLayer(previousPropositionLayer)
        self.updateMutexActions(previousLayerMutexProposition)

        self.updatePropositionLayer()
        self.updateMutexProposition()

    def expandWithoutMutex(self, previousLayer):
        """
        Questions 11 and 12
        You don't have to use this function
        """
        previousLayerProposition = previousLayer.getPropositionLayer()
        self.updateActionLayer(previousLayerProposition)
        self.updatePropositionLayer()


def mutexActions(a1, a2, mutexProps):
    """
    This function returns true if a1 and a2 are mutex actions.
    We first check whether a1 and a2 are in PlanGraphLevel.independentActions,
    this is the list of all the independent pair of actions (according to your implementation in question 1).
    If not, we check whether a1 and a2 have competing needs
    """
    if Pair(a1, a2) not in PlanGraphLevel.independentActions:
        return True
    return haveCompetingNeeds(a1, a2, mutexProps)


def haveCompetingNeeds(a1, a2, mutexProps):
    """
    Complete code for deciding whether actions a1 and a2 have competing needs,
    given the mutex proposition from previous level (list of pairs of propositions).
    Hint: for propositions p  and q, the command  "Pair(p, q) in mutexProps"
          returns true if p and q are mutex in the previous level
    """
    def is_mutex(p1, p2):
        return Pair(p1, p2) in mutexProps

    preconditions1 = a1.getPre()
    preconditions2 = a2.getPre()

    # for all the preconditions check if they are mutex
    for cond1 in preconditions1:
        for cond2 in preconditions2:
            if is_mutex(cond1, cond2):
                return True

    # if one of them is mutex so the props is mutex
    return False


def mutexPropositions(prop1, prop2, mutexActions):
    """
    complete code for deciding whether two propositions are mutex,
    given the mutex action from the current level (list of pairs of actions).
    Your updateMutexProposition function should call this function
    You might want to use this function:
    prop1.getProducers() returns the list of all the possible actions in the layer that have prop1 on their add list
    """
    def is_pairwise_mutex(action1, action2):
        return (Pair(action1, action2) in mutexActions)

    producers1 = prop1.getProducers()
    producers2 = prop2.getProducers()

    # for all the producers(action) check if they are pairwise mutex
    for action1 in producers1:
        for action2 in producers2:
            if not is_pairwise_mutex(action1, action2):
                return False
    # if all of them are mutex so the props is mutex
    return True

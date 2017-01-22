from util import Pair

class PropositionLayer(object):
  """
  A class for an PropositionLayer  in a level of the graph.
  The layer contains a list of propositions (Proposition objects) and a list of mutex propositions (Pair objects)
  """


  def __init__(self):
    """
    Constructor
    """
    self.propositions = [] 		    # list of all the propositions in the layer
    self.mutexPropositions = []   # list of pairs of propositions that are mutex in the layer
    
  def addProposition(self, proposition):
  # adds proposition to the propositions list
    self.propositions.append(proposition)
    
  def removePropositions(self, proposition):
  # remove proposition from the propositions list
    self.propositions.remove(proposition)
    
  def getPropositions(self):
  # retunrs the propositions list
    return self.propositions    
  
  def addMutexProp(self, p1, p2):
  # adds the pair(p1,p2) to the mutex propositions list
    self.mutexPropositions.append(Pair(p1,p2))
  
  """
  returns true if proposition p1 and proposition p2 are mutex at this layer
  """
  def isMutex(self, p1, p2):
    return Pair(p1,p2) in self.mutexPropositions  
  
  def getMutexProps(self):
  # returns the mutex propositions list
    return self.mutexPropositions  
  
  def allPrecondsInLayer(self, action):
    """
    returns true if all propositions that are preconditions of the
    action exist in this layer (i.e. the action can be applied)
    """
    for pre in action.getPre():
      if not(pre in self.propositions):
        return False
    for pre1 in action.getPre():
      for pre2 in action.getPre():
        if Pair(pre1,pre2) in self.mutexPropositions:
          return False
    
    return True

  def __eq__(self, other):
    return (isinstance(other, self.__class__)
      and self.__dict__ == other.__dict__)

  def __ne__(self, other):
    return not self.__eq__(other)
      

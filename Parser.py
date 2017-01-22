from action import Action
from proposition import Proposition

class Parser(object):
  """
  A utility class for parsing the domain and problem.
  """


  def __init__(self, domainFile, problemFile):
    """
    Constructor
    """
    self.domainFile = domainFile
    self.problemFile = problemFile


  def parseActionsAndPropositions(self):
    propositions = []
    f = open(self.domainFile, 'r')
    line = f.readline()
    propositionLine = f.readline()
    words = [word.rstrip() for word in propositionLine.split(" ") if len(word.rstrip()) > 0]
    for i in range(0, len(words)):
      propositions.append(Proposition(words[i]))
    actions = []
    f = open(self.domainFile, 'r')
    line = f.readline()
    while(line != ''):
      words =  [word.rstrip() for word in line.split(" ") if len(word.rstrip()) > 0]
      if(words[0] == 'Name:'):
        name = words[1]
        line = f.readline()
        precond = []
        add = []
        delete = []
        words = [word.rstrip() for word in line.split(" ") if len(word.rstrip()) > 0]
        for i in range(1, len(words)):
          precond.append(Proposition(words[i]))
        line = f.readline()
        words = [word.rstrip() for word in line.split(" ") if len(word.rstrip()) > 0]
        for i in range(1, len(words)):
          add.append(Proposition(words[i]))
        line = f.readline()
        words = [word.rstrip() for word in line.split(" ") if len(word.rstrip()) > 0]
        for i in range(1, len(words)):
          delete.append(Proposition(words[i]))
        act = Action(name,precond,add,delete)
        for prop in add:
          self.findPropByName(prop, propositions).addProducer(act)
        actions.append(act)
      line = f.readline()

    for a in actions:
      new_pre = [p for p in propositions if p.name in [q.name for q in a.pre]]
      new_add = [p for p in propositions if p.name in [q.name for q in a.add]]
      new_delete = [p for p in propositions if p.name in [q.name for q in a.delete]]
      a.pre = new_pre
      a.add = new_add
      a.delete = new_delete
      
    return [actions, propositions]

  def findPropByName(self, name, propositions):
    for prop in propositions:
      if prop == name:
        return prop

  def pasreProblem(self):
    init = []
    goal = []
    f = open(self.problemFile, 'r')
    line = f.readline()
    words = [word.rstrip() for word in line.split(" ") if len(word.rstrip()) > 0]
    for i in range(2, len(words)):
      init.append(Proposition(words[i]))
    line = f.readline()
    words = [word.rstrip() for word in line.split(" ") if len(word.rstrip()) > 0]
    for i in range(2, len(words)):
      goal.append(Proposition(words[i]))
    return [init, goal]

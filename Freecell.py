from collections import deque
from os import urandom

allnaipes="ABCD"
maxstorage=4

def genCard (s):
    naipe=s[0].upper()
    rank=0
    if len(s)==2:
        rank=int(s[1])
    elif len(s)==3:
        rank=int(s[1]+s[2])
    return Card (naipe, rank)

class Card:
    def __init__(self, naipe, rank):
        self.naipe=naipe
        self.rank=rank
    def __eq__ (self, other):
        if other:
            return ((self.naipe==other.naipe) and (self.rank==other.rank))
        else:
            return False
    def __hash__ (self):
        return hash((self.naipe, self.rank))
    def __str__(self):
        return str(self.naipe)+str(self.rank)
    def __repr__(self):
        return str(self.naipe)+str(self.rank)
    def mayConnect (self, other):
        if self.rank!=(other.rank+1):
            return False
        if (self.naipe=='A') or (self.naipe=='C'):
            if (other.naipe=='B') or (other.naipe=='D'):
                return True
            else:
                return False
        elif (self.naipe=='B') or (self.naipe=='D'):
            if (other.naipe=='A') or (other.naipe=='C'):
                return True
            else:
                return False

def getDeck():
    ret=[]
    for naipe in allnaipes:
        for rank in range(1,14):
            ret.append (Card (naipe, rank))
    return ret

def getRandomizedDeck():
    orig=getDeck()
    ret=[]
    while len(orig):
        c=orig[urandom(1)[0]%len(orig)]
        orig.remove(c)
        ret.append(c)
    return ret

class Table:
    def __init__(self):
        self.destiny={"A":[],"B":[],"C":[],"D":[]}
        self.storage=set()
        self.columns=[[],[],[],[],[],[],[],[]]
    def __eq__ (self, other):
        return (self.destiny==other.destiny) and (self.storage==other.storage) and (self.columns==other.columns)
    def copy(self):
        ret=Table()
        ret.destiny["A"]=self.destiny["A"][:]
        ret.destiny["B"]=self.destiny["B"][:]
        ret.destiny["C"]=self.destiny["C"][:]
        ret.destiny["D"]=self.destiny["D"][:]
        ret.storage=self.storage.copy()
        i=0
        while i<len(self.columns):
            ret.columns[i]=self.columns[i][:]
            i+=1
        return ret
    def populate (self):
        deck=getRandomizedDeck()
        coli=0
        while len(deck):
            self.columns[coli].append(deck.pop())
            coli+=1
            if coli==len(self.columns):
                coli=0
    def __str__ (self):
        return "Destiny: "+str(self.destiny)+'\nStorage:'+str(self.storage)+'\n0: '+str(self.columns[0])+'\n1: '+str(self.columns[1])+'\n2: '+str(self.columns[2])+'\n3: '+str(self.columns[3])+'\n4: '+str(self.columns[4])+'\n5: '+str(self.columns[5])+'\n6: '+str(self.columns[6])+'\n7: '+str(self.columns[7])
    def getFreeCards (self):
        ret=list(self.storage)
        for col in self.columns:
            if col:
                ret.append(col[-1])
        return ret
    def getPossibleCommands (self, card):
        ret=[]
        '''if card not in self.getFreeCards():
            return ret'''
        if (len(self.storage)<maxstorage) and (card not in self.storage):
            ret.append (str(card)+" S")
        if card.rank==1:
            ret.append (str(card)+" D")
        elif self.destiny[card.naipe] and self.destiny[card.naipe][-1].rank==card.rank-1:
            ret.append (str(card)+" D")
        for icol, col in enumerate (self.columns):
            if col:
                oc=col[-1]
                if oc.mayConnect(card):
                    ret.append (str(card)+' '+str(icol))
            else:
                if (card.rank==13):
                    ret.append (str(card)+' '+str(icol))
        return ret
    def isDestinyComplete (self):
        n=len(self.destiny["A"])+len(self.destiny["B"])+len(self.destiny["C"])+len(self.destiny["D"])
        #print("n=",n)
        return n==52
    def getCard (self, card):
        #print ("getCard ("+str(id(self))+", "+str(card))
        if card in self.storage:
            self.storage.remove(card)
            return card
        for col in self.columns:
            if len(col)==0:
                continue
            if card==col[-1]:
                return col.pop()
        return None
    def putCard (self, card, where):
            #print ("putCard ("+str(id(self))+", "+str(card)+", "+where+")")
            #print(self)
            if where=='S':
                if len(self.storage)<maxstorage:
                    #print ("Storing card.")
                    self.storage.add(card)
                    return True
                #print ("self.storage="+str(self.storage))
                print ("Storage is full.")
                return False
            if where=='D':
                specific=self.destiny[card.naipe]
                if card.rank==1:
                    specific.append(card)
                    return True
                if specific:
                    if specific[-1].rank==card.rank-1:
                        specific.append(card)
                        return True
                print ("The destiny is not ready for this card yet.")
                return False
            try:
                coli=int(where)
            except:
                print ("Unrecognized destination.")
                return False
            #print ("coli="+str(coli))
            try:
                 col=self.columns[coli]
            except:
                print ("Invalid destination number.")
                return False
            #print("col="+str(col))
            if len(col)==0:
                if card.rank==13:
                    col.append(card)
                    return True
                print ("It is illegal to begin with this rank.")
                return False
            if col[-1].mayConnect(card):
                col.append(card)
                return True
            else:
                print ("Trying to connect "+str(card)+" to "+str(col[-1]))
                print ("Such cards do not connect with each other.")
                return False           
    def applyCommand (self, command):
        #print ("applyCommand ("+str(id(self))+', '+command)
        #print(self)
        #ap = self.getAllPossibilities()
        #print(ap)
        com=command.upper()
        '''if com in ap:
            print ("This command is possible.")
        else:
            print ("This command is not in all possibilities.")'''
        l=com.split(' ')
        if len(l)!=2:
            print ("Invalid command: len(l)!=2")
            return False
        card=genCard(l[0])
        #print ("card="+str(card))
        card=self.getCard(card)
        #print ("card="+str(card))
        if card==None:
             print("This card is not movable.")
             return False
        if not self.putCard (card, l[1]):
            print ("You stayed with a card at hand and this is illegal.")
            exit()
        return True
    def getAllPossibilities (self):
            ret=[]
            sfc=self.getFreeCards()
            for ca in sfc:
                l=self.getPossibleCommands(ca)
                for co in l:
                    ret.append(co)
            return ret
    def isPossible (self):
        print ("Verifying Table "+str(id(self)))
        stack=[self]
        queue = deque()
        queue.append(self)
        while queue:
            #print ("len(queue)="+str(len(queue))+"\tlen(stack)="+str(len(stack)))
            ni=queue.popleft()
            if ni.isDestinyComplete():
                return True
            apl=ni.getAllPossibilities()
            for com in apl:
                nt=ni.copy()
                if not nt.applyCommand(com):
                    print ("Invalid command.")
                    exit()
                if nt in stack:
                    #print ("nt in stack")
                    continue
                else:
                    #print ("Modified copy is not in stack.")
                    stack.append(nt)
                    queue.append(nt)
        return False

def main():
    print ("Hello")
    t=Table()
    t.populate()
    #print(t)
    while not t.isPossible():
        t=Table()
        t.populate()
        #print(t)
    while not t.isDestinyComplete():
        print(t)
        fc=t.getFreeCards()
        print ("The free cards are: "+str(fc))
        print ("The possible commands are: ")
        lc=t.getAllPossibilities()
        for c in lc:
            print (c)
        command=input("Enter your command: ")
        t.applyCommand (command)
    print ("You won.")

main()

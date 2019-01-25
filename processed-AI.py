import random
import os

class Decision(object):
    giveup = 0
    allin = 0
    check = 0
    callbet = 0
    raisebet = 0
    amount = 0

    def clear(self):
        self.giveup = self.allin = self.check = self.callbet = self.raisebet = self.amount = 0

'''
    self.bigBlind = bigBlind
    self.currpos = 0             
    self.playernum = totalPlayer 
    self.moneypot = 0            
    self.minbet = bigBlind       
    self.sharedcards = []        
    self.turnNum = 0            
    self.last_raised = bigBlind         
    self.money = initMoney      
    self.bet = 0                 
    self.cards = []             
    self.totalbet = 0           
'''

forward = open('forward.txt', 'r')
back = open('back.txt', 'wt')
s = forward.readlines()
ll = len(s)
for i in range(ll):
    s[i] = s[i].strip()
    s[i] = eval(s[i])

bigBlind = s[0]
currpos = s[1]
playernum = s[2]
moneypot = s[3]
minbet = s[4]
sharedcards = s[5]
turnNum = s[6]
last_raised = s[7]
money = s[8]
bet = s[9]
cards = s[10]
totalbet = s[11]

delta = minbet - bet
decision = Decision()

if delta <= 0:
    if money < bigBlind:
        flag = random.randint(1, 5)
        if flag == 1:
            decision.giveup = 1
        else:
            decision.allin = 1
    elif money == bigBlind:
        decision.allin = 1
    else:
        decision.raisebet = 1
        decision.amount = bigBlind
elif money <= delta:
    flag = random.randint(1, 5)
    if flag == 1:
        decision.giveup = 1
    else:
        decision.allin = 1

else:
    # t = random.randint(1, 5)
    if money > delta + last_raised:
        flag = random.randint(1, 2)
        if flag == 2:
            decision.callbet = 1
        else:
            decision.raisebet = 1
            decision.amount = random.randint(minbet + last_raised, bet + money - 1)

    else:
        decision.callbet = 1

back.write(str(decision.giveup))
back.write('\n')
back.write(str(decision.allin))
back.write('\n')
back.write(str(decision.check))
back.write('\n')
back.write(str(decision.callbet))
back.write('\n')
back.write(str(decision.raisebet))
back.write('\n')
back.write(str(decision.amount))
forward.close()
back.close()

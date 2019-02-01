import random
import os
from AI.naive import naive_ai
from time import sleep
import communicate.dealer_pb2 as dealer_pb2
import communicate.dealer_pb2_grpc as rpc

initMoney = 1000
bigBlind = 20
totalPlayer = 3 
button = 0


# alter the id into color
def id2color(card):
    return card % 4

# alter the id into number
def id2num(card):
    return card // 4



class Hand(object):
    def __init__(self, cards):
        cards = cards[:]
        self.level = 0
        self.cnt_num = [0] * 13
        self.cnt_color = [0] * 4
        self.cnt_num_eachcolor = [[0 for col in range(13)] for row in range(4)]
        self.maxnum = -1
        self.single = []
        self.pair = []
        self.tripple = []
        for x in cards:
            self.cnt_num[id2num(x)] += 1
            self.cnt_color[id2color(x)] += 1
            self.cnt_num_eachcolor[id2color(x)][id2num(x)] += 1
        for i in range(12, -1, -1):
            if self.cnt_num[i] == 1:
                self.single.append(i)
            elif self.cnt_num[i] == 2:
                self.pair.append(i)
            elif self.cnt_num[i] == 3:
                self.tripple.append(i)
        self.single.sort(reverse=True)
        self.pair.sort(reverse=True)
        self.tripple.sort(reverse=True)

        for i in range(4):
            if self.cnt_num_eachcolor[i][8:13].count(1) == 5:
                self.level = 10
                return


        for i in range(4):
            for j in range(7, -1, -1):
                if self.cnt_num_eachcolor[i][j:j+5].count(1) == 5:
                    self.level = 9
                    self.maxnum = j + 4
                    return


        for i in range(12, -1, -1):
            if self.cnt_num[i] == 4:
                self.maxnum = i
                self.level = 8
                return


        tripple = self.cnt_num.count(3)
        if tripple > 1:
            self.level = 7
            return
        elif tripple > 0:
            if self.cnt_num.count(2) > 0:
                self.level = 7
                return


        for i in range(4):
            if self.cnt_color[i] >=5:
                if(max(self.cnt_num_eachcolor[i]) > self.maxnum):
                    self.maxnum = max(self.cnt_num_eachcolor[i])
                self.level = 6
        if self.level == 6:
            return

        for i in range(8, -1, -1):
            flag = 1
            for j in range(i, i + 5):
                if self.cnt_num[j] == 0:
                    flag = 0
                    break
            if flag == 1:
                self.maxnum = i + 4
                self.level = 5
                return


        for i in range(12, -1, -1):
            if self.cnt_num[i] == 3:
                self.maxnum = i
                self.level = 4
                return


        if self.cnt_num.count(2) > 1:
            self.level = 3
            return


        for i in range(12, -1, -1):
            if self.cnt_num[i] == 2:
                self.maxnum = i
                self.level = 2
                return


        if self.cnt_num.count(1) == 7:
            self.level = 1
            return

        self.level = -1

    def __str__(self):
        return 'level = %s' % self.level


def cmp(x,y):  # x < y return 1
    if x > y: return -1
    elif x == y: return 0
    else: return 1


def judge_two(cards0, cards1):
    hand0 = Hand(cards0)
    hand1 = Hand(cards1)
    if hand0.level > hand1.level:
        return 0
    elif hand0.level < hand1.level:
        return 1
    else:
        if hand0.level in [5, 6, 9]:
            return cmp(hand0.maxnum, hand1.maxnum)
        elif hand0.level in [1, 2, 4]:
            t = cmp(hand0.maxnum, hand1.maxnum)
            if t == 1: return 1
            elif t == -1: return -1
            else:
                if hand0.single < hand1.single:
                    return 1
                elif hand0.single == hand1.single:
                    return 0
                else:
                    return -1
        elif hand0.level == 8:
            t = cmp(hand0.maxnum, hand1.maxnum)
            if t == 1:
                return 1
            elif t == -1:
                return -1
            else:
                pair_single0 = hand0.pair + hand0.pair + hand0.single
                pair_single0.sort()
                pair_single1 = hand1.pair + hand1.pair + hand1.single
                pair_single1.sort()
                if pair_single0 < pair_single1:
                    return 1
                elif pair_single0 == pair_single1:
                    return 0
                else:
                    return -1
        elif hand0.level == 3:
            if cmp(hand0.pair[0], hand1.pair[0]) != 0:
                return cmp(hand0.pair[0], hand1.pair[0])
            elif cmp(hand0.pair[1], hand1.pair[1]) != 0:
                return cmp(hand0.pair[1], hand1.pair[1])
            else:
                hand0.pair = hand0.pair[2:]
                hand1.pair = hand1.pair[2:]
                tmp0 = hand0.pair + hand0.pair + hand0.single
                tmp1 = hand1.pair + hand1.pair + hand1.single
                if tmp0 < tmp1:
                    return 1
                elif tmp0 == tmp1:
                    return 0
                else:
                    return -1

        elif hand0.level == 7:
            if cmp(hand0.tripple[0], hand1.tripple[0]) != 0:
                return cmp(hand0.tripple[0], hand1.tripple[0])
            else:
                tmp0 = hand0.pair
                tmp1 = hand1.pair
                if len(hand0.tripple) > 1:
                    tmp0.append(hand0.tripple[1])
                if len(hand1.tripple) > 1:
                    tmp1.append(hand1.tripple[1])
                if tmp0 < tmp1:
                    return 1
                elif tmp0 == tmp1:
                    return 0
                else:
                    return -1
        else:
            pass
            # assert 0





class Player(object):

    def __init__(self, initMoney, state):
        self.active = True
        self.money = initMoney
        self.bet = 0
        self.cards = []
        self.allin = 0
        self.totalbet = 0
        self.state = state

    def raisebet(self, amount):
        self.money -= amount
        self.bet += amount
        assert self.money > 0


    def allinbet(self):
        self.bet += self.money
        self.allin = 1
        self.money = 0

    def getcards(self):
        return self.cards + self.state.sharedcards

    def __str__(self):
        return 'player: active = %s, money = %s, bet = %s, allin = %s' % (self.active, self.money, self.bet, self.allin)




class State(object):
    global initMoney
    global bigBlind
    global totalPlayer
    global button
    def __init__(self, totalPlayer, initMoney, bigBlind):
        ''' class to hold the game '''
        self.bigBlind = bigBlind
        self.currpos = 0
        self.playernum = totalPlayer
        self.moneypot = 0
        self.minbet = bigBlind
        self.sharedcards = []
        self.turnNum = 0
        self.last_raised = bigBlind
        self.player = []
        for i in range(totalPlayer):
            self.player.append(Player(initMoney, self))


    def __str__(self):
        return 'state: currpos = %s, playernum = %s, moneypot = %s, \n minbet = %s, last_raised = %s' \
               % (self.currpos, self.playernum, self.moneypot, self.minbet, self.last_raised)

    def restore(self, turn, button, bigBlind):      # restore the state before each round
        self.turnNum = turn
        self.currpos = button
        self.minbet = 0
        self.last_raised = bigBlind

    def update(self, totalPlayer):                       # update the state after each round
        for i in range(totalPlayer):
            if self.player[i].active == False:
                continue
            self.player[i].totalbet += self.player[i].bet
            self.player[i].bet = 0

    def round_over(self):
        if self.playernum == 1:
            for i in range(self.playernum):
                if self.player[i].active == True:
                    print('Only Winner: player %s' % i)
            return 1
        for i in range(self.playernum):
            if self.player[i].active is True and self.player[i].allin == 0:
                break
        else:
            return 1
        for i in range(self.playernum):
            if self.player[i].active is True and (self.player[i].bet != self.minbet and self.player[i].allin == 0):
                return 0
        if self.turnNum != 0 and self.minbet == 0:
            return 0
        return 1

    def nextpos(self, pos):
        self.currpos = (pos + 1) % totalPlayer
        return self.currpos

    def play_round(self, round, request, response):
        checkflag = 0
        while True:
            if self.round_over() == 1:
                break
            self.currpos = self.nextpos(self.currpos)
            if self.player[self.currpos].active == False:
                continue
            if self.player[self.currpos].allin == 1:
                continue

            decision = Decision()
            # TODO   send state and player info to player[state.currpos]
            response[self.currpos].append(dealer_pb2.DealerRequest(pos=self.currpos, type=2))
            # TODO   run player AI
            while len(request[self.currpos]) == 0:
                # print('waiting for position ', self.currpos)
                sleep(1)
            tmp = request[self.currpos].pop()
            decision.update([tmp.giveup, tmp.allin, tmp.check, tmp.callbet, tmp.raisebet, tmp.amount])
            # TODO   receive decision from player, decision = (give-up, allin, check, callbet, raisebet, amount)


            if decision.giveup == 1:
                self.player[self.currpos].active = False
                self.playernum -= 1
                print("## player %s giveup" % self.currpos)
            elif round != 0 and decision.check == 1:
                if checkflag == 1:
                    self.illegalmove()
                    continue
                print("## player %s check" % self.currpos)
                continue
            elif decision.allin == 1:
                self.moneypot += self.player[self.currpos].money
                self.player[self.currpos].allinbet()
                if self.player[self.currpos].bet > self.minbet:
                    self.last_raised = self.player[self.currpos].bet - self.minbet
                    self.minbet = self.player[self.currpos].bet
                checkflag = 1
                print("## player %s allin: %s" % (self.currpos, self.player[self.currpos].money))

            elif decision.callbet == 1:
                delta = self.minbet - self.player[self.currpos].bet
                assert delta >= 0
                if delta >= self.player[self.currpos].money or delta < 0:
                    self.illegalmove()
                    continue
                self.player[self.currpos].raisebet(delta)
                self.moneypot += delta
                checkflag = 1
                print("## player %s callbet: %s" % (self.currpos, delta))

            elif decision.raisebet == 1:
                assert decision.amount >= self.minbet
                if decision.amount - self.minbet < self.last_raised:
                    self.illegalmove()
                    continue
                self.last_raised = decision.amount - self.minbet
                self.minbet = decision.amount
                delta = decision.amount - self.player[self.currpos].bet
                if delta >= self.player[self.currpos].money or delta < 0:
                    self.illegalmove()
                    continue
                self.player[self.currpos].raisebet(delta)
                self.moneypot += delta
                checkflag = 1
                print("## player %s raisebet: %s" % (self.currpos, delta))

            else:
                self.illegalmove()
                continue

            for i in range(totalPlayer):
                response[i].append(dealer_pb2.DealerRequest(giveup=decision.giveup,
                allin=decision.allin, check=decision.check, callbet=decision.callbet,
                raisebet=decision.raisebet, amount=decision.amount, pos=self.currpos, type=1))

            print(self)
            print(self.player[self.currpos])

    def findwinner(self):
        winpos = -1
        for pos in range(self.playernum):
            if self.player[pos].active == 0:
                continue
            if winpos == -1:
                winpos = pos
            else:
                t = judge_two(self.player[winpos].getcards(), self.player[pos].getcards())
                if t == 1:
                    winpos = pos
        return winpos

    def illegalmove(self):  # player进行非法行动的处理
        # TODO  send infomation to the player: illegal decision!
        self.player[self.currpos].active = False
        self.playernum -= 1
        self.currpos = self.nextpos(self.currpos)
        print('player %s illegal move' % self.currpos)




class Decision(object):
    giveup = 0
    allin = 0
    check = 0
    callbet = 0
    raisebet = 0
    amount = 0

    def clear(self):
        self.giveup = self.allin = self.check = self.callbet = self.raisebet = self.amount = 0

    def update(self, a):
        self.giveup = a[0]
        self.allin = a[1]
        self.check = a[2]
        self.callbet = a[3]
        self.raisebet = a[4]
        self.amount = a[5]

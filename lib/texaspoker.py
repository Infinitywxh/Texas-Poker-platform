import random
import os
from AI.naive import naive_ai
# 0 黑桃 1 红桃 2 方片 3 草花
# 牌的id: 0-51


# 将牌的id转为颜色
def id2color(card):
    return card % 4

# 将牌的id转为数字
def id2num(card):
    return card // 4

'''
牌面level编号
    皇家同花顺：10
    同花顺    ：9
    四条      ：8
    葫芦      ：7
    同花      ：6
    顺子      ：5
    三条      ：4
    两对      ：3
    一对      ：2
    高牌      ：1
'''

class Hand(object):
    def __init__(self, cards):
        cards = cards[:]
        self.level = 0              # 盘面的等级
        self.cnt_num = [0] * 13     # 每种数字的个数
        self.cnt_color = [0] * 4    # 每种颜色的个数
        self.cnt_num_eachcolor = [[0 for col in range(13)] for row in range(4)]  # 记录每种花色的牌
        self.maxnum = -1            # 最大等级五牌最大数字
        self.single = []            # 单牌
        self.pair = []              # 对子
        self.tripple = []           # 三条
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
        # 判断皇家同花顺
        for i in range(4):
            if self.cnt_num_eachcolor[i][8:13].count(1) == 5:
                self.level = 10
                return

        # 判断同花顺
        for i in range(4):
            for j in range(7, -1, -1):       # 从7开始，因为8，9，10，11，12是同花顺
                if self.cnt_num_eachcolor[i][j:j+5].count(1) == 5:
                    self.level = 9
                    self.maxnum = j + 4
                    return

        # 判断四条
        for i in range(12, -1, -1):
            if self.cnt_num[i] == 4:
                self.maxnum = i
                self.level = 8
                return

        # 判断葫芦
        tripple = self.cnt_num.count(3)
        if tripple > 1:
            self.level = 7
            return
        elif tripple > 0:
            if self.cnt_num.count(2) > 0:
                self.level = 7
                return

        # 判断同花
        for i in range(4):
            if self.cnt_color[i] >=5:
                if(max(self.cnt_num_eachcolor[i]) > self.maxnum):
                    self.maxnum = max(self.cnt_num_eachcolor[i])
                self.level = 6
        if self.level == 6:
            return
        # 判断顺子
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

        # 判断三条
        for i in range(12, -1, -1):
            if self.cnt_num[i] == 3:
                self.maxnum = i
                self.level = 4
                return

        # 判断两对
        if self.cnt_num.count(2) > 1:
            self.level = 3
            return

        # 判断一对
        for i in range(12, -1, -1):
            if self.cnt_num[i] == 2:
                self.maxnum = i
                self.level = 2
                return

        # 高牌
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


def judge_two(cards0, cards1):      # 比较两手牌的大小，cards0和cards1都是7元组，若cards0大则返回-1，一样大返回0，否则返回1
    hand0 = Hand(cards0)
    hand1 = Hand(cards1)
    if hand0.level > hand1.level:
        return 0
    elif hand0.level < hand1.level:
        return 1
    else:       # 同级别牌面比较  皇家同花顺一定不会同时出现
        if hand0.level in [5, 6, 9]: # 只用比最大
            return cmp(hand0.maxnum, hand1.maxnum)
        elif hand0.level in [1, 2, 4]: # 先比最大，再比单牌
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
        elif hand0.level == 8:  # 先比最大，再比单牌/对子
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
        self.active = True           # 玩家是否已弃牌
        self.money = initMoney       # 玩家持有的钱数
        self.bet = 0                 # 玩家在本轮下注
        self.cards = []              # 玩家手牌
        self.allin = 0               # 玩家是否已allin
        self.totalbet = 0            # 玩家在本局的总下注
        self.state = state

    def raisebet(self, amount):
        self.money -= amount
        self.bet += amount
        assert self.money > 0


    def allinbet(self):        # 玩家 allin
        self.bet += self.money
        self.allin = 1
        self.money = 0

    def getcards(self):
        return self.cards + self.state.sharedcards

    def __str__(self):
        return 'player: active = %s, money = %s, bet = %s, allin = %s' % (self.active, self.money, self.bet, self.allin)




class State(object):
    def __init__(self, totalPlayer, initMoney, bigBlind):
        ''' class to hold the game '''
        self.bigBlind = bigBlind
        self.currpos = 0             # 当前轮到的玩家
        self.playernum = totalPlayer # 未弃牌的玩家总数
        self.moneypot = 0            # 池中总钱数
        self.minbet = bigBlind       # 当前跟注的最小值
        self.sharedcards = []        # 已亮出的公共牌
        self.turnNum = 0             # 轮次  0：pre-lop     1: flop     2: turn     3: river
        self.last_raised = bigBlind         # 上一次的加注额
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
        if self.playernum == 1:        #TODO 游戏结束  只剩1人?
            for i in range(self.playernum):
                if self.player[i].active == True:
                    print('Only Winner: player %s' % i)
            return 1
        for i in range(self.playernum):
            if self.player[i].active is True and self.player[i].allin == 0:
                break
        else:
            return 1  # 所有人allin
        for i in range(self.playernum):
            if self.player[i].active is True and (self.player[i].bet != self.minbet and self.player[i].allin == 0):
                return 0  # 有某个未退出的玩家下注未达最小值且未allin，回合尚未结束
        if self.turnNum != 0 and self.minbet == 0:
            return 0      # 仍在看牌，尚未有人下注
        return 1          # 回合结束

    def nextpos(self, pos):
        self.currpos = (pos + 1) % self.playernum
        return self.currpos

    def play_round(self, round):
        checkflag = 0  # 记录是否可以看牌（即尚未有人下注）
        while True:
            if self.round_over() == 1:  # TODO 除了一人以外其他人都弃牌，但此人无足够的钱下注来继续游戏 如何处理
                break
            self.currpos = self.nextpos(self.currpos)
            if self.player[self.currpos].active == False:
                continue
            if self.player[self.currpos].allin == 1:
                continue

            # TODO   send state and player info to player[state.currpos]
            # TODO   run player AI
            decision = naive_ai(self.currpos, self)
            # TODO   receive decision from player， decision = (give-up, allin, check, callbet, raisebet, amount)

            # pre-flop轮，不可能check，此位会被忽略
            if decision.giveup == 1:  # 玩家弃牌
                self.player[self.currpos].active = False
                self.playernum -= 1
                print("## player %s giveup" % self.currpos)
            elif round != 0 and decision.check == 1:  # 玩家过牌
                if checkflag == 1:
                    illegalmove(self.currpos)
                    continue
                print("## player %s check" % self.currpos)
                continue
            elif decision.allin == 1:  # 玩家allin
                self.moneypot += self.player[self.currpos].money
                self.player[self.currpos].allinbet()
                if self.player[self.currpos].bet > self.minbet:  # allin 加注
                    self.last_raised = self.player[self.currpos].bet - self.minbet
                    self.minbet = self.player[self.currpos].bet
                checkflag = 1
                print("## player %s allin: %s" % (self.currpos, self.player[self.currpos].money))

            elif decision.callbet == 1:  # 玩家跟注
                delta = self.minbet - self.player[self.currpos].bet
                assert delta > 0
                if delta >= self.player[self.currpos].money or delta < 0:  # 跟注时所有钱押入，这种情况属于allin
                    illegalmove(self.currpos)
                    continue
                self.player[self.currpos].raisebet(delta)
                self.moneypot += delta
                checkflag = 1
                print("## player %s callbet: %s" % (self.currpos, delta))

            elif decision.raisebet == 1:  # 玩家加注
                assert decision.amount >= self.minbet
                if decision.amount - self.minbet < self.last_raised:  # 加注量至少和上一次一致
                    illegalmove(self.currpos)
                    continue
                self.last_raised = decision.amount - self.minbet
                self.minbet = decision.amount
                delta = decision.amount - self.player[self.currpos].bet
                if delta >= self.player[self.currpos].money or delta < 0:  # 跟注时所有钱押入，这种情况属于allin
                    illegalmove(self.currpos)
                    continue
                self.player[self.currpos].raisebet(delta)
                self.moneypot += delta
                checkflag = 1
                print("## player %s raisebet: %s" % (self.currpos, delta))

            else:  # 不合法行动
                illegalmove(self.currpos)
                continue

            print(self)
            print(self.player[self.currpos])

    def findwinner(self):       # 从active的玩家中找到一个赢家
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



def illegalmove(playerid):              # player进行非法行动的处理
    # TODO  send infomation to the player: illegal decision!
    player[playerid].active = False
    state.playernum -= 1
    state.currpos = nextpos(state.currpos)
    print('player %s illegal move' % playerid)

class Decision(object):
    giveup = 0    # 弃牌
    allin = 0     # allin
    check = 0     # 看牌
    callbet = 0   # 跟注
    raisebet = 0  # 加注
    amount = 0    # 加注到amount

    def clear(self):
        self.giveup = self.allin = self.check = self.callbet = self.raisebet = self.amount = 0



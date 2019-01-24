import random
import os
from lib.texaspoker import State

if __name__ == '__main__':
    # main routine
    # 0 黑桃 1 红桃 2 方片 3 草花
    # 牌的id: 0-51

    initMoney = 1000    # 初始钱数
    bigBlind = 20       # 大盲注
    totalPlayer = 5     # 玩家人数
    button = 0          # 庄家位置


    state = State(totalPlayer, initMoney, bigBlind)

    '''
    向玩家AI发送的信息：state, player
    从玩家AI接受的信息：decision = (give-up, allin, check, callbet, raisebet, amount)
    '''

    # 洗牌，准备牌堆
    cardHeap = list(range(0,52))
    random.shuffle(cardHeap)

    # pre-flop begin
    print('$$$ pre-flop begin')
    # 小盲注、大盲注
    state.nextpos(button)
    state.player[state.currpos].raisebet(bigBlind // 2)
    state.moneypot += bigBlind // 2

    print("## player %s smallBlind: %s" % (state.currpos, bigBlind // 2))
    print(state)
    print(state.player[state.currpos])

    state.nextpos(state.currpos)
    state.player[state.currpos].raisebet(bigBlind)
    state.moneypot += bigBlind
    print(state)
    print(state.player[state.currpos])
    print("## player %s bigBlind: %s" % (state.currpos, bigBlind))

    state.play_round(0)

    # pre-flop ended
    for i in range(totalPlayer):
        if state.player[i].active == False:
            continue
        state.player[i].totalbet += state.player[i].bet
        state.player[i].bet = 0
    state.sharedcards = cardHeap[0:3]

    # flop begin
    print('$$$ flop begin')
    #TODO 如果所有人一直看牌（check）会怎么样 ?

    state.turnNum = 1
    state.currpos = button
    state.minbet = 0
    state.last_raised = bigBlind

    state.play_round(1)


    # flop ended
    for i in range(totalPlayer):
        if state.player[i].active == False:
            continue
        state.player[i].totalbet += state.player[i].bet
        state.player[i].bet = 0
    state.sharedcards = cardHeap[0:4]

    # turn begin
    print('$$$ turn begin')
    #TODO 如果所有人一直看牌（check）会怎么样 ?

    state.turnNum = 2
    state.currpos = button
    state.minbet = 0
    state.last_raised = bigBlind

    state.play_round(2)

    # turn ended
    for i in range(totalPlayer):
        if state.player[i].active == False:
            continue
        state.player[i].totalbet += state.player[i].bet
        state.player[i].bet = 0
    state.sharedcards = cardHeap[0:5]

    # river begin
    print('$$$ river begin')
    #TODO 如果所有人一直看牌（check）会怎么样 ?

    state.turnNum = 3
    state.currpos = button
    state.minbet = 0
    state.last_raised = bigBlind

    state.play_round(3)

    # river ended
    for i in range(totalPlayer):
        if state.player[i].active == False:
            continue
        state.player[i].totalbet += state.player[i].bet
        state.player[i].bet = 0


    print("game ended")

    # game over, 开始分配彩池

    totalmoney = state.moneypot


    while state.playernum > 0:
        pos = state.findwinner()
        t = state.player[pos].totalbet
        sum = 0
        for i in range(totalPlayer):
            sum += min(t, state.player[i].totalbet)
            state.player[i].totalbet -= min(t, state.player[i].totalbet)
            if state.player[i].totalbet == 0:
                state.player[pos].active = False
                state.playernum -= 1
        state.player[pos].money += sum

    print('final state:')
    for i in range(totalPlayer):
        print("player %s have money %s" % (i, state.player[i].money))

    # main routine ended


    '''
    # 测试：计算牌面 level

    A = [0] * 7
    for i in range(7):
        A[i] = random.randint(0, 51)
    print(A)
    B = [[0 for col in range(2)] for row in range(7)]
    for i in range(7):
        B[i][0] = id2color(A[i])
        B[i][1] = id2num(A[i])
    B.sort(key=lambda f: f[1])
    for i in B:
        print("color = %s, num = %s" % (i[0], i[1]))
    a = Hand(A)
    print(a.level)
    '''

    '''
    while True:
        A = [0] * 7
        for i in range(7):
            A[i] = random.randint(0, 51)
        print(A)
        B = [[0 for col in range(2)] for row in range(7)]
        for i in range(7):
            B[i][0] = id2color(A[i])
            B[i][1] = id2num(A[i])

        B.sort(key=lambda f: f[1])
        # for i in B:
        #    print("color = %s, num = %s" % (i[0], i[1]))
        a = Hand(A)
        print(a.level)
        if a.level == 10:
            # print(A)
            for i in B:
                print("color = %s, num = %s" % (i[0], i[1]))
            # print(a.level)
            break
    '''

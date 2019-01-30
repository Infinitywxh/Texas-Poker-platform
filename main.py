import random
import os
from lib.texaspoker import State
from lib.texaspoker import initMoney
from lib.texaspoker import bigBlind
from lib.texaspoker import totalPlayer
from lib.texaspoker import button


def mainroutine():
    # main routine
    # id of the card: 0-51
    global initMoney
    global bigBlind
    global totalPlayer
    global button


    state = State(totalPlayer, initMoney, bigBlind)

    # shuffle the cards
    cardHeap = list(range(0, 52))
    random.shuffle(cardHeap)

    # pre-flop begin
    print('$$$ pre-flop begin')

    # small and big blind
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
    state.update(totalPlayer)
    state.sharedcards = cardHeap[0:3]

    # flop begin
    print('$$$ flop begin')

    state.restore(1, button, bigBlind)

    state.play_round(1)


    # flop ended
    state.update(totalPlayer)
    state.sharedcards = cardHeap[0:4]

    # turn begin
    print('$$$ turn begin')

    state.restore(2, button, bigBlind)

    state.play_round(2)

    # turn ended
    state.update(totalPlayer)
    state.sharedcards = cardHeap[0:5]

    # river begin
    print('$$$ river begin')

    state.restore(3, button, bigBlind)

    state.play_round(3)

    # river ended
    state.update(totalPlayer)


    print("game ended")

    # game over, allocate the money pot

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


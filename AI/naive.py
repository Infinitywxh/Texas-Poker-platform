import random
import os


class Decision(object):
    giveup = 0    # 弃牌
    allin = 0     # allin
    check = 0     # 看牌
    callbet = 0   # 跟注
    raisebet = 0  # 加注
    amount = 0    # 加注到amount

    def clear(self):
        self.giveup = self.allin = self.check = self.callbet = self.raisebet = self.amount = 0

    def __str__(self):
        return 'giveup=%s, allin=%s, check=%s, callbet=%s, raisebet=%s, amount=%s' % (self.giveup,self.allin,self.check,
                                                                                                    self.callbet, self.raisebet, self.amount)


def naive_ai(id, state):
    delta = state.minbet - state.player[id].bet
    decision = Decision()
    decision.clear()
    if delta <= 0:  # 还在看牌期，之前无人下注
        if state.player[id].money < state.bigBlind:
            flag = random.randint(1, 5)
            if flag == 1:
                decision.giveup = 1
            else:
                decision.allin = 1
        elif state.player[id].money == state.bigBlind:
            decision.allin = 1
        else:
            decision.raisebet = 1
            decision.amount = state.bigBlind
    elif state.player[id].money <= delta:      # 手中的钱不够补全或正好补全
        flag = random.randint(1, 5)
        if flag == 1:
            decision.giveup = 1
        else:
            decision.allin = 1

    else:
        # t = random.randint(1, 5)
        if state.player[id].money > delta + state.last_raised:
            flag = random.randint(1, 2)
            if flag == 2:
                decision.callbet = 1
            else:
                decision.raisebet = 1
                decision.amount = random.randint(state.minbet + state.last_raised, state.player[id].bet+ state.player[id].money - 1)

        else:
            decision.callbet = 1

    return decision

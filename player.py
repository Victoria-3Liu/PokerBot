'''
Simple example pokerbot, written in Python.
'''
from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot

import random

def cardConverter(e):
    key_dict = {"2" : 2, "3" : 3, "4" : 4, "5" : 5, "6" : 6, "7" : 7, "8" : 8, "9" : 9, "T" : 10, "J" : 11, "Q" : 12, "K": 13, "A": 14}
    suit_dict = {"s" : 0.1, "c" : 0.2, "h" : 0.3, "d" : 0.4} 
    return key_dict[e[0]] + suit_dict[e[1]]

def card_value_converter(e):
    key_dict = {"2" : 2, "3" : 3, "4" : 4, "5" : 5, "6" : 6, "7" : 7, "8" : 8, "9" : 9, "T" : 10, "J" : 11, "Q" : 12, "K": 13, "A": 14}
    return key_dict[e[0]]

def hand_classifier(cards):
    suit_dict = {"s" : 0, "c" : 0, "h" : 0, "d" : 0}
    straight = False
    flush = False
    four_kind = False
    three_kind = False
    pair_count = 0
    card_values = [card_value_converter(card) for card in cards]
    card_values = sorted(card_values)
    run = 1
    for i in range(len(card_values) - 1):
        if (card_values[i] == card_values[i+1] - 1):
            run += 1
        else:
            run = 1
        if (run == 5):
            straight = True
            break
    for card in cards:
        suit_dict[card[1]] += 1
    for suit in suit_dict:
        if (suit_dict[suit] >= 5):
            flush = True
    card_dict = {}
    for card in cards:
        if card[0] in card_dict:
            card_dict[card[0]] += 1
        else:
            card_dict[card[0]] = 1
    for card in card_dict:
        if card_dict[card] == 2:
            pair_count += 1
        if card_dict[card] == 3:
            three_kind = True
        if card_dict[card] == 4:
            four_kind = True
    if (straight and flush):
        return "sf"
    if (four_kind):
        return "4k"
    if (three_kind and pair_count > 1):
        return "fh"
    if (flush):
        return "fl"
    if (straight):
        return "st"
    if (three_kind):
        return "3k"
    if (pair_count >= 2):
        return "2p"
    if (pair_count == 1):
        return "pa"
    else:
        return "hc"

class Player(Bot):
    '''
    A pokerbot.
    '''

    def __init__(self):
        '''
        Called when a new game starts. Called exactly once.

        Arguments:
        Nothing.

        Returns:
        Nothing.
        '''
        pass

    def handle_new_round(self, game_state, round_state, active):
        '''
        Called when a new round starts. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        #my_bankroll = game_state.bankroll  # the total number of chips you've gained or lost from the beginning of the game to the start of this round
        #game_clock = game_state.game_clock  # the total number of seconds your bot has left to play this game
        #round_num = game_state.round_num  # the round number from 1 to NUM_ROUNDS
        #my_cards = round_state.hands[active]  # your cards
        #big_blind = bool(active)  # True if you are the big blind
        pass

    def handle_round_over(self, game_state, terminal_state, active):
        '''
        Called when a round ends. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        terminal_state: the TerminalState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        #my_delta = terminal_state.deltas[active]  # your bankroll change from this round
        previous_state = terminal_state.previous_state  # RoundState before payoffs
        #street = previous_state.street  # 0, 3, 4, or 5 representing when this round ended
        #my_cards = previous_state.hands[active]  # your cards
        #opp_cards = previous_state.hands[1-active]  # opponent's cards or [] if not revealed
        pass

    def get_action(self, game_state, round_state, active):
        '''
        Where the magic happens - your code should implement this function.
        Called any time the engine needs an action from your bot.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Your action.
        '''
        legal_actions = round_state.legal_actions()  # the actions you are allowed to take
        street = round_state.street  # 0, 3, 4, or 5 representing pre-flop, flop, turn, or river respectively
        my_cards = round_state.hands[active]  # your cards
        board_cards = round_state.deck[:street]  # the board cards
        my_pip = round_state.pips[active]  # the number of chips you have contributed to the pot this round of betting
        opp_pip = round_state.pips[1-active]  # the number of chips your opponent has contributed to the pot this round of betting
        my_stack = round_state.stacks[active]  # the number of chips you have remaining
        opp_stack = round_state.stacks[1-active]  # the number of chips your opponent has remaining
        continue_cost = opp_pip - my_pip  # the number of chips needed to stay in the pot
        my_contribution = STARTING_STACK - my_stack  # the number of chips you have contributed to the pot
        opp_contribution = STARTING_STACK - opp_stack  # the number of chips your opponent has contributed to the pot
        if RaiseAction in legal_actions:
            min_raise, max_raise = round_state.raise_bounds()  # the smallest and largest numbers of chips for a legal bet/raise
            min_cost = min_raise - my_pip  # the cost of a minimum bet/raise
            max_cost = max_raise - my_pip  # the cost of a maximum bet/raise
            hand_dict = {"sf":max_raise-1,"4k":max_raise/2, "fh":max_raise/4, "fl": max_raise/5, "st" : max_raise/7, "3k" : max_raise/10, "2p" : min_raise+10, "pa":min_raise,"hc":0}
        cards = my_cards+board_cards
        cards.sort(key = cardConverter)
        rai = 0
        hand_value = 10
        if(street == 0):
            card_dict = {}
            suit_dict = {}
            for card in my_cards:  
                card_dict[card] = 0
                suit_dict[card[1]] = 0
            hand_value += 5 * (len(my_cards) - len(card_dict))
            hand_value += 5 * (len(my_cards) - len(suit_dict)) ** 3
            if (my_pip == 5):
                print()
            for card in my_cards:
                if (not card[0].isdigit()):
                    hand_value += 5
        x = hand_classifier(cards)
        #add hand_dict to each street
        rai = (int)(max((int)(hand_value/2.0),hand_dict[x]))
        if RaiseAction in legal_actions and min_cost<rai<max_cost:
            return RaiseAction(rai)
        if CheckAction in legal_actions:  # check-call
            return CheckAction()
        if street == 2 and continue_cost > 15 and hand_value <= 20 and rai * 2 < continue_cost:
            return FoldAction()
        if street == 4 and continue_cost > rai and continue_cost * 2 > my_contribution:
            return FoldAction()
        return CallAction()


if __name__ == '__main__':
    run_bot(Player(), parse_args())
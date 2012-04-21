""" Python poker equity calculator.
"""

import itertools
import pokereval

def make_pair_hands(cards):
    """ Creates hands list from card in '88' like format.
    """
    # '55' -> [['5c', '5s'], ['5c', '5h'], ['5c', '5d'], ['5s', '5c'], ...
    possible_suits = (
                'cs', 'ch', 'cd', 'sc', 'sh', 'sd',
                'hc', 'hs', 'hd', 'dc', 'ds', 'dh'
            )
    hands = []
    for suits in possible_suits:
        hands.append(
                        [
                            '%s%s' % (cards[0], suits[0]),
                            '%s%s' % (cards[0], suits[1])
                        ]
                    )
    return hands

def make_suited_hands(cards):
    """ Creates hands list from card in 'A8s' like format.
    """
    # '75s' -> [['7c', '5c'], ['7s', '5s'], ['7h', '5h'], ['7d', '5d']]
    possible_suits = ('cc', 'hh', 'dd', 'ss')
    hands = []
    for suits in possible_suits:
        hands.append(
                        [
                            '%s%s' % (cards[0], suits[0]),
                            '%s%s' % (cards[1], suits[1])
                        ]
                    )
    return hands

def make_offsuited_hands(cards):
    """ Creates hands list from card in 'A8o' like format.
    """
    # '76o' -> [['7c', '6s'], ['7c', '6h'], ['7c', '6d'], ['7s', '6c'], ...
    possible_suits = (
              'cs', 'ch', 'cd', 'sc', 'sh', 'sd',
              'hc', 'hs', 'hd', 'dc', 'ds', 'dh',

              'sc', 'hc', 'dc', 'cs', 'hs', 'ds',
              'ch', 'sh', 'dh', 'cd', 'sd', 'hd'
            )
    hands = []
    for suits in possible_suits:
        hands.append(
                        [
                            '%s%s' % (cards[0], suits[0]),
                            '%s%s' % (cards[1], suits[1])
                        ]
                    )
    return hands

def make_hands(cards):
    """ Creates hands list from card in '88', 'A8o', 'A8s' like format.
    """
    if len(cards) == 2:
        return make_pair_hands(cards)
    elif cards[2] == 's':
        return make_suited_hands(cards)
    else:
        return make_offsuited_hands(cards)

def hands_from_range(cards_ranges):
    """ Creates card list from ranges list like:

            ['KK+', '44-22']  -> ['KK', 'AA', '22', '33', '44']

        Ranges format:

            'QQ+'       ->  ['QQ', 'KK', 'AA']
            'AJs+'      ->  ['AJs', 'AQs', 'AKs']
            'AJo+'      ->  ['AJo', 'AQo', 'AKo']
            '66-33'     ->  ['33', '44', '55', '66']
            'J5o-J3o'   ->  ['J3o', 'J4o', 'J5o']
            'J5s-J3s'   ->  ['J3s', 'J4s', 'J5s']

    """

    cards = []
    ranks = ('2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A')
    for crange in cards_ranges:
        crlen = len(crange)
        if crlen == 2:          # single pair like 'AA'
            cards.append(crange)
        elif crlen == 3:
            if crange[2] == '+':    # pair range like 'JJ+'
                for rank in range(ranks.index(crange[0]), len(ranks)):
                    cards.append(ranks[rank] * 2)
            else:               # card like 'AKs', 'QKo'
                cards.append(crange)
        elif crlen == 4:        # cards range like 'A5s+'
            for rank in range(ranks.index(crange[1]), len(ranks) - 1):
                cards.append('%s%s%s' % (crange[0], ranks[rank], crange[2]))
        elif crlen == 5:        # pair range like '66-33'
            for rank in range(ranks.index(crange[3]), ranks.index(crange[0])+1):
                cards.append(ranks[rank] * 2)
        elif crlen == 7:        # cards range like 'J5o-J3o'
            for rank in range(ranks.index(crange[5]), ranks.index(crange[1])+1):
                cards.append('%s%s%s' % (crange[0], ranks[rank], crange[2]))

    hands = []
    for fixme in cards:
        hands += make_hands(fixme)
    return hands


def compute_equity(pockets, dead=[], board=[], iterations=None):
    """ Compute hands equity.
    """

    pot_wins = [0] * len(pockets)

    pockets = [hands_from_range(p) for p in pockets]
    for pck in itertools.product(*pockets):
        lpck = []                       # F
        for x in pck:                   # I
            lpck += x                   # X
        if len(lpck) != len(set(lpck)): # M
            continue                    # E

        if iterations:
            result = pe.poker_eval(game='holdem', pockets = list(pck), dead = dead, fill_pockets=1, iterations=iterations, board=board)
        else:
            result = pe.poker_eval(game='holdem', pockets = list(pck), dead = dead, fill_pockets=1, board=board)

        for player, eval in enumerate(result['eval']):
            pot_wins[player] += (eval['winhi'] + eval['tiehi'] / 9.0) * result['info'][0]

    pots_wins_sum = sum(pot_wins)
    equity = []
    for pots in pot_wins:
        equity.append(100.0 * pots / pots_wins_sum)

    return equity


# vim: filetype=python syntax=python expandtab shiftwidth=4 softtabstop=4


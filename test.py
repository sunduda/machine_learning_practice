import numpy as np
import itertools, random


class Dealer:
    def __init__(self):
        self.name = 'Dealer'
        self.deck = list(itertools.product(range(1, 14), ['Spade', 'Heart', 'Diamond', 'Club']))
        self.cards, self.nhigh_aces, self.nlow_aces, self.total_points = [], 0, 0, 0
        self.rank = []
        self.score, self.n1st = 0, 0

    def new_game(self, players):
        if type(players) != list:
            list_players = [players, ]
        else:
            list_players = players
        for player in list_players:
            if not callable(getattr(player, "new_game", None)):
                return 1
            player.new_game()

        self._reset_status()
        self.shuffle_deck()

    def _reset_status(self):
        self.cards, self.nhigh_aces, self.nlow_aces, self.total_points = [], 0, 0, 0
        self.rank = []

    def shuffle_deck(self):
        # shuffle the cards
        if not self.cards:
            random.shuffle(self.deck)

    def deal(self, to_whom=None):
        # deal one card at a time
        if hasattr(to_whom, 'cards'):
            to_whom.cards.append(self.deck.pop(0))
        else:
            self.cards.append(self.deck.pop(0))

    @staticmethod
    def count_total_points(__o):
        if not hasattr(__o, 'nhigh_aces') or not hasattr(__o, 'nlow_aces') or not hasattr(__o, 'total_points'):
            return 1
        point_list = [c[0] if c[0] < 10 else 10 for c in __o.cards]
        other_cards = [p for p in point_list if p > 1]
        naces = len(point_list) - len(other_cards)
        if naces <= 0:
            __o.nhigh_aces = 0
            __o.nlow_aces = 0
            __o.total_points = np.sum(other_cards)
        else:
            __o.nhigh_aces = 1 if np.sum(other_cards) + naces + 10 <= 21 else 0
            __o.nlow_aces = naces - __o.nhigh_aces
            __o.total_points = np.sum(other_cards) + __o.nlow_aces + __o.nhigh_aces * 11

        return 0

    def should_hit(self):
        # if the dealer should hit the next card, return true
        Dealer.count_total_points(self)
        if self.total_points >= 17:
            return False
        else:
            return True

    def gaming(self, players):
        if type(players) != list:
            list_players = [players, ]
        else:
            list_players = players
        for player in list_players:
            if not callable(getattr(player, "should_hit", None)) or not hasattr(player, 'name') \
                    or not hasattr(player, 'total_points') or not hasattr(player, 'score'):
                return 1

        players_on = list_players.copy()
        for player in list_players:
            while player.should_hit():
                self.deal(player)
            if player.total_points > 21:
                self.rank.append(tuple(['Loser', player.name]))
                players_on.remove(player)
        if not players_on:
            self.rank.insert(0, tuple([1, self.name]))
            self.score += len(list_players)
        else:
            while self.should_hit():
                self.deal()
            if self.total_points > 21:
                self.rank.append(tuple(['Loser', self.name]))
            else:
                players_on.append(self)
            players_on = {p.name: p.total_points for p in players_on}
            players_on = sorted(players_on.items(), key=lambda x: (x[1], x[0]), reverse=True)
            for i in range(len(players_on)):
                if i > 0 and players_on[i][0] == self.name:
                    if players_on[i][1] < players_on[i - 1][1]:
                        break
                    for j in range(i - 2, -1, -1):
                        if players_on[i][1] < players_on[j][1]:
                            j += 1
                            break
                    popped = players_on.pop(i)
                    players_on.insert(j, popped)
            for i in range(len(players_on)):
                if i > 0 and players_on[i][1] == players_on[i - 1][1] and players_on[i - 1][0] != self.name:
                    self.rank.insert(i, tuple([self.rank[i - 1][0], players_on[i][0]]))
                else:
                    self.rank.insert(i, tuple([i + 1, players_on[i][0]]))
        return 0


class Player:
    def __init__(self, name):
        self.name = str(name)
        self.cards, self.nhigh_aces, self.nlow_aces, self.total_points = [], 0, 0, 0
        self.score, self.n1st = 0, 0

    def new_game(self):
        self._reset_status()

    def _reset_status(self):
        self.cards, self.nhigh_aces, self.nlow_aces, self.total_points = [], 0, 0, 0

    def should_hit(self):
        # if the dealer should hit the next card, return true
        Dealer.count_total_points(self)
        if self.total_points >= 21:
            return False
        else:
            return True


player1 = Player('Tom')
player2 = Player('Jim')
players = [player1, player2]
dealer = Dealer()

for i in range(3):
    dealer.new_game(players)
    dealer.gaming(players)
    print(dealer.rank)

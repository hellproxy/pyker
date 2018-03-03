from collections import deque

from turn import Turn
from action import *


class BettingRound:

    def __init__(self, seats, remaining_seats, cards, min_raise, bet=0):
        print("\n=================== BETTING ROUND ===================")
        self.seats = seats
        self.remaining_seats = remaining_seats
        self.filtered_seats = deque(remaining_seats)
        self.cards = cards
        self.min_raise = min_raise

        self.current_bet = bet
        self.end_seat = self.filtered_seats[-1]

    def play(self):
        last_action = None

        while True:
            seat = self.filtered_seats[0]

            turn = Turn(
                self.seats,
                self.filtered_seats,
                self.cards,
                self.current_bet,
                last_action,
                self.min_raise
            )

            last_action = turn.play()
            self.resolve_action(seat, last_action)

            if len(self.filtered_seats) == 1:
                self.move_all_bets_to_pots()
                return self.filtered_seats[0:1]

            if seat is self.end_seat:
                # bets have been called
                self.move_all_bets_to_pots()
                return [seat for seat in self.remaining_seats if seat in self.filtered_seats]

            self.filtered_seats.rotate(-1)

    def move_all_bets_to_pots(self):
        for seat in self.seats:
            seat.move_bet_to_pot()

    def resolve_action(self, seat, action):
        if isinstance(action, Fold):
            del self.filtered_seats[0]
        elif isinstance(action, CheckCall):
            seat.bet_chips(self.current_bet)
        elif isinstance(action, Raise):
            self.end_seat = self.filtered_seats[-1]
            self.current_bet += action.amount
            seat.bet_chips(self.current_bet)

from collections import deque
import logging

from turn import Turn
from action import *


class BettingRound:

    def __init__(self, seats, remaining_seats, cards, min_raise, bet=0):
        logging.info("NEW BETTING ROUND")
        self.seats = deque(seats)
        self.remaining_seats = remaining_seats
        self.filtered_seats = deque(remaining_seats)
        self.cards = cards
        self.min_raise = min_raise
        self.current_bet = bet

    def play(self):
        last_action = None
        self.end_seat = self.filtered_seats[-1]
        self.align_seat_deques()

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
                logging.info("Player {} wins".format(self.filtered_seats[0].index))
                self.move_all_bets_to_pots()
                return list(self.filtered_seats)

            if seat is self.end_seat:
                # bets have been called
                self.move_all_bets_to_pots()
                return [seat for seat in self.remaining_seats if seat in self.filtered_seats]

            self.filtered_seats.rotate(-1)
            self.align_seat_deques()

    def align_seat_deques(self):
        while self.seats[0] != self.filtered_seats[0]:
            self.seats.rotate(-1)

    def move_all_bets_to_pots(self):
        for seat in self.seats:
            seat.move_bet_to_pot()

    def resolve_action(self, seat, action):
        if isinstance(action, Fold):
            del self.filtered_seats[0]
            self.filtered_seats.rotate()
            logging.info("Player {} folds".format(seat.index))
        elif isinstance(action, CheckCall):
            call_amount = self.current_bet - seat.bet
            seat.bet_chips(call_amount)

            if call_amount == 0:
                logging.info("Player {} checks".format(seat.index))
            else:
                logging.info("Player {} calls, putting in {}".format(seat.index, call_amount))
        elif isinstance(action, Raise):
            self.end_seat = self.filtered_seats[-1]

            call_amount = self.current_bet - seat.bet
            seat.bet_chips(call_amount)

            raise_amount = seat.bet_chips(action.amount)
            self.current_bet += raise_amount

            logging.info("Player {} raises {}".format(seat.index, raise_amount))


class PreFlop(BettingRound):

    def __init__(self, seats, remaining_seats, cards, min_raise, big_blind):
        super().__init__(seats, remaining_seats, cards, min_raise, big_blind)

    def play(self):
        # start left of small blind
        self.filtered_seats.rotate(-3)
        return super().play()

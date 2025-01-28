from db import get_players_to_pay, pay_player
import math

def get_curves_value(positions: int, place: int) -> float:
    return 0.52430132 * (positions * place) ** -0.477

def get_curves_sum(positions: int) -> float:
    curves_sum = 0.0
    for i in range(1, positions + 1):
        curves_sum += get_curves_value(positions, i)
    return curves_sum

def payouts(player_count: int) -> list:
    payout = []
    positions = int(math.ceil(player_count * 0.45))
    curves_sum = get_curves_sum(positions)
    for i in range(1, positions + 1):
        payout.append(round((player_count * 2) * get_curves_value(positions, i) / curves_sum))
    return payout



def payout_manager(current_date: str):
    player_place = {}
    player_db_return, err = get_players_to_pay(current_date)
    player_count = 0
    if not err:
        if player_db_return:
            for player_id, player_place_val in player_db_return:
                if player_place_val:
                    if player_place_val not in player_place:
                        player_place[player_place_val] = []
                    player_count += 1
                    player_place[player_place_val].append(player_id)
        else:
            return f"no payable players for {current_date}"
    else:
        return err

    payout_list = payouts(player_count)
    if payout_list is None or not payout_list: # Check if payout_list is None OR empty
        return f"No payouts available for {current_date} or payout list is empty"
    for place_key in sorted(player_place.keys()):
        num_players_in_place = len(player_place[place_key])
        num_payouts_remaining = len(payout_list)
        if num_players_in_place <= num_payouts_remaining:
            payout_val = sum(payout_list[:num_players_in_place]) / num_players_in_place
            payout_list = payout_list[num_players_in_place:]
        else:
            payout_val = sum(payout_list) / num_players_in_place
            payout_list = [] # Exhaust the payout list since there are not enough payouts for all players
        for id in player_place[place_key]:
            outcome, err = pay_player(id, payout_val)
            if not outcome:
                return err

    return f"payouts done for {current_date}"




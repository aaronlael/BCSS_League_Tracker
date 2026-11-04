import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


database_stub = types.ModuleType('db')
database_stub.get_players_to_pay = None
database_stub.pay_player = None
with patch.dict(sys.modules, {'db': database_stub}):
    module_spec = importlib.util.spec_from_file_location(
        'payout_under_test',
        Path(__file__).resolve().parents[1] / 'payout.py',
    )
    payout = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(payout)


class PayoutTests(unittest.TestCase):
    def test_rounding_never_exceeds_entry_pool(self):
        for player_count in range(1, 501):
            with self.subTest(player_count=player_count):
                result = payout.payouts(player_count)
                self.assertEqual(sum(result), player_count * 2)
                self.assertTrue(all(amount >= 0 for amount in result))
                self.assertEqual(result, sorted(result, reverse=True))

    def test_tied_third_place_stays_within_seven_player_pool(self):
        players = [(player_id, place) for player_id, place in enumerate(
            [1, 2, 3, 3, 5, 6, 7],
            start=1,
        )]
        payments = []

        with (
            patch.object(payout, 'get_players_to_pay', return_value=(players, None)),
            patch.object(
                payout,
                'pay_player',
                side_effect=lambda player_id, amount: (
                    payments.append((player_id, amount)) or (True, None)
                ),
            ),
        ):
            result = payout.payout_manager('2026-11-03')

        self.assertEqual(result, 'payouts done for 2026-11-03')
        self.assertEqual(payments[:4], [(1, 6.0), (2, 4.0), (3, 2.0), (4, 2.0)])
        self.assertEqual(sum(amount for _, amount in payments), 14)


if __name__ == '__main__':
    unittest.main()

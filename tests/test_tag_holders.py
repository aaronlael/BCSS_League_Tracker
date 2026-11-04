import datetime
import unittest

from tag_history import select_current_tag_holders


class CurrentTagHolderTests(unittest.TestCase):
    def test_selects_latest_holder_per_tag_and_one_tag_per_player(self):
        records = [
            ('Alex', 1, datetime.date(2026, 1, 4), 1),
            ('Blair', 1, datetime.date(2026, 2, 1), 2),
            ('Casey', 2, datetime.date(2026, 2, 2), 3),
            ('casey', 3, datetime.date(2026, 2, 2), 4),
            ('Drew', 3, datetime.date(2026, 2, 3), 5),
            ('Evan', 4, datetime.date(2026, 2, 3), 6),
        ]

        holders = select_current_tag_holders(records)

        self.assertEqual(
            holders,
            [
                ('Blair', 1, datetime.date(2026, 2, 1)),
                ('Casey', 2, datetime.date(2026, 2, 2)),
                ('Drew', 3, datetime.date(2026, 2, 3)),
                ('Evan', 4, datetime.date(2026, 2, 3)),
            ],
        )
        self.assertEqual(len({tag for _, tag, _ in holders}), len(holders))
        self.assertEqual(
            len({name.casefold() for name, _, _ in holders}),
            len(holders),
        )

    def test_same_day_duplicate_rows_use_later_record_id(self):
        records = [
            ('Alex', 10, datetime.date(2026, 5, 3), 12),
            ('Blair', 10, datetime.date(2026, 5, 3), 13),
        ]

        self.assertEqual(
            select_current_tag_holders(records),
            [('Blair', 10, datetime.date(2026, 5, 3))],
        )


if __name__ == '__main__':
    unittest.main()

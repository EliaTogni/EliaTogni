import unittest

from city.data import CalendarError, parse_response


def payload(weeks):
    return {
        "data": {
            "user": {
                "contributionsCollection": {
                    "contributionCalendar": {
                        "weeks": [
                            {"contributionDays": [{"date": d, "contributionCount": c} for d, c in week]}
                            for week in weeks
                        ]
                    }
                }
            }
        }
    }


class ParseResponseTest(unittest.TestCase):
    def test_weekday_comes_from_date_not_position(self):
        days = parse_response(payload([[("2025-11-25", 1), ("2025-11-26", 0)], [("2025-11-30", 2)]]))
        self.assertEqual([(d.week, d.weekday) for d in days], [(0, 2), (0, 3), (1, 0)])

    def test_counts_and_dates_are_kept_in_order(self):
        days = parse_response(payload([[("2025-11-23", 5), ("2025-11-24", 0)]]))
        self.assertEqual([(d.date, d.count) for d in days], [("2025-11-23", 5), ("2025-11-24", 0)])

    def test_graphql_errors_raise(self):
        with self.assertRaises(CalendarError):
            parse_response({"errors": [{"message": "Bad credentials"}]})

    def test_null_user_raises(self):
        with self.assertRaises(CalendarError):
            parse_response({"data": {"user": None}})


if __name__ == "__main__":
    unittest.main()

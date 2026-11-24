import re
import unittest
import xml.etree.ElementTree as ET
from datetime import date, timedelta

from city.data import Day
from city.render import DARK, LIGHT, render_svg


def year(counts):
    start = date(2025, 11, 23)  # a Sunday
    return [Day(i // 7, i % 7, c, (start + timedelta(days=i)).isoformat()) for i, c in enumerate(counts)]


class RenderSvgTest(unittest.TestCase):
    def test_one_building_per_active_day_and_one_tile_per_empty_day(self):
        svg = render_svg(year([0, 3, 0, 7]), DARK)
        self.assertEqual(svg.count('class="b"'), 2)
        self.assertEqual(svg.count("data-tile"), 2)

    def test_output_is_well_formed_xml_and_deterministic(self):
        days = year([1, 4, 9, 12, 0, 30])
        ET.fromstring(render_svg(days, DARK))
        self.assertEqual(render_svg(days, DARK), render_svg(days, DARK))

    def test_text_shows_total_and_active_days(self):
        svg = render_svg(year([1000, 801, 0]), LIGHT)
        self.assertIn(">1,801<", svg)
        self.assertIn("contributions in the last year · 2 active days", svg)
        self.assertNotIn("As a city", svg)

    def test_single_active_day_is_singular(self):
        self.assertIn("· 1 active day<", render_svg(year([0, 5, 0]), DARK))

    def test_empty_year_renders_ground_only(self):
        svg = render_svg(year([0] * 30), DARK)
        ET.fromstring(svg)
        self.assertEqual(svg.count('class="b"'), 0)
        self.assertIn(">0<", svg)

    def test_outlier_day_is_capped(self):
        capped = render_svg(year([1, 400]), DARK)
        self.assertEqual(capped, render_svg(year([1, 64]), DARK).replace(">65<", ">401<"))

    def test_glow_only_in_dark_theme(self):
        days = year([1, 2, 3, 4, 5, 6, 7, 8, 40])
        self.assertIn("feGaussianBlur", render_svg(days, DARK))
        self.assertNotIn("feGaussianBlur", render_svg(days, LIGHT))

    def test_delays_follow_date_order(self):
        svg = render_svg(year([1] * 10), DARK)
        delays = [float(x) for x in re.findall(r"animation-delay:([\d.]+)s", svg)]
        self.assertEqual(sorted(delays), [round(i / 10 * 3.6, 2) for i in range(10)])


if __name__ == "__main__":
    unittest.main()

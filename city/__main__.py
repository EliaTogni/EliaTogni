"""Writes city-dark.svg and city-light.svg for a GitHub user."""
import argparse
import os
import sys

from city.data import CalendarError, fetch_days
from city.render import DARK, LIGHT, render_svg


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="python3 -m city")
    parser.add_argument("--login", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args(argv)

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("GITHUB_TOKEN is not set", file=sys.stderr)
        return 1
    try:
        days = fetch_days(args.login, token)
    except CalendarError as e:
        print(f"cannot read the contribution calendar: {e}", file=sys.stderr)
        return 1

    svgs = {"city-dark.svg": render_svg(days, DARK), "city-light.svg": render_svg(days, LIGHT)}
    os.makedirs(args.out_dir, exist_ok=True)
    for name, svg in svgs.items():
        with open(os.path.join(args.out_dir, name), "w", encoding="utf-8") as f:
            f.write(svg)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

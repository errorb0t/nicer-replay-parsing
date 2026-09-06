import argparse

from .parse_replay import print_replay_contents


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Print the decoded contents of a Heroes of the Storm replay."
    )
    parser.add_argument("filename", help=".StormReplay file to print")
    args = parser.parse_args(argv)

    print_replay_contents(args.filename)

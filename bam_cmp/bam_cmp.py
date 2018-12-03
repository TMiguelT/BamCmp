#!/usr/bin/env python3
import argparse
import pysam
import pathlib
from dataclasses import dataclass
import typing
import os


@dataclass
class Comparison:
    left_id: str
    right_id: str


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('bam_a', type=pathlib.Path)
    parser.add_argument('bam_b', type=pathlib.Path)
    parser.add_argument('--ignore-tags', action='store_true')
    return parser


def _compare_alignments(
        a: pysam.AlignmentFile,
        b: pysam.AlignmentFile,
        ignore_tags: bool
) -> typing.Iterable[Comparison]:
    comparisons = []

    for al_a, al_b in zip(a, b):

        if ignore_tags:
            al_a.set_tags([])
            al_b.set_tags([])

        comp = al_a.compare(al_b)

        if comp != 0:
            comparisons.append(Comparison(al_a.qname, al_b.qname))

    return comparisons


def compare(bam_a: os.PathLike, bam_b: os.PathLike, ignore_tags: bool) -> typing.Iterable[Comparison]:
    al_a = pysam.AlignmentFile(bam_a)
    al_b = pysam.AlignmentFile(bam_b)
    return _compare_alignments(al_a, al_b, ignore_tags)


def main():
    args = get_parser().parse_args()
    for comparison in compare(args.bam_a, args.bam_b, args.ignore_tags):
        print('{} differs from {}'.format(comparison.left_id, comparison.right_id))


if __name__ == '__main__':
    main()

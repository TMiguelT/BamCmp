#!/usr/bin/env python3
import argparse
import pysam
import pathlib
from dataclasses import dataclass
import typing
import os
from deepdiff import DeepDiff


@dataclass
class Comparison:
    left_id: str
    right_id: str
    diff: dict


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('bam_a', type=pathlib.Path)
    parser.add_argument('bam_b', type=pathlib.Path)
    parser.add_argument('--reference', type=pathlib.Path)
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
            ddiff = DeepDiff(al_a.to_dict(), al_b.to_dict())
            comparisons.append(Comparison(
                al_a.qname,
                al_b.qname,
                ddiff
            ))

    return comparisons


def open_alignment(path: os.PathLike, reference: os.PathLike = None) -> pysam.AlignmentFile:
    suffix = pathlib.Path(path).suffix

    if suffix == '.bam':
        return pysam.AlignmentFile(path, 'rb', reference_filename=reference)
    elif suffix == '.cram':
        return pysam.AlignmentFile(path, 'rc', reference_filename=reference)
    else:
        return pysam.AlignmentFile(path, 'r', reference_filename=reference)


def compare(
        bam_a: os.PathLike,
        bam_b: os.PathLike,
        ignore_tags: bool,
        reference: os.PathLike = None
) -> typing.Iterable[Comparison]:
    al_a = open_alignment(bam_a, reference)
    al_b = open_alignment(bam_b, reference)
    return _compare_alignments(al_a, al_b, ignore_tags)


def main():
    args = get_parser().parse_args()
    for comparison in compare(args.bam_a, args.bam_b, args.ignore_tags, args.reference):
        print('{} differs from {}. Difference: {}'.format(comparison.left_id, comparison.right_id, comparison.diff))


if __name__ == '__main__':
    main()

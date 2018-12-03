#!/usr/bin/env python3
import argparse
import pysam
import pathlib
from dataclasses import dataclass
import typing
import os
import sys
from deepdiff import DeepDiff


@dataclass
class Comparison:
    left_id: str
    right_id: str
    diff: dict


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'bam_a',
        type=pathlib.Path
    )
    parser.add_argument(
        'bam_b',
        type=pathlib.Path
    )
    parser.add_argument(
        '--reference',
        type=pathlib.Path,
        help='Path to reference fasta file, needed for CRAM alignments'
    )
    parser.add_argument(
        '--ignore-tags',
        action='store_true',
        help='Ignore the optional tags section for each segment'
    )
    parser.add_argument(
        '--sort-tags',
        action='store_true',
        help='Sort tag dictionary before comparing, meaning that alignments with differently ordered tags will still '
             'be considered identical'
    )
    return parser


def _compare_alignments(
        a: pysam.AlignmentFile,
        b: pysam.AlignmentFile,
        ignore_tags: bool = False,
        sort_tags: bool = False
) -> typing.Iterable[Comparison]:
    comparisons = []

    for al_a, al_b in zip(a, b):

        if sort_tags:
            al_a.set_tags(sorted(al_a.get_tags()))
            al_b.set_tags(sorted(al_b.get_tags()))

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
        ignore_tags: bool = False,
        sort_tags: bool = False,
        reference: os.PathLike = None
) -> typing.Iterable[Comparison]:
    al_a = open_alignment(bam_a, reference)
    al_b = open_alignment(bam_b, reference)
    return _compare_alignments(al_a, al_b, ignore_tags=ignore_tags, sort_tags=sort_tags)


def main():
    args = get_parser().parse_args()

    # Compare all segments
    comparisons = compare(
            args.bam_a,
            args.bam_b,
            sort_tags=args.sort_tags,
            ignore_tags=args.ignore_tags,
            reference=args.reference
    )

    # Print the differences to stdout
    for comparison in comparisons:
        print('{} differs from {}. Difference: {}'.format(comparison.left_id, comparison.right_id, comparison.diff))

    # Exit with a nonzero exit code if we had any differences
    if len(comparisons) > 0:
       sys.exit(1)
    else:
        print('Alignment files were identical.')
        sys.exit(0)


if __name__ == '__main__':
    main()

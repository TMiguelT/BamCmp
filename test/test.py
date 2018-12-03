import unittest
from bam_cmp.bam_cmp import compare
from pkg_resources import resource_filename

NO_TAGS = resource_filename('test.test', 'no_tags.sam')
TAGS_A = resource_filename('test.test', 'tags_a.sam')
TAGS_B = resource_filename('test.test', 'tags_b.sam')


class Simple(unittest.TestCase):
    def test_same(self):
        """
        Any SAM should pass when compared to itself
        """
        comparisons = compare(NO_TAGS, NO_TAGS, ignore_tags=False)
        self.assertEqual(len(comparisons), 0)


class Tags(unittest.TestCase):
    def test_tag_no_tag(self):
        """
        Should fail if one SAM has tags and the other doesn't
        """
        comparisons = compare(NO_TAGS, TAGS_A, ignore_tags=False)
        self.assertEqual(len(comparisons), 1)

    def test_tag_no_tag_ignore(self):
        """
        Should pass if one SAM has tags and the other doesn't,but ignore tags is true
        """
        comparisons = compare(NO_TAGS, TAGS_A, ignore_tags=True)
        self.assertEqual(len(comparisons), 0)

    def test_different_tags(self):
        """
        Should fail if one SAM has tags that are different from the other
        """
        comparisons = compare(TAGS_A, TAGS_B, ignore_tags=False)
        self.assertEqual(len(comparisons), 1)

    def test_different_tags_ignore(self):
        """
        Should pass if one SAM has tags that are different from the other, but ignore tags is true
        """
        comparisons = compare(TAGS_A, TAGS_B, ignore_tags=True)
        self.assertEqual(len(comparisons), 0)

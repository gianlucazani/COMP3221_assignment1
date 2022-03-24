from unittest import TestCase

from assignment1.lib import extract_path


class Test(TestCase):
    def test_extract_path(self):
        self.assertEqual(extract_path({'A': (0.0, 'A'), 'B': (2.0, 'A'), 'C': (1.0, 'A'), 'D': (2.0, 'C'), 'E': (3.0, 'B'), 'F': (5.0, 'D')}, "A", "F"), "ACDF")

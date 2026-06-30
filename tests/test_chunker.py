"""Unit tests for pocketknife.chunker."""

import unittest

from pocketknife.chunker import paginate


class TestPaginate(unittest.TestCase):
    def test_even_division(self):
        result = list(paginate([1, 2, 3, 4], 2))
        self.assertEqual(result, [[1, 2], [3, 4]])

    def test_uneven_division_last_chunk_smaller(self):
        result = list(paginate([1, 2, 3, 4, 5], 2))
        self.assertEqual(result, [[1, 2], [3, 4], [5]])

    def test_chunk_size_larger_than_iterable(self):
        result = list(paginate([1, 2, 3], 10))
        self.assertEqual(result, [[1, 2, 3]])

    def test_chunk_size_one(self):
        result = list(paginate([1, 2, 3], 1))
        self.assertEqual(result, [[1], [2], [3]])

    def test_empty_iterable_yields_nothing(self):
        result = list(paginate([], 5))
        self.assertEqual(result, [])

    def test_works_on_string(self):
        result = list(paginate("abcdef", 4))
        self.assertEqual(result, [["a", "b", "c", "d"], ["e", "f"]])

    def test_works_on_generator(self):
        def gen():
            yield from range(5)

        result = list(paginate(gen(), 2))
        self.assertEqual(result, [[0, 1], [2, 3], [4]])

    def test_works_on_tuple(self):
        result = list(paginate((1, 2, 3, 4, 5), 3))
        self.assertEqual(result, [[1, 2, 3], [4, 5]])

    def test_preserves_order(self):
        result = list(paginate(range(10), 4))
        flattened = [item for chunk in result for item in chunk]
        self.assertEqual(flattened, list(range(10)))

    def test_is_lazy_generator(self):
        # paginate should return a generator/iterator, not a list,
        # so it can be used on infinite sequences.
        gen = paginate(range(1000), 10)
        first_chunk = next(gen)
        self.assertEqual(first_chunk, list(range(10)))

    def test_zero_size_raises_value_error(self):
        with self.assertRaises(ValueError):
            list(paginate([1, 2, 3], 0))

    def test_negative_size_raises_value_error(self):
        with self.assertRaises(ValueError):
            list(paginate([1, 2, 3], -1))

    def test_non_integer_size_raises_value_error(self):
        with self.assertRaises(ValueError):
            list(paginate([1, 2, 3], 2.5))

    def test_does_not_materialize_infinite_generator_eagerly(self):
        # Only pull a few chunks from an infinite generator; if paginate
        # eagerly consumed the whole thing this would hang forever.
        def infinite():
            i = 0
            while True:
                yield i
                i += 1

        gen = paginate(infinite(), 3)
        first = next(gen)
        second = next(gen)
        self.assertEqual(first, [0, 1, 2])
        self.assertEqual(second, [3, 4, 5])


if __name__ == "__main__":
    unittest.main()

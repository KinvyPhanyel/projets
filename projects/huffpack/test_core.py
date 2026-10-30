import unittest
from core import compress, decompress
import random


class Tests(unittest.TestCase):
    def test_roundtrips(self):
        rng = random.Random(42)
        for data in [
            b"",
            b"a",
            b"a" * 100,
            bytes(range(256)),
            bytes(rng.randrange(256) for _ in range(4096)),
        ]:
            packed = compress(data)
            self.assertEqual(decompress(packed), data)
            self.assertEqual(packed, compress(data))

    def test_corruption_and_truncation(self):
        packed = compress(b"abracadabra" * 30)
        bad = bytearray(packed)
        bad[-1] ^= 128
        with self.assertRaises(ValueError):
            decompress(bytes(bad))
        with self.assertRaises(ValueError):
            decompress(packed[:-1])
        with self.assertRaises(ValueError):
            decompress(packed + b"junk")

    def test_output_limit(self):
        with self.assertRaises(ValueError):
            decompress(compress(b"a" * 100), max_output=10)


if __name__ == "__main__":
    unittest.main()

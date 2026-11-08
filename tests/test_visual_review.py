"""Review sampling must cover opening, each sequence and final frames."""
import unittest
from src.visual_review import sample_times


class VisualSamplingTests(unittest.TestCase):
    def test_video_twenty_seconds_includes_both_ten_second_sequences(self):
        ts = sample_times(20.032, interval=2)
        self.assertTrue(any(t < 2 for t in ts))
        self.assertTrue(any(8 < t < 10 for t in ts))
        self.assertTrue(any(10 < t < 12 for t in ts))
        self.assertTrue(ts[-1] > 19)

    def test_short_video(self):
        self.assertEqual(sample_times(0.1), [0.0])

    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            sample_times(0)
        with self.assertRaises(ValueError):
            sample_times(10, interval=0)


if __name__ == "__main__":
    unittest.main()

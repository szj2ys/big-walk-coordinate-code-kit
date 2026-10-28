import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from grid_codes import decode_code, encode_reading


class GridCodeTests(unittest.TestCase):
    def test_all_codes_round_trip_without_losing_zeros(self):
        for number in range(10000):
            code = f"{number:04d}"
            self.assertEqual(encode_reading(decode_code(code)), code)

    def test_rejects_ambiguous_or_non_ascii_codes(self):
        for value in ["416", "41666", "41.66", "-025", "4e66", "４１６６"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                decode_code(value)

    def test_reverse_rejects_nonfinite_range_and_rounding(self):
        for value in ["NaN", "Infinity", "-0.01", "100", "1.001", "oops"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                encode_reading(value)

    def test_precision_beyond_decimal_context_is_never_rounded(self):
        for value in ["1.00000000000000000000000000001", "1e-1000000"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                encode_reading(value)
        self.assertEqual(encode_reading("1.00000000000000000000000000000"), "0100")
        self.assertEqual(encode_reading("0e1000000"), "0000")

    def test_real_cli_batch_preserves_strings_and_labels(self):
        command = [sys.executable, "grid_codes.py", "--csv", "examples.csv", "--format", "json"]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        rows = json.loads(result.stdout)
        self.assertEqual(rows[0]["side_reading"], "41.66")
        self.assertEqual(rows[0]["bottom_reading"], "18.99")
        self.assertEqual(rows[1]["side_code"], "0025")
        self.assertIn("Synthetic", rows[1]["label"])

    def test_bad_csv_line_produces_no_partial_stdout(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "bad.csv"
            file.write_text("side_code,bottom_code\n4166,1899\n25,0900\n", encoding="utf-8")
            result = subprocess.run([sys.executable, "grid_codes.py", "--csv", str(file)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, "")
            self.assertIn("CSV line 3", result.stderr)


if __name__ == "__main__":
    unittest.main()

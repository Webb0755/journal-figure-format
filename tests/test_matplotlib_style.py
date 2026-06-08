from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from matplotlib_style import (
    load_style,
    normalize_output_format,
    normalize_style,
)


class MatplotlibStyleTests(unittest.TestCase):
    def test_normalizers(self) -> None:
        self.assertEqual(normalize_style("nature"), "Nature")
        self.assertEqual(normalize_output_format("tif"), "tiff")

    def test_load_style_sets_expected_values(self) -> None:
        params = load_style("Nature", "1-column", "pdf")
        self.assertEqual(params["figure.figsize"], (3.50394, 3))
        self.assertEqual(params["savefig.format"], "pdf")
        self.assertEqual(params["savefig.dpi"], 600)

    def test_invalid_style_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            normalize_style("unknown")


if __name__ == "__main__":
    unittest.main()

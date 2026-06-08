from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from figure_prepare import get_preset, inspect_image


class FigurePrepareTests(unittest.TestCase):
    def test_known_preset(self) -> None:
        preset = get_preset("nature")
        self.assertEqual(preset.name, "Nature Portfolio")
        self.assertEqual(preset.dpi_by_type["combo"], 600)

    def test_inspect_image_returns_target_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            image_path = Path(temp_dir) / "figure.png"
            Image.new("RGB", (2400, 1200), "white").save(
                image_path,
                dpi=(300, 300),
            )

            report = inspect_image(
                image_path,
                journal="nature",
                figure_type="photo",
                width_class="single",
                width_mm=None,
            )

        self.assertEqual(report["preset"], "Nature Portfolio")
        self.assertEqual(report["source"]["width_px"], 2400)
        self.assertEqual(report["target"]["width_mm"], 89)
        self.assertEqual(report["target"]["dpi"], 300)
        self.assertEqual(report["status"], "pass")


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Inspect and export raster figures for journal submission presets."""

from __future__ import annotations

import argparse
import json
import math
from io import BytesIO
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from PIL import Image
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Pillow is required. Install it with: python3 -m pip install pillow") from exc


MM_PER_INCH = 25.4


@dataclass(frozen=True)
class Preset:
    name: str
    single_width_mm: float
    double_width_mm: float
    dpi_by_type: dict[str, int]
    preferred_format: str = "tif"
    color_mode: str = "RGB"


PRESETS: dict[str, Preset] = {
    "nature": Preset("Nature Portfolio", 89, 183, {"photo": 300, "combo": 600, "line": 1200}),
    "science": Preset("Science / AAAS", 89, 178, {"photo": 300, "combo": 600, "line": 1200}),
    "cell": Preset("Cell Press", 85, 180, {"photo": 300, "combo": 600, "line": 1200}),
    "plos": Preset("PLOS", 85, 180, {"photo": 300, "combo": 600, "line": 1200}),
    "ieee": Preset("IEEE", 88.9, 182.9, {"photo": 300, "combo": 600, "line": 1200}),
    "elsevier": Preset("Elsevier", 90, 180, {"photo": 300, "combo": 600, "line": 1000}),
    "springer": Preset("Springer Nature", 85, 180, {"photo": 300, "combo": 600, "line": 1200}),
    "acs": Preset("ACS", 85, 180, {"photo": 300, "combo": 600, "line": 1200}),
    "wiley": Preset("Wiley", 85, 180, {"photo": 300, "combo": 600, "line": 1200}),
}


def get_preset(name: str) -> Preset:
    key = name.lower().strip()
    if key not in PRESETS:
        known = ", ".join(sorted(PRESETS))
        raise SystemExit(f"Unknown journal preset '{name}'. Known presets: {known}")
    return PRESETS[key]


def image_dpi(img: Image.Image) -> tuple[float, float]:
    dpi = img.info.get("dpi", (72, 72))
    try:
        return float(dpi[0]), float(dpi[1])
    except (TypeError, ValueError, IndexError):
        return 72.0, 72.0


def target_width_mm(preset: Preset, width_class: str, width_mm: float | None) -> float:
    if width_mm:
        return width_mm
    if width_class == "single":
        return preset.single_width_mm
    if width_class == "double":
        return preset.double_width_mm
    raise SystemExit("width_class must be 'single' or 'double'")


def inspect_image(path: Path, journal: str, figure_type: str, width_class: str, width_mm: float | None) -> dict[str, Any]:
    preset = get_preset(journal)
    with Image.open(path) as img:
        dpi_x, dpi_y = image_dpi(img)
        target_dpi = preset.dpi_by_type[figure_type]
        target_mm = target_width_mm(preset, width_class, width_mm)
        required_px = math.ceil(target_mm / MM_PER_INCH * target_dpi)
        source_px = img.width
        scale_factor = required_px / source_px
        status = "pass"
        warnings: list[str] = []

        if source_px < required_px:
            status = "needs-source-improvement" if scale_factor > 1.1 else "pass-with-warnings"
            warnings.append(
                f"Source width is {source_px}px; target needs {required_px}px at {target_mm:g} mm and {target_dpi} dpi."
            )
        if img.mode not in ("RGB", "L", "CMYK"):
            warnings.append(f"Source mode is {img.mode}; export will convert to {preset.color_mode}.")
            if status == "pass":
                status = "pass-with-warnings"

        return {
            "input": str(path),
            "preset": preset.name,
            "figure_type": figure_type,
            "source": {
                "format": img.format,
                "mode": img.mode,
                "width_px": img.width,
                "height_px": img.height,
                "dpi": [dpi_x, dpi_y],
            },
            "target": {
                "width_mm": target_mm,
                "dpi": target_dpi,
                "required_width_px": required_px,
                "preferred_format": preset.preferred_format,
                "color_mode": preset.color_mode,
            },
            "scale_factor": round(scale_factor, 4),
            "status": status,
            "warnings": warnings,
        }


def save_report(report: dict[str, Any], output_dir: Path, stem: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{stem}_compliance.json"
    md_path = output_dir / f"{stem}_compliance.md"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = [
        f"# Figure Compliance: {Path(report['input']).name}",
        "",
        f"- Preset: {report['preset']}",
        f"- Figure type: {report['figure_type']}",
        f"- Status: {report['status']}",
        f"- Target width: {report['target']['width_mm']} mm",
        f"- Target dpi: {report['target']['dpi']}",
        f"- Required width: {report['target']['required_width_px']} px",
        f"- Source: {report['source']['width_px']} x {report['source']['height_px']} px, {report['source']['mode']}",
        "",
    ]
    if report["warnings"]:
        lines.append("## Warnings")
        lines.extend(f"- {warning}" for warning in report["warnings"])
        lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")


def save_pdf(exported: Image.Image, output_path: Path, dpi: int) -> None:
    try:
        from reportlab.lib.utils import ImageReader
        from reportlab.pdfgen import canvas
    except ImportError as exc:  # pragma: no cover
        raise SystemExit("ReportLab is required for PDF export. Install it with: python3 -m pip install reportlab") from exc

    width_pt = exported.width / dpi * 72
    height_pt = exported.height / dpi * 72
    buffer = BytesIO()
    exported.save(buffer, format="PNG")
    buffer.seek(0)

    pdf = canvas.Canvas(str(output_path), pagesize=(width_pt, height_pt))
    pdf.drawImage(ImageReader(buffer), 0, 0, width=width_pt, height=height_pt, preserveAspectRatio=True)
    pdf.showPage()
    pdf.save()


def save_eps(exported: Image.Image, output_path: Path) -> None:
    exported.save(output_path, format="EPS")


def export_image(args: argparse.Namespace) -> dict[str, Any]:
    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    report = inspect_image(input_path, args.journal, args.figure_type, args.width_class, args.width_mm)
    target = report["target"]
    output_format = args.format.lower() if args.format else target["preferred_format"]
    suffix_by_format = {
        "eps": ".eps",
        "pdf": ".pdf",
        "tif": ".tif",
        "tiff": ".tif",
    }
    suffix = suffix_by_format[output_format]
    output_path = output_dir / f"{input_path.stem}_{args.journal}_{args.figure_type}{suffix}"

    with Image.open(input_path) as img:
        target_width_px = int(target["required_width_px"])
        ratio = target_width_px / img.width
        target_height_px = max(1, round(img.height * ratio))
        resample = Image.Resampling.LANCZOS
        exported = img.convert(target["color_mode"]).resize((target_width_px, target_height_px), resample)
        output_dir.mkdir(parents=True, exist_ok=True)
        save_kwargs: dict[str, Any] = {"dpi": (target["dpi"], target["dpi"])}
        if suffix == ".tif":
            save_kwargs["compression"] = args.compression
            exported.save(output_path, **save_kwargs)
        elif suffix == ".pdf":
            save_pdf(exported, output_path, target["dpi"])
        else:
            save_eps(exported, output_path)
            report["warnings"].append("EPS was exported from raster pixels; use Matplotlib/vector source for true vector EPS.")
            if report["status"] == "pass":
                report["status"] = "pass-with-warnings"

    report["output"] = str(output_path)
    report["output_dimensions_px"] = [target_width_px, target_height_px]
    save_report(report, output_dir, input_path.stem)
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command in ("inspect", "export"):
        sub = subparsers.add_parser(command)
        sub.add_argument("input", help="Input raster figure path")
        sub.add_argument("--journal", default="nature", help="Preset key")
        sub.add_argument("--figure-type", choices=("photo", "combo", "line"), default="combo")
        sub.add_argument("--width-class", choices=("single", "double"), default="single")
        sub.add_argument("--width-mm", type=float, help="Override final figure width in millimeters")

        if command == "export":
            sub.add_argument("--output-dir", default="figures_ready")
            sub.add_argument("--format", choices=("eps", "pdf", "tif", "tiff"), default=None)
            sub.add_argument("--compression", default="tiff_lzw")

    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "inspect":
        report = inspect_image(Path(args.input), args.journal, args.figure_type, args.width_class, args.width_mm)
    else:
        report = export_image(args)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

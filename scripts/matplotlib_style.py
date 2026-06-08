#!/usr/bin/env python3
"""Matplotlib rcParams presets for journal-ready scientific figures."""

from __future__ import annotations

import argparse
import json
from typing import Any


FIGSIZE_INCHES: dict[tuple[str, str], tuple[float, float]] = {
    ("APS", "1-column"): (3.375, 3),
    ("APS", "1.5-column"): (5.0625, 3),
    ("APS", "2-column"): (5.35, 2.5),
    ("APS", "2-rows"): (3, 5.35),
    ("HHL", "1-column"): (4.4, 3.3),
    ("HHL", "3-column"): (7, 7 * 9 / 8),
    ("Nature", "1-column"): (3.50394, 3),
    ("Nature", "1.5-column"): (5.35, 3),
    ("Nature", "2-column"): (7.204724, 3),
}


def load_style(style: str = "HHL", width: str = "1-column", output_format: str = "pdf") -> dict[str, Any]:
    """Reset and apply journal-style Matplotlib parameters.

    Call this before creating figures:

        import matplotlib.pyplot as plt
        from matplotlib_style import load_style
        load_style("Nature", "1-column", "pdf")
        ...
        plt.savefig("figure.pdf")

    Use output_format="eps" or "pdf" for vector-friendly line art. Use
    output_format="tiff" for raster journal submission exports.
    """

    import matplotlib as mpl

    style = normalize_style(style)
    output_format = normalize_output_format(output_format)
    key = (style, width)
    if key not in FIGSIZE_INCHES:
        valid = ", ".join(f"{preset_style}/{preset_width}" for preset_style, preset_width in sorted(FIGSIZE_INCHES))
        raise ValueError(f"Unsupported style/width '{style}/{width}'. Valid pairs: {valid}")

    mpl.rcParams.update(mpl.rcParamsDefault)

    params: dict[str, Any] = {
        "text.usetex": True,
        "text.latex.preamble": r"\usepackage{braket}\usepackage{amssymb}\usepackage{txfonts}",
        "font.family": ["Times New Roman", "Times", "serif"],
        "figure.dpi": 150,
        "figure.figsize": FIGSIZE_INCHES[key],
        "figure.subplot.wspace": 0.08,
        "figure.subplot.hspace": 0.08,
        "figure.autolayout": False,
        "axes.autolimit_mode": "data",
        "axes.linewidth": 0.8,
        "axes.labelsize": "large",
        "lines.linewidth": 1,
        "lines.markerfacecolor": "none",
        "lines.markeredgewidth": 0.8,
        "lines.markersize": 5,
        "xtick.direction": "in",
        "xtick.major.size": 3,
        "xtick.minor.size": 1.75,
        "ytick.direction": "in",
        "ytick.minor.size": 1.75,
        "ytick.major.size": 3,
        "xtick.top": True,
        "ytick.right": True,
        "xtick.minor.visible": True,
        "ytick.minor.visible": True,
        "legend.fontsize": "small",
        "legend.labelspacing": 0.4,
        "legend.handlelength": 1.8,
        "legend.handletextpad": 0.5,
        "legend.borderaxespad": 0.5,
        "legend.columnspacing": 1.0,
        "legend.frameon": False,
        "savefig.transparent": False,
        "savefig.bbox": "tight",
        "savefig.dpi": 600,
        "savefig.format": output_format,
    }

    mpl.rcParams.update(params)
    return params


def save_figure(fig: Any, path: str, output_format: str | None = None, **kwargs: Any) -> None:
    """Save a Matplotlib figure as EPS, PDF, or TIFF with journal defaults."""

    output_format = normalize_output_format(output_format or path.rsplit(".", 1)[-1])
    save_kwargs: dict[str, Any] = {
        "format": output_format,
        "dpi": 600,
        "bbox_inches": "tight",
    }
    save_kwargs.update(kwargs)
    fig.savefig(path, **save_kwargs)


def normalize_style(style: str) -> str:
    aliases = {
        "aps": "APS",
        "nature": "Nature",
        "hhl": "HHL",
    }
    key = style.strip().lower()
    if key not in aliases:
        raise ValueError("style must be 'APS', 'Nature', or 'HHL'")
    return aliases[key]


def normalize_output_format(output_format: str) -> str:
    aliases = {
        "eps": "eps",
        "pdf": "pdf",
        "tif": "tiff",
        "tiff": "tiff",
    }
    key = output_format.strip().lower()
    if key not in aliases:
        raise ValueError("output_format must be 'eps', 'pdf', or 'tiff'")
    return aliases[key]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Print Matplotlib journal-style rcParams as JSON.")
    parser.add_argument("--style", default="HHL", choices=("APS", "Nature", "HHL"))
    parser.add_argument("--width", default="1-column", choices=sorted({width for _, width in FIGSIZE_INCHES}))
    parser.add_argument("--format", default="pdf", choices=("eps", "pdf", "tif", "tiff"), dest="output_format")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    params = load_style(args.style, args.width, args.output_format)
    printable = {key: value for key, value in params.items() if key != "text.latex.preamble"}
    printable["text.latex.preamble"] = params["text.latex.preamble"]
    print(json.dumps(printable, indent=2))


if __name__ == "__main__":
    main()

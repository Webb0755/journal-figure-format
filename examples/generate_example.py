#!/usr/bin/env python3
"""Generate a deterministic scientific figure used by the README example."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH = 2400
HEIGHT = 1440
MARGIN_LEFT = 260
MARGIN_RIGHT = 120
MARGIN_TOP = 120
MARGIN_BOTTOM = 220


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    names = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
        if bold
        else "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def main() -> None:
    output = Path(__file__).resolve().parent / "nature_combo_source.png"
    image = Image.new("RGB", (WIDTH, HEIGHT), "white")
    draw = ImageDraw.Draw(image)

    plot_left = MARGIN_LEFT
    plot_top = MARGIN_TOP
    plot_right = WIDTH - MARGIN_RIGHT
    plot_bottom = HEIGHT - MARGIN_BOTTOM

    axis = (30, 30, 30)
    grid = (218, 222, 226)
    blue = (37, 99, 166)
    red = (197, 64, 54)

    def x_pixel(value: float) -> float:
        return plot_left + value / 10 * (plot_right - plot_left)

    def y_pixel(value: float) -> float:
        y_min, y_max = -1.35, 1.35
        return plot_bottom - (value - y_min) / (y_max - y_min) * (
            plot_bottom - plot_top
        )

    for tick in range(0, 11, 2):
        x = x_pixel(tick)
        draw.line((x, plot_top, x, plot_bottom), fill=grid, width=2)
        label = str(tick)
        box = draw.textbbox((0, 0), label, font=font(42))
        draw.text(
            (x - (box[2] - box[0]) / 2, plot_bottom + 32),
            label,
            fill=axis,
            font=font(42),
        )

    for tick in (-1.0, -0.5, 0.0, 0.5, 1.0):
        y = y_pixel(tick)
        draw.line((plot_left, y, plot_right, y), fill=grid, width=2)
        label = f"{tick:.1f}"
        box = draw.textbbox((0, 0), label, font=font(42))
        draw.text(
            (plot_left - (box[2] - box[0]) - 30, y - 24),
            label,
            fill=axis,
            font=font(42),
        )

    draw.rectangle(
        (plot_left, plot_top, plot_right, plot_bottom),
        outline=axis,
        width=4,
    )

    points_a = []
    points_b = []
    for index in range(601):
        x = index / 60
        response_a = math.sin(1.55 * x) * math.exp(-0.055 * x)
        response_b = 0.72 * math.cos(1.55 * x + 0.35) * math.exp(-0.045 * x)
        points_a.append((x_pixel(x), y_pixel(response_a)))
        points_b.append((x_pixel(x), y_pixel(response_b)))

    draw.line(points_a, fill=blue, width=9, joint="curve")
    draw.line(points_b, fill=red, width=9, joint="curve")

    draw.text(
        (plot_left, 28),
        "Damped oscillatory response",
        fill=axis,
        font=font(58, bold=True),
    )

    x_label = "Time (s)"
    box = draw.textbbox((0, 0), x_label, font=font(48))
    draw.text(
        ((WIDTH - (box[2] - box[0])) / 2, HEIGHT - 112),
        x_label,
        fill=axis,
        font=font(48),
    )

    y_label = Image.new("RGBA", (460, 80), (255, 255, 255, 0))
    y_draw = ImageDraw.Draw(y_label)
    y_draw.text((0, 5), "Normalized response", fill=axis, font=font(48))
    y_label = y_label.rotate(90, expand=True)
    image.paste(y_label, (54, 430), y_label)

    legend_x = plot_right - 560
    legend_y = plot_top + 55
    draw.rounded_rectangle(
        (legend_x, legend_y, plot_right - 40, legend_y + 165),
        radius=12,
        fill="white",
        outline=(110, 110, 110),
        width=2,
    )
    draw.line((legend_x + 40, legend_y + 52, legend_x + 170, legend_y + 52), fill=blue, width=9)
    draw.text((legend_x + 205, legend_y + 24), "Probe A", fill=axis, font=font(40))
    draw.line((legend_x + 40, legend_y + 116, legend_x + 170, legend_y + 116), fill=red, width=9)
    draw.text((legend_x + 205, legend_y + 88), "Probe B", fill=axis, font=font(40))

    image.save(output, dpi=(600, 600))
    print(output)


if __name__ == "__main__":
    main()

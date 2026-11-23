from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
FONT_REGULAR = Path("C:/Windows/Fonts/arial.ttf")
FONT_BOLD = Path("C:/Windows/Fonts/arialbd.ttf")

BG_TOP = (3, 21, 31)
BG_BOTTOM = (7, 39, 47)
TEAL = (20, 157, 145)
TEAL_LIGHT = (80, 220, 205)
WHITE = (255, 255, 255)
TEXT = (224, 235, 238)
MUTED = (167, 194, 200)
AMBER = (250, 166, 27)


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size=size)


def gradient(size: tuple[int, int]) -> Image.Image:
    width, height = size
    image = Image.new("RGB", size, BG_TOP)
    draw = ImageDraw.Draw(image)
    for y in range(height):
        ratio = y / max(height - 1, 1)
        color = tuple(
            round(start + (end - start) * ratio)
            for start, end in zip(BG_TOP, BG_BOTTOM, strict=True)
        )
        draw.line((0, y, width, y), fill=color)
    return image


def shield(
    draw: ImageDraw.ImageDraw,
    *,
    center: tuple[int, int],
    radius: int,
    stroke: int,
) -> None:
    cx, cy = center
    draw.ellipse(
        (cx - radius, cy - radius, cx + radius, cy + radius),
        fill=(9, 38, 47),
        outline=TEAL_LIGHT,
        width=stroke,
    )
    top = cy - radius * 0.62
    bottom = cy + radius * 0.68
    left = cx - radius * 0.45
    right = cx + radius * 0.45
    shoulder = cy + radius * 0.22
    points = [
        (cx, top - radius * 0.12),
        (right, cy - radius * 0.42),
        (right, shoulder),
        (cx, bottom + radius * 0.08),
        (left, shoulder),
        (left, cy - radius * 0.42),
    ]
    draw.polygon(points, fill=(11, 58, 65), outline=TEAL_LIGHT, width=stroke)
    check_width = max(stroke + 2, round(radius * 0.12))
    draw.line(
        (
            cx - radius * 0.25,
            cy + radius * 0.08,
            cx - radius * 0.04,
            cy + radius * 0.31,
            cx + radius * 0.35,
            cy - radius * 0.30,
        ),
        fill=AMBER,
        width=check_width,
        joint="curve",
    )


def render_cover() -> Path:
    scale = 2
    size = (1280 * scale, 720 * scale)
    image = gradient(size).convert("RGBA")
    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    draw.ellipse(
        (850 * scale, -260 * scale, 1360 * scale, 260 * scale),
        fill=(16, 92, 98, 170),
    )
    draw.ellipse(
        (-170 * scale, 530 * scale, 300 * scale, 990 * scale),
        fill=(12, 76, 83, 160),
    )
    draw.rounded_rectangle(
        (72 * scale, 72 * scale, 1208 * scale, 648 * scale),
        radius=28 * scale,
        outline=(80, 111, 122, 210),
        width=2 * scale,
    )

    draw.text(
        (105 * scale, 94 * scale),
        "ESG · HOSTED API",
        font=font(FONT_BOLD, 23 * scale),
        fill=TEAL_LIGHT,
    )
    title_font = font(FONT_BOLD, 65 * scale)
    draw.text(
        (99 * scale, 168 * scale),
        "ESG Commitment Audit",
        font=title_font,
        fill=WHITE,
    )
    subtitle_font = font(FONT_REGULAR, 32 * scale)
    draw.text(
        (99 * scale, 257 * scale),
        "Evidence-first ESG & climate",
        font=subtitle_font,
        fill=TEXT,
    )
    draw.text(
        (99 * scale, 298 * scale),
        "commitment structure audits",
        font=subtitle_font,
        fill=TEXT,
    )

    bullet_font = font(FONT_REGULAR, 24 * scale)
    for index, label in enumerate(
        (
            "Structured extraction",
            "CRV evidence",
            "Tenant-scoped JSON",
        )
    ):
        y = (398 + 50 * index) * scale
        draw.ellipse(
            (99 * scale, y, 112 * scale, y + 13 * scale),
            fill=AMBER,
        )
        draw.text((132 * scale, y - 5 * scale), label, font=bullet_font, fill=TEXT)

    draw.rounded_rectangle(
        (99 * scale, 551 * scale, 642 * scale, 612 * scale),
        radius=16 * scale,
        fill=(15, 144, 131, 255),
    )
    draw.text(
        (124 * scale, 565 * scale),
        "Founding Small Team · $29/month",
        font=font(FONT_BOLD, 23 * scale),
        fill=WHITE,
    )
    shield(
        draw,
        center=(1010 * scale, 300 * scale),
        radius=112 * scale,
        stroke=5 * scale,
    )

    image = Image.alpha_composite(image, overlay).resize(
        (1280, 720),
        Image.Resampling.LANCZOS,
    )
    output = ASSETS / "esg-commitment-audit-cover.png"
    image.convert("RGB").save(output, format="PNG", optimize=True)
    return output


def render_thumbnail() -> Path:
    scale = 2
    size = (600 * scale, 600 * scale)
    image = gradient(size).convert("RGBA")
    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    draw.ellipse(
        (340 * scale, -170 * scale, 760 * scale, 250 * scale),
        fill=(16, 92, 98, 175),
    )
    draw.text(
        (42 * scale, 48 * scale),
        "ESG · HOSTED API",
        font=font(FONT_BOLD, 18 * scale),
        fill=TEAL_LIGHT,
    )

    title_font = font(FONT_BOLD, 54 * scale)
    draw.text((42 * scale, 120 * scale), "ESG", font=title_font, fill=WHITE)
    draw.text(
        (42 * scale, 178 * scale),
        "COMMITMENT",
        font=title_font,
        fill=WHITE,
    )
    draw.text((42 * scale, 236 * scale), "AUDIT", font=title_font, fill=WHITE)
    draw.text(
        (44 * scale, 302 * scale),
        "Evidence-first structure audits",
        font=font(FONT_REGULAR, 23 * scale),
        fill=TEXT,
    )
    shield(
        draw,
        center=(300 * scale, 430 * scale),
        radius=82 * scale,
        stroke=4 * scale,
    )
    draw.rounded_rectangle(
        (42 * scale, 535 * scale, 392 * scale, 580 * scale),
        radius=12 * scale,
        fill=(15, 144, 131, 255),
    )
    draw.text(
        (60 * scale, 549 * scale),
        "Founding Small Team · $29/month",
        font=font(FONT_BOLD, 17 * scale),
        fill=WHITE,
    )

    image = Image.alpha_composite(image, overlay).resize(
        (600, 600),
        Image.Resampling.LANCZOS,
    )
    output = ASSETS / "esg-commitment-audit-thumbnail.png"
    image.convert("RGB").save(output, format="PNG", optimize=True)
    return output


def main() -> int:
    ASSETS.mkdir(parents=True, exist_ok=True)
    for output in (render_cover(), render_thumbnail()):
        with Image.open(output) as image:
            print(
                f"{output.name}: {image.width}x{image.height}, "
                f"{output.stat().st_size} bytes"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

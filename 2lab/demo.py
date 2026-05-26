from __future__ import annotations

from itertools import chain
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

from polygon_api import (  # noqa: E402
    agr_area,
    agr_max_side,
    agr_min_area,
    agr_origin_nearest,
    agr_perimeter,
    flt_intersects_any,
    flt_short_side,
    flt_square,
    gen_hexagon,
    gen_rectangle,
    gen_triangle,
    plot_polygons,
    polygon,
    take,
    tr_homothety,
    tr_rotate,
    tr_symmetry,
    tr_translate,
    zip_polygons,
)

OUT = Path("examples/out")


def quads_between_rays(n: int = 15):
    """Quadrilaterals between two rays y=0.35x and y=1.1x."""

    def one(i: int):
        x1 = 0.7 + i * 0.45
        x2 = x1 + 0.3
        return polygon(((x1, 0.35 * x1), (x2, 0.35 * x2), (x2, 1.1 * x2), (x1, 1.1 * x1)))

    return map(one, range(n))


def save_base_sequences() -> None:
    rectangles = take(7, gen_rectangle(width=1.2, height=0.8, start=(0, 0)))
    triangles = take(7, gen_triangle(side=1.1, start=(0, 1.8)))
    hexagons = take(7, gen_hexagon(radius=0.45, start=(0, 3.5)))
    plot_polygons(
        chain(rectangles, triangles, hexagons),
        title="Seven non-overlapping rectangles, triangles and hexagons",
        save_path=OUT / "01_base_sequences.png",
    )


def save_transformations() -> None:
    # 1. Three parallel bands at an acute angle.
    bands = chain.from_iterable(
        map(
            lambda y: take(8, map(tr_rotate(22), gen_rectangle(width=0.8, height=0.35, gap=0.25, start=(0, y)))),
            (0.0, 0.8, 1.6),
        )
    )
    plot_polygons(bands, title="Three parallel bands", save_path=OUT / "02_parallel_bands.png")

    # 2. Two crossing bands; intersection is shifted away from the origin.
    band_a = take(9, map(tr_translate(2.0, 0.8), map(tr_rotate(28), gen_rectangle(width=0.8, height=0.35, gap=0.18))))
    band_b = take(9, map(tr_translate(1.0, 2.4), map(tr_rotate(-28), gen_rectangle(width=0.8, height=0.35, gap=0.18))))
    plot_polygons(chain(band_a, band_b), title="Crossing bands away from origin", save_path=OUT / "03_crossing_bands.png")

    # 3. Two parallel triangle bands symmetric around the x-axis.
    top = take(8, map(tr_translate(0.0, 1.1), gen_triangle(side=0.8, gap=0.25)))
    bottom = tuple(map(tr_symmetry("x"), top))
    plot_polygons(chain(top, bottom), title="Symmetric triangle bands", save_path=OUT / "04_symmetric_triangles.png")

    # 4. Quadrilaterals of different scale between two lines through the origin.
    plot_polygons(quads_between_rays(12), title="Scaled quadrilaterals between rays", save_path=OUT / "05_quads_between_rays.png")


def save_filter_scenarios() -> None:
    # Scenario 1: from p.4 figures, keep exactly six by area.
    filtered_six = tuple(filter(flt_square(0.7), quads_between_rays(15)))
    plot_polygons(filtered_six, title="Filter scenario 1: exactly six polygons", save_path=OUT / "06_filter_exactly_six.png")

    # Scenario 2: from >=15 scaled figures, select <=4 with a short side under threshold.
    base = polygon(((0, 0), (1, 0), (1, 1), (0, 1)))
    scaled = map(lambda k: tr_translate(k * 1.8, 0)(tr_homothety(0.2 + k * 0.08)(base)), range(15))
    small_short_side = tuple(filter(flt_short_side(0.5), scaled))
    plot_polygons(small_short_side, title="Filter scenario 2: short side < 0.5", save_path=OUT / "07_filter_short_side.png")

    # Scenario 3: from >=15 figures, keep polygons intersecting a reference polygon.
    reference = polygon(((3.2, -0.3), (5.0, -0.3), (5.0, 1.0), (3.2, 1.0)))
    candidates = take(15, gen_rectangle(width=0.7, height=0.7, gap=0.15))
    intersecting = tuple(filter(flt_intersects_any((reference,)), candidates))
    plot_polygons(chain((reference,), intersecting), title="Filter scenario 3: intersecting polygons", save_path=OUT / "08_filter_intersections.png")


def save_zip_demo() -> None:
    upper = take(5, gen_triangle(side=0.8, start=(0, 0.7)))
    lower = tuple(map(tr_symmetry("x"), upper))
    glued = tuple(zip_polygons(upper, lower))
    plot_polygons(glued, title="zip_polygons demo", save_path=OUT / "09_zip_polygons.png")


def print_aggregates() -> None:
    polys = take(5, gen_rectangle(width=1.0, height=2.0, gap=0.5))
    print("Nearest vertex to origin:", agr_origin_nearest(polys))
    print("Longest side:", agr_max_side(polys))
    print("Minimal area:", agr_min_area(polys))
    print("Total perimeter:", agr_perimeter(polys))
    print("Total area:", agr_area(polys))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    save_base_sequences()
    save_transformations()
    save_filter_scenarios()
    save_zip_demo()
    print_aggregates()
    print(f"Images saved to {OUT.resolve()}")


if __name__ == "__main__":
    main()

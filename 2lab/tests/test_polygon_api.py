from __future__ import annotations

from itertools import chain
from math import sqrt

import pytest

from polygon_api import (
    agr_area,
    agr_max_side,
    agr_min_area,
    agr_origin_nearest,
    agr_perimeter,
    area,
    count_2D,
    flt_angle_point,
    flt_convex_polygon,
    flt_point_inside,
    flt_polygon_angles_inside,
    flt_short_side,
    flt_square,
    gen_hexagon,
    gen_rectangle,
    gen_triangle,
    perimeter,
    polygon,
    polygon_intersects,
    take,
    tr_homothety,
    tr_rotate,
    tr_symmetry,
    tr_translate,
    zip_polygons,
    zip_tuple,
)


def test_generators_return_infinite_non_overlapping_polygons() -> None:
    rectangles = take(7, gen_rectangle(width=1, height=1, gap=0.5))
    triangles = take(7, gen_triangle(side=1, gap=0.5))
    hexagons = take(7, gen_hexagon(radius=0.5, gap=0.5))

    assert len(rectangles) == len(triangles) == len(hexagons) == 7
    assert all(
        isinstance(
            poly,
            tuple) for poly in chain(
            rectangles,
            triangles,
            hexagons))
    assert all(not polygon_intersects(a, b)
               for a, b in zip(rectangles, rectangles[1:]))


@pytest.mark.parametrize(
    "poly, expected_area, expected_perimeter",
    [
        (polygon(((0, 0), (2, 0), (2, 1), (0, 1))), 2.0, 6.0),
        (polygon(((0, 0), (1, 0), (0, 1))), 0.5, 2.0 + sqrt(2)),
    ],
)
def test_area_and_perimeter(poly, expected_area, expected_perimeter) -> None:
    assert area(poly) == pytest.approx(expected_area)
    assert perimeter(poly) == pytest.approx(expected_perimeter)


def test_transformations_are_usable_with_map() -> None:
    square = polygon(((0, 0), (1, 0), (1, 1), (0, 1)))

    moved = tr_translate(2, 3)(square)
    assert moved == ((2.0, 3.0), (3.0, 3.0), (3.0, 4.0), (2.0, 4.0))

    rotated = tr_rotate(90)(polygon(((1, 0), (2, 0), (2, 1))))
    assert rotated[0] == pytest.approx((0.0, 1.0))

    reflected = tr_symmetry("x")(polygon(((1, 2), (2, 2), (1, 3))))
    assert reflected == ((1.0, -2.0), (2.0, -2.0), (1.0, -3.0))

    scaled = tr_homothety(2)(square)
    assert area(scaled) == pytest.approx(4.0)

    result = tuple(map(tr_translate(1, 0), (square, square)))
    assert len(result) == 2
    assert result[0][0] == (1.0, 0.0)


def test_all_six_filters_are_usable_with_filter() -> None:
    square = polygon(((0, 0), (2, 0), (2, 2), (0, 2)))
    small_triangle = polygon(((0, 0), (0.4, 0), (0, 0.4)))
    concave = polygon(((0, 0), (2, 0), (1, 0.2), (2, 2), (0, 2)))
    outer = polygon(((-1, -1), (3, -1), (3, 3), (-1, 3)))

    assert tuple(filter(flt_convex_polygon, (square, concave))) == (square,)
    assert tuple(
        filter(
            flt_angle_point(
                (0, 0)), (square, small_triangle))) == (
        square, small_triangle)
    assert tuple(
        filter(
            flt_square(1), (square, small_triangle))) == (
        small_triangle,)
    assert tuple(
        filter(
            flt_short_side(0.5),
            (square,
             small_triangle))) == (
        small_triangle,
    )
    assert tuple(
        filter(
            flt_point_inside(
                (1, 1)), (square, small_triangle))) == (
        square,)
    assert tuple(
        filter(
            flt_polygon_angles_inside(small_triangle),
            (square,
             outer))) == (
        square,
        outer)


def test_decorators_filter_and_transform_iterator_arguments() -> None:
    square = polygon(((0, 0), (1, 0), (1, 1), (0, 1)))
    concave = polygon(((0, 0), (2, 0), (1, 0.2), (2, 2), (0, 2)))

    @flt_convex_polygon
    def collect(polygons):
        return tuple(polygons)

    @flt_square(1.1)
    def collect_small(polygons):
        return tuple(polygons)

    @tr_translate(10, 0)
    def collect_moved(polygons):
        return tuple(polygons)

    assert collect((square, concave)) == (square,)
    assert collect_small((square, concave)) == (square,)
    assert collect_moved((square,))[0][0] == (10.0, 0.0)


def test_aggregators_are_reduce_based_results() -> None:
    p1 = polygon(((0, 0), (2, 0), (2, 1), (0, 1)))
    p2 = polygon(((10, 0), (13, 0), (13, 1), (10, 1)))
    polys = (p1, p2)

    assert agr_origin_nearest(polys) == (0.0, 0.0)
    assert agr_max_side(polys)[2] == pytest.approx(3.0)
    assert agr_min_area(polys) == pytest.approx(2.0)
    assert agr_perimeter(polys) == pytest.approx(6.0 + 8.0)
    assert agr_area(polys) == pytest.approx(2.0 + 3.0)


def test_zip_polygons_matches_assignment_example() -> None:
    first = [((1, 1), (2, 2), (3, 1)), ((11, 11), (12, 12), (13, 11))]
    second = [((1, -1), (2, -2), (3, -1)), ((11, -11), (12, -12), (13, -11))]

    assert list(zip_polygons(first, second)) == [
        ((1, 1), (2, 2), (3, 1), (1, -1), (2, -2), (3, -1)),
        ((11, 11), (12, 12), (13, 11), (11, -11), (12, -12), (13, -11)),
    ]


def test_extra_utilities() -> None:
    assert take(3, count_2D(start=(1, 2), step=(2, -1))
                ) == ((1, 2), (3, 1), (5, 0))
    assert zip_tuple((1, 2), (3,), (4, 5)) == (1, 2, 3, 4, 5)

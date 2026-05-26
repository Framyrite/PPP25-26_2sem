"""Functional API for generation, transformation and analysis of 2D polygons.

The project intentionally keeps polygons immutable:
    Polygon = tuple[tuple[float, float], ...]

Sequences of polygons are treated as iterators and are processed with map(),
filter(), functools.reduce() and itertools utilities.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from functools import reduce, wraps
from itertools import chain, count, islice, pairwise, tee
from math import cos, hypot, pi, radians, sin, sqrt
from numbers import Real
from typing import Any, Literal, TypeAlias

Point: TypeAlias = tuple[float, float]
Polygon: TypeAlias = tuple[Point, ...]
EPS = 1e-9


# ---------------------------------------------------------------------------
# Normalization and geometry helpers
# ---------------------------------------------------------------------------


def point(x: Real, y: Real) -> Point:
    """Return a normalized point tuple."""

    return (float(x), float(y))


def polygon(points: Iterable[tuple[Real, Real]]) -> Polygon:
    """Return a normalized polygon represented as a tuple of point tuples."""

    return tuple(point(x, y) for x, y in points)


def _is_point(value: Any) -> bool:
    return (
        isinstance(value, (tuple, list))
        and len(value) == 2
        and isinstance(value[0], Real)
        and isinstance(value[1], Real)
    )


def _is_polygon(value: Any) -> bool:
    return isinstance(value, (tuple, list)) and len(value) >= 3 and all(
        _is_point(item) for item in value
    )


def _is_polygon_iterator_arg(value: Any) -> bool:
    if isinstance(value, (str, bytes, dict)):
        return False
    if _is_polygon(value):
        return False
    return isinstance(value, Iterable)


def _close(a: Point, b: Point, eps: float = EPS) -> bool:
    return hypot(a[0] - b[0], a[1] - b[1]) <= eps


def _cyclic_pairs(poly: Polygon) -> Iterator[tuple[Point, Point]]:
    """Iterate over polygon edges, including the last-first edge."""

    return pairwise(chain(poly, poly[:1]))


def distance(a: Point, b: Point = (0.0, 0.0)) -> float:
    return hypot(a[0] - b[0], a[1] - b[1])


def side_lengths(poly: Polygon) -> tuple[float, ...]:
    return tuple(map(lambda edge: distance(
        edge[0], edge[1]), _cyclic_pairs(poly)))


def perimeter(poly: Polygon) -> float:
    return sum(side_lengths(poly))


def area(poly: Polygon) -> float:
    """Return polygon area by the shoelace formula."""

    twice_area = reduce(
        lambda acc,
        edge: acc +
        edge[0][0] *
        edge[1][1] -
        edge[1][0] *
        edge[0][1],
        _cyclic_pairs(poly),
        0.0,
    )
    return abs(twice_area) / 2.0


def signed_area(poly: Polygon) -> float:
    twice_area = reduce(
        lambda acc,
        edge: acc +
        edge[0][0] *
        edge[1][1] -
        edge[1][0] *
        edge[0][1],
        _cyclic_pairs(poly),
        0.0,
    )
    return twice_area / 2.0


def _cross(o: Point, a: Point, b: Point) -> float:
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def _orientation(a: Point, b: Point, c: Point) -> float:
    return _cross(a, b, c)


def _on_segment(a: Point, b: Point, p: Point, eps: float = EPS) -> bool:
    return (
        abs(_orientation(a, b, p)) <= eps
        and min(a[0], b[0]) - eps <= p[0] <= max(a[0], b[0]) + eps
        and min(a[1], b[1]) - eps <= p[1] <= max(a[1], b[1]) + eps
    )


def _segments_intersect(
    a: Point,
    b: Point,
    c: Point,
    d: Point,
        eps: float = EPS) -> bool:
    o1 = _orientation(a, b, c)
    o2 = _orientation(a, b, d)
    o3 = _orientation(c, d, a)
    o4 = _orientation(c, d, b)

    if o1 * o2 < -eps and o3 * o4 < -eps:
        return True

    return any(
        (
            _on_segment(a, b, c, eps),
            _on_segment(a, b, d, eps),
            _on_segment(c, d, a, eps),
            _on_segment(c, d, b, eps),
        )
    )


def polygon_intersects(poly1: Polygon, poly2: Polygon) -> bool:
    """Return True if polygons intersect or contain each other."""

    edge_crossing = any(
        _segments_intersect(a, b, c, d)
        for a, b in _cyclic_pairs(poly1)
        for c, d in _cyclic_pairs(poly2)
    )
    if edge_crossing:
        return True

    return point_in_convex_polygon(
        poly1[0], poly2) or point_in_convex_polygon(
        poly2[0], poly1)


def point_in_convex_polygon(p: Point, poly: Polygon, eps: float = EPS) -> bool:
    """Return True if point is inside or on the polygon boundary."""

    if not is_convex_polygon(poly):
        return False

    signs = tuple(
        0 if abs(cross) <= eps else (
            1 if cross > 0 else -
            1) for cross in map(
            lambda edge: _cross(
                edge[0],
                edge[1],
                p),
            _cyclic_pairs(poly)))
    non_zero = tuple(filter(lambda sign: sign != 0, signs))
    return not non_zero or all(map(lambda sign: sign == non_zero[0], non_zero))


def is_convex_polygon(poly: Polygon, eps: float = EPS) -> bool:
    if not _is_polygon(poly) or len(poly) < 3 or area(poly) <= eps:
        return False

    triples = zip(poly, chain(poly[1:], poly[:1]), chain(poly[2:], poly[:2]))
    signs = tuple(
        0 if abs(cross) <= eps else (1 if cross > 0 else -1)
        for cross in map(lambda t: _cross(t[0], t[1], t[2]), triples)
    )
    non_zero = tuple(filter(lambda sign: sign != 0, signs))
    return bool(non_zero) and all(
        map(lambda sign: sign == non_zero[0], non_zero))


# ---------------------------------------------------------------------------
# Infinite generators
# ---------------------------------------------------------------------------


def gen_rectangle(
    width: float = 1.0,
    height: float = 1.0,
    gap: float = 0.3,
    start: Point = (0.0, 0.0),
) -> Iterator[Polygon]:
    """Generate an infinite sequence of non-overlapping rectangles."""

    sx, sy = start
    step = width + gap
    return map(
        lambda i: polygon(
            (
                (sx + i * step, sy),
                (sx + i * step + width, sy),
                (sx + i * step + width, sy + height),
                (sx + i * step, sy + height),
            )
        ),
        count(),
    )


def gen_triangle(
    side: float = 1.0,
    gap: float = 0.3,
    start: Point = (0.0, 0.0),
) -> Iterator[Polygon]:
    """Generate infinite non-overlapping equilateral triangles."""

    sx, sy = start
    height = side * sqrt(3.0) / 2.0
    step = side + gap
    return map(
        lambda i: polygon(
            (
                (sx + i * step, sy),
                (sx + i * step + side, sy),
                (sx + i * step + side / 2.0, sy + height),
            )
        ),
        count(),
    )


def gen_hexagon(
    radius: float = 0.5,
    gap: float = 0.3,
    start: Point = (0.0, 0.0),
) -> Iterator[Polygon]:
    """Generate an infinite sequence of non-overlapping regular hexagons."""

    sx, sy = start
    step = 2.0 * radius + gap
    angles = tuple(map(lambda k: pi / 6.0 + k * pi / 3.0, range(6)))
    return map(
        lambda i: polygon(
            map(
                lambda angle: (
                    sx + radius + i * step + radius * cos(angle),
                    sy + radius + radius * sin(angle),
                ),
                angles,
            )
        ),
        count(),
    )


# ---------------------------------------------------------------------------
# Decorator infrastructure
# ---------------------------------------------------------------------------


def _decorate_iterable_args(
    func: Callable[..., Any],
    operation: Callable[[Iterable[Polygon]], Iterable[Polygon]],
) -> Callable[..., Any]:
    """Apply operation to every polygon iterator among function arguments."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        new_args = tuple(map(lambda arg: operation(
            arg) if _is_polygon_iterator_arg(arg) else arg, args))
        new_kwargs = {
            key: operation(value) if _is_polygon_iterator_arg(value) else value
            for key, value in kwargs.items()
        }
        return func(*new_args, **new_kwargs)

    return wrapper


@dataclass(frozen=True)
class PredicateDecorator:
    predicate: Callable[[Polygon], bool]

    def __call__(self, target: Any) -> Any:
        if callable(target) and not _is_polygon(target):
            return _decorate_iterable_args(
                target, lambda iterator: filter(
                    self.predicate, iterator))
        return self.predicate(polygon(target))


@dataclass(frozen=True)
class TransformDecorator:
    transform: Callable[[Polygon], Polygon]

    def __call__(self, target: Any) -> Any:
        if callable(target) and not _is_polygon(target):
            return _decorate_iterable_args(
                target, lambda iterator: map(
                    self.transform, iterator))
        return self.transform(polygon(target))


# ---------------------------------------------------------------------------
# Transformations. Each function returns an object that works both as:
#   map(tr_translate(...), polygons)
#   @tr_translate(...)
# ---------------------------------------------------------------------------


def tr_translate(dx: float = 0.0, dy: float = 0.0) -> TransformDecorator:
    return TransformDecorator(lambda poly: tuple(
        map(lambda p: (p[0] + dx, p[1] + dy), poly)))


def tr_rotate(
    angle: float,
    origin: Point = (0.0, 0.0),
    degrees: bool = True,
) -> TransformDecorator:
    theta = radians(angle) if degrees else angle
    cos_t, sin_t = cos(theta), sin(theta)
    ox, oy = origin

    def rotate(poly: Polygon) -> Polygon:
        def rotate_point(p: Point) -> Point:
            x, y = p[0] - ox, p[1] - oy
            return (ox + x * cos_t - y * sin_t, oy + x * sin_t + y * cos_t)

        return tuple(map(rotate_point, poly))

    return TransformDecorator(rotate)


def tr_symmetry(
    axis: Literal["x", "y", "origin"] | float | tuple[Point, Point] = "x",
) -> TransformDecorator:
    """Reflect polygons against x/y/origin, angle, or line.

    axis="x"      -> (x, y) -> (x, -y)
    axis="y"      -> (x, y) -> (-x, y)
    axis="origin" -> (x, y) -> (-x, -y)
    axis=angle    -> reflection over a line through origin at angle degrees
    axis=((x1,y1),(x2,y2)) -> reflection over an arbitrary line
    """

    def reflect_x(poly: Polygon) -> Polygon:
        return tuple(map(lambda p: (p[0], -p[1]), poly))

    def reflect_y(poly: Polygon) -> Polygon:
        return tuple(map(lambda p: (-p[0], p[1]), poly))

    def reflect_origin(poly: Polygon) -> Polygon:
        return tuple(map(lambda p: (-p[0], -p[1]), poly))

    def reflect_line_by_angle(
            angle_degrees: float) -> Callable[[Polygon], Polygon]:
        theta = radians(angle_degrees)
        cos_2t, sin_2t = cos(2.0 * theta), sin(2.0 * theta)

        def reflect(poly: Polygon) -> Polygon:
            return tuple(
                map(
                    lambda p: (
                        p[0] * cos_2t + p[1] * sin_2t,
                        p[0] * sin_2t - p[1] * cos_2t,
                    ),
                    poly,
                )
            )

        return reflect

    def reflect_line_by_points(
            line: tuple[Point, Point]) -> Callable[[Polygon], Polygon]:
        (x1, y1), (x2, y2) = line
        dx, dy = x2 - x1, y2 - y1
        length_sq = dx * dx + dy * dy
        if length_sq <= EPS:
            raise ValueError(
                "Reflection line must be defined by two different points")

        def reflect(poly: Polygon) -> Polygon:
            def reflect_point(p: Point) -> Point:
                px, py = p[0] - x1, p[1] - y1
                projection = (px * dx + py * dy) / length_sq
                proj_x, proj_y = projection * dx, projection * dy
                perp_x, perp_y = px - proj_x, py - proj_y
                return (x1 + proj_x - perp_x, y1 + proj_y - perp_y)

            return tuple(map(reflect_point, poly))

        return reflect

    if axis == "x":
        return TransformDecorator(reflect_x)
    if axis == "y":
        return TransformDecorator(reflect_y)
    if axis == "origin":
        return TransformDecorator(reflect_origin)
    if isinstance(axis, Real):
        return TransformDecorator(reflect_line_by_angle(float(axis)))
    return TransformDecorator(reflect_line_by_points(axis))


def tr_homothety(k: float, center: Point = (0.0, 0.0)) -> TransformDecorator:
    cx, cy = center
    return TransformDecorator(lambda poly: tuple(
        map(lambda p: (cx + k * (p[0] - cx), cy + k * (p[1] - cy)), poly)))


# ---------------------------------------------------------------------------
# Filters. They work with filter() and as decorators for functions that accept
# polygon iterators.
# ---------------------------------------------------------------------------


def flt_convex_polygon(target: Any) -> Any:
    """Predicate/decorator: keep only convex polygons."""

    if callable(target) and not _is_polygon(target):
        return _decorate_iterable_args(
            target, lambda iterator: filter(
                is_convex_polygon, iterator))
    return is_convex_polygon(polygon(target))


def flt_angle_point(
        target_point: Point,
        eps: float = EPS) -> PredicateDecorator:
    return PredicateDecorator(lambda poly: any(
        map(lambda p: _close(p, target_point, eps), poly)))


def flt_square(max_area: float) -> PredicateDecorator:
    return PredicateDecorator(lambda poly: area(poly) < max_area)


def flt_short_side(max_length: float) -> PredicateDecorator:
    return PredicateDecorator(
        lambda poly: min(
            side_lengths(poly)) < max_length)


def flt_point_inside(target_point: Point) -> PredicateDecorator:
    return PredicateDecorator(
        lambda poly: point_in_convex_polygon(
            target_point, poly))


def flt_polygon_angles_inside(inner_polygon: Polygon) -> PredicateDecorator:
    inner = polygon(inner_polygon)
    return PredicateDecorator(lambda outer: is_convex_polygon(outer) and any(
        map(lambda p: point_in_convex_polygon(p, outer), inner)))


def flt_intersects_any(
    other_polygons: Iterable[Polygon],
) -> PredicateDecorator:
    """Keep polygons intersecting at least one polygon from collection."""

    others = tuple(map(polygon, other_polygons))
    return PredicateDecorator(lambda poly: any(
        map(lambda other: polygon_intersects(poly, other), others)))


# ---------------------------------------------------------------------------
# Aggregators implemented via functools.reduce
# ---------------------------------------------------------------------------


def agr_origin_nearest(polygons: Iterable[Polygon]) -> Point | None:
    """Return the vertex closest to the origin among all polygons."""

    return reduce(lambda best, p: p if best is None or distance(
        p) < distance(best) else best, chain.from_iterable(polygons), None, )


def agr_max_side(polygons: Iterable[Polygon]
                 ) -> tuple[Point, Point, float] | None:
    """Return the longest side as (point1, point2, length)."""

    edges = chain.from_iterable(map(_cyclic_pairs, polygons))
    return reduce(
        lambda best, edge: (edge[0], edge[1], distance(edge[0], edge[1]))
        if best is None or distance(edge[0], edge[1]) > best[2]
        else best,
        edges,
        None,
    )


def agr_min_area(polygons: Iterable[Polygon]) -> float | None:
    """Return the smallest polygon area in a sequence."""

    return reduce(lambda best, poly: area(poly) if best is None or area(
        poly) < best else best, polygons, None, )


def agr_perimeter(polygons: Iterable[Polygon]) -> float:
    """Return the total perimeter of all polygons."""

    return reduce(lambda acc, poly: acc + perimeter(poly), polygons, 0.0)


def agr_area(polygons: Iterable[Polygon]) -> float:
    """Return the total area of all polygons."""

    return reduce(lambda acc, poly: acc + area(poly), polygons, 0.0)


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------


def take(n: int, iterator: Iterable[Any]) -> tuple[Any, ...]:
    return tuple(islice(iterator, n))


def count_2D(
    start: Point = (
        0.0, 0.0), step: Point = (
            1.0, 0.0)) -> Iterator[Point]:
    """Generate an infinite arithmetic progression of 2D points."""

    sx, sy = start
    dx, dy = step
    return map(lambda i: (sx + i * dx, sy + i * dy), count())


def zip_tuple(*tuples: Iterable[Any]) -> tuple[Any, ...]:
    """Concatenate several tuple-like iterables into one tuple."""

    return tuple(chain.from_iterable(tuples))


def zip_polygons(*iterators: Iterable[Polygon]) -> Iterator[Polygon]:
    """Glue polygons from sequences by iterator position.

    The first polygons from all iterators are concatenated, then the second
    polygons, and so on. Iteration stops when the shortest input iterator ends.
    """

    return map(
        lambda polys: tuple(
            chain.from_iterable(polys)), zip(
            *iterators))


def duplicate_iterator(
        iterator: Iterable[Any], n: int = 2) -> tuple[Iterator[Any], ...]:
    """A small itertools-based helper useful in demos/tests."""

    return tee(iterator, n)

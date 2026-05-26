from __future__ import annotations
from polygon_api import (
    agr_area,
    agr_max_side,
    agr_min_area,
    agr_origin_nearest,
    agr_perimeter,
    flt_convex_polygon,
    flt_intersects_any,
    flt_point_inside,
    flt_polygon_angles_inside,
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

from functools import reduce
from itertools import chain, islice
from math import ceil

import matplotlib

matplotlib.use("Agg")


def ask_string(prompt: str, default: str | None = None) -> str:
    if default is None:
        value = input(f"{prompt}: ").strip()
    else:
        value = input(f"{prompt} [{default}]: ").strip()
    return value if value else str(default)


def ask_int(prompt: str, default: int) -> int:
    while True:
        value = input(f"{prompt} [{default}]: ").strip()
        if not value:
            return default
        try:
            return int(value)
        except ValueError:
            print("Некорректное число. Попробуйте ещё раз.")


def ask_float(prompt: str, default: float) -> float:
    while True:
        value = input(f"{prompt} [{default}]: ").strip().replace(",", ".")
        if not value:
            return default
        try:
            return float(value)
        except ValueError:
            print("Некорректное число. Попробуйте ещё раз.")


def ask_yes_no(prompt: str, default: bool = False) -> bool:
    default_text = "y" if default else "n"
    while True:
        value = input(
            f"{prompt} [y/n, default: {default_text}]: ").strip().lower()
        if not value:
            return default
        if value in ("y", "yes"):
            return True
        if value in ("n", "no"):
            return False
        print("Введите y или n.")


def ask_choice(prompt: str, choices: tuple[str, ...], default: str) -> str:
    print(f"\n{prompt}")
    for index, choice in enumerate(choices, start=1):
        print(f"{index}. {choice}")

    while True:
        value = input(f"Выберите вариант [{default}]: ").strip().lower()
        if not value:
            return default
        if value in choices:
            return value
        if value.isdigit():
            index = int(value)
            if 1 <= index <= len(choices):
                return choices[index - 1]
        print("Некорректный вариант. Попробуйте ещё раз.")


def apply_transforms(polygons, transforms):
    return reduce(
        lambda iterator, transform: map(transform, iterator),
        transforms,
        polygons,
    )


def apply_filters(polygons, filters):
    return reduce(
        lambda iterator, predicate: filter(predicate, iterator),
        filters,
        polygons,
    )


def quads_between_rays(
        count: int,
        slope_low: float,
        slope_high: float,
        start_x: float,
        step_x: float,
        width: float):
    def make_one(i: int):
        x1 = start_x + i * step_x
        x2 = x1 + width
        return polygon(
            (
                (x1, slope_low * x1),
                (x2, slope_low * x2),
                (x2, slope_high * x2),
                (x1, slope_high * x1),
            )
        )

    return map(make_one, range(count))


def make_reference_rectangle(x: float, y: float, width: float, height: float):
    return polygon(
        (
            (x, y),
            (x + width, y),
            (x + width, y + height),
            (x, y + height),
        )
    )


def ask_scenario_settings(candidate_count: int):
    scenarios = (
        "rectangle_line",
        "triangle_line",
        "hexagon_line",
        "mixed_base_sequences",
        "parallel_bands",
        "crossing_bands",
        "symmetric_triangles",
        "scaled_quads_between_rays",
        "zipped_triangles",
    )

    scenario = ask_choice(
        "Выберите сценарий генерации",
        scenarios,
        default="rectangle_line",
    )

    if scenario == "rectangle_line":
        print("\n=== Настройки rectangle_line ===")
        width = ask_float("Ширина rectangle", 2.0)
        height = ask_float("Высота rectangle", 1.0)
        gap = ask_float("Расстояние между фигурами", 0.5)
        start_x = ask_float("Начальная координата X", 0.0)
        start_y = ask_float("Начальная координата Y", 0.0)
        return scenario, islice(
            gen_rectangle(
                width=width, height=height, gap=gap, start=(
                    start_x, start_y)), candidate_count, )

    if scenario == "triangle_line":
        print("\n=== Настройки triangle_line ===")
        side = ask_float("Сторона triangle", 2.0)
        gap = ask_float("Расстояние между фигурами", 0.5)
        start_x = ask_float("Начальная координата X", 0.0)
        start_y = ask_float("Начальная координата Y", 0.0)
        return scenario, islice(
            gen_triangle(side=side, gap=gap, start=(start_x, start_y)),
            candidate_count,
        )

    if scenario == "hexagon_line":
        print("\n=== Настройки hexagon_line ===")
        radius = ask_float("Радиус hexagon", 1.0)
        gap = ask_float("Расстояние между фигурами", 0.5)
        start_x = ask_float("Начальная координата X", 0.0)
        start_y = ask_float("Начальная координата Y", 0.0)
        return scenario, islice(
            gen_hexagon(radius=radius, gap=gap, start=(start_x, start_y)),
            candidate_count,
        )

    if scenario == "mixed_base_sequences":
        print("\n=== Настройки mixed_base_sequences ===")
        print(
            "Будут сгенерированы rectangle, triangle и hexagon "
            "в трёх рядах."
        )
        per_type = max(1, ceil(candidate_count / 3))
        rectangle_y = ask_float("Y для ряда rectangle", 0.0)
        triangle_y = ask_float("Y для ряда triangle", 2.0)
        hexagon_y = ask_float("Y для ряда hexagon", 4.0)

        rectangles = take(
            per_type,
            gen_rectangle(
                width=1.2,
                height=0.8,
                gap=0.35,
                start=(
                    0.0,
                    rectangle_y)))
        triangles = take(
            per_type, gen_triangle(
                side=1.1, gap=0.35, start=(
                    0.0, triangle_y)))
        hexagons = take(
            per_type, gen_hexagon(
                radius=0.5, gap=0.35, start=(
                    0.0, hexagon_y)))
        return scenario, islice(
            chain(rectangles, triangles, hexagons), candidate_count)

    if scenario == "parallel_bands":
        print("\n=== Настройки parallel_bands ===")
        band_count = ask_int("Количество параллельных лент", 3)
        angle = ask_float("Угол наклона лент в градусах", 22.0)
        band_gap = ask_float("Расстояние между лентами по Y", 0.8)
        width = ask_float("Ширина rectangle", 0.8)
        height = ask_float("Высота rectangle", 0.35)
        gap = ask_float("Расстояние между rectangle внутри ленты", 0.25)
        per_band = max(1, ceil(candidate_count / band_count))

        bands = map(
            lambda band_index: take(
                per_band,
                map(
                    tr_rotate(angle),
                    gen_rectangle(
                        width=width,
                        height=height,
                        gap=gap,
                        start=(0.0, band_index * band_gap),
                    ),
                ),
            ),
            range(band_count),
        )
        return scenario, islice(chain.from_iterable(bands), candidate_count)

    if scenario == "crossing_bands":
        print("\n=== Настройки crossing_bands ===")
        angle = ask_float("Угол пересечения в градусах", 28.0)
        width = ask_float("Ширина rectangle", 0.8)
        height = ask_float("Высота rectangle", 0.35)
        gap = ask_float("Расстояние между rectangle внутри ленты", 0.18)
        per_band = max(1, ceil(candidate_count / 2))

        band_a = take(
            per_band,
            map(
                tr_translate(2.0, 0.8),
                map(
                    tr_rotate(angle),
                    gen_rectangle(width=width, height=height, gap=gap),
                ),
            ),
        )
        band_b = take(
            per_band,
            map(
                tr_translate(1.0, 2.4),
                map(
                    tr_rotate(-angle),
                    gen_rectangle(width=width, height=height, gap=gap),
                ),
            ),
        )
        return scenario, islice(chain(band_a, band_b), candidate_count)

    if scenario == "symmetric_triangles":
        print("\n=== Настройки symmetric_triangles ===")
        side = ask_float("Сторона triangle", 0.8)
        gap = ask_float("Расстояние между triangle", 0.25)
        y = ask_float("Смещение верхней ленты по Y", 1.1)
        per_band = max(1, ceil(candidate_count / 2))

        top = take(
            per_band, map(
                tr_translate(
                    0.0, y), gen_triangle(
                    side=side, gap=gap)))
        bottom = tuple(map(tr_symmetry("x"), top))
        return scenario, islice(chain(top, bottom), candidate_count)

    if scenario == "scaled_quads_between_rays":
        print("\n=== Настройки scaled_quads_between_rays ===")
        slope_low = ask_float("Коэффициент нижней прямой y = kx", 0.35)
        slope_high = ask_float("Коэффициент верхней прямой y = kx", 1.1)
        start_x = ask_float("Начальный X", 0.7)
        step_x = ask_float("Шаг по X", 0.45)
        width = ask_float("Ширина каждого четырёхугольника по X", 0.3)
        return scenario, quads_between_rays(
            candidate_count, slope_low, slope_high, start_x, step_x, width)

    if scenario == "zipped_triangles":
        print("\n=== Настройки zipped_triangles ===")
        side = ask_float("Сторона triangle", 0.8)
        gap = ask_float("Расстояние между triangle", 0.25)
        y = ask_float("Смещение верхней ленты по Y", 0.7)

        upper = take(
            candidate_count,
            gen_triangle(
                side=side,
                gap=gap,
                start=(
                    0.0,
                    y)))
        lower = tuple(map(tr_symmetry("x"), upper))
        return scenario, zip_polygons(upper, lower)

    raise ValueError(f"Неизвестный сценарий: {scenario}")


def make_transforms() -> tuple:
    transforms = []

    print("\n=== Дополнительные трансформации ===")
    print("Эти действия применяются после выбранного сценария генерации.")

    if ask_yes_no("Применить параллельный перенос?", default=False):
        dx = ask_float("Сдвиг по X", 0.0)
        dy = ask_float("Сдвиг по Y", 0.0)
        transforms.append(tr_translate(dx=dx, dy=dy))

    if ask_yes_no("Применить поворот?", default=False):
        angle = ask_float("Угол поворота в градусах", 30.0)
        transforms.append(tr_rotate(angle=angle))

    if ask_yes_no("Применить гомотетию / масштабирование?", default=False):
        k = ask_float("Коэффициент масштаба", 1.2)
        center_x = ask_float("Центр масштаба X", 0.0)
        center_y = ask_float("Центр масштаба Y", 0.0)
        transforms.append(tr_homothety(k=k, center=(center_x, center_y)))

    if ask_yes_no("Применить симметрию?", default=False):
        mode = ask_choice(
            "Выберите тип симметрии",
            ("x", "y", "origin", "angle", "line"),
            default="x",
        )

        if mode == "angle":
            angle = ask_float("Угол прямой симметрии в градусах", 45.0)
            transforms.append(tr_symmetry(angle))
        elif mode == "line":
            x1 = ask_float("Точка 1: X", 0.0)
            y1 = ask_float("Точка 1: Y", 0.0)
            x2 = ask_float("Точка 2: X", 1.0)
            y2 = ask_float("Точка 2: Y", 1.0)
            transforms.append(tr_symmetry(((x1, y1), (x2, y2))))
        else:
            transforms.append(tr_symmetry(mode))

    return tuple(transforms)


def make_filters() -> tuple:
    filters = []

    print("\n=== Фильтры ===")
    print("Фильтры оставляют только подходящие полигоны.")

    if ask_yes_no("Оставить только выпуклые полигоны?", default=False):
        filters.append(flt_convex_polygon)

    if ask_yes_no("Фильтровать по площади?", default=False):
        max_area = ask_float("Оставить полигоны с площадью меньше", 100.0)
        filters.append(flt_square(max_area))

    if ask_yes_no("Фильтровать по кратчайшей стороне?", default=False):
        max_side = ask_float(
            "Оставить полигоны с кратчайшей стороной меньше", 10.0)
        filters.append(flt_short_side(max_side))

    if ask_yes_no("Фильтровать по точке внутри полигона?", default=False):
        x = ask_float("Координата точки X", 0.0)
        y = ask_float("Координата точки Y", 0.0)
        filters.append(flt_point_inside((x, y)))

    if ask_yes_no(
        "Фильтровать по вершинам другого полигона внутри?",
        default=False,
    ):
        print(
            "Будет создан контрольный rectangle. Останутся полигоны, "
            "содержащие хотя бы одну его вершину."
        )
        x = ask_float("X контрольного rectangle", 0.0)
        y = ask_float("Y контрольного rectangle", 0.0)
        width = ask_float("Ширина контрольного rectangle", 1.0)
        height = ask_float("Высота контрольного rectangle", 1.0)
        filters.append(
            flt_polygon_angles_inside(
                make_reference_rectangle(x, y, width, height)
            )
        )

    if ask_yes_no(
        "Фильтровать пересекающиеся с контрольным rectangle?",
        default=False,
    ):
        print(
            "Будет создан контрольный rectangle. Останутся полигоны, "
            "которые с ним пересекаются."
        )
        x = ask_float("X контрольного rectangle", 3.2)
        y = ask_float("Y контрольного rectangle", -0.3)
        width = ask_float("Ширина контрольного rectangle", 1.8)
        height = ask_float("Высота контрольного rectangle", 1.3)
        filters.append(
            flt_intersects_any(
                (make_reference_rectangle(x, y, width, height),)
            )
        )

    return tuple(filters)


def format_number(value: float) -> str:
    rounded = round(float(value), 4)
    if rounded == -0.0:
        rounded = 0.0
    return str(rounded)


def format_point(point):
    return f"({format_number(point[0])}, {format_number(point[1])})"


def print_polygon(index, poly):
    print(f"\nПОЛИГОН #{index}")
    for point_item in poly:
        print(f"  {format_point(point_item)}")


def print_result(polygons):
    print("\n==============================")
    print("РЕЗУЛЬТАТ: ПОЛИГОНЫ")
    print("==============================")

    if not polygons:
        print(
            "Полигоны не найдены. Попробуйте ослабить фильтры "
            "или увеличить количество кандидатов."
        )
        return

    for index, poly in enumerate(polygons, start=1):
        print_polygon(index, poly)

    print("\n==============================")
    print("АГРЕГИРУЮЩИЕ ФУНКЦИИ")
    print("==============================")

    print("Количество полигонов:", len(polygons))
    print(
        "Ближайшая вершина к началу координат:",
        agr_origin_nearest(polygons),
    )
    print("Самая длинная сторона:", agr_max_side(polygons))
    print("Минимальная площадь:", agr_min_area(polygons))
    print("Суммарный периметр:", agr_perimeter(polygons))
    print("Суммарная площадь:", agr_area(polygons))


def main():
    print("Функциональный API для работы с полигонами")
    print("=========================================")

    candidate_count = ask_int(
        "Сколько фигур-кандидатов сгенерировать до фильтрации?",
        21,
    )
    result_count = ask_int(
        "Сколько полигонов вывести после фильтрации?",
        7,
    )

    scenario_name, polygons = ask_scenario_settings(candidate_count)
    transforms = make_transforms()
    filters = make_filters()

    save_path = ask_string(
        "\nПуть для сохранения изображения",
        default="examples/out/interactive_case.png",
    )
    title = ask_string(
        "Название изображения",
        default=f"Interactive case: {scenario_name}",
    )

    # Функциональный pipeline:
    # candidates -> map(transform) -> filter(predicate) -> take(result_count)
    transformed = apply_transforms(polygons, transforms)
    filtered = apply_filters(transformed, filters)
    result = take(result_count, filtered)

    print_result(result)

    if result:
        plot_polygons(
            result,
            title=title,
            save_path=save_path,
        )
        print("\n==============================")
        print("ИЗОБРАЖЕНИЕ")
        print("==============================")
        print(f"Сохранено в файл: {save_path}")


if __name__ == "__main__":
    main()

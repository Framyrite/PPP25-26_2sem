# Functional Polygons API

Учебный проект: **функциональный API для работы с полигонами**.

Проект умеет:

- генерировать последовательности полигонов;
- преобразовывать полигоны;
- фильтровать полигоны;
- визуализировать результат;
- считать площадь, периметр и другие характеристики;
- работать в функциональном стиле через `map`, `filter`, `reduce`, `itertools` и декораторы.

Полигон представлен как кортеж кортежей координат:

```python
((0, 0), (2, 0), (2, 2), (0, 2))
```

Это означает фигуру с вершинами:

```text
(0, 0)
(2, 0)
(2, 2)
(0, 2)
```

Последовательности полигонов представлены как итераторы.

---

## 1. Основная идея проекта

Программа работает как функциональный конвейер обработки данных:

```text
генератор фигур
    ↓
map — применить трансформации
    ↓
filter — применить фильтры
    ↓
take — взять нужное количество фигур
    ↓
print / plot / aggregate
```

Пример:

```python
from polygon_api import gen_rectangle, tr_translate, flt_square, take

polygons = gen_rectangle(width=2, height=1)

moved = map(tr_translate(5, 2), polygons)
filtered = filter(flt_square(10), moved)

result = take(7, filtered)

print(result)
```

Что здесь происходит:

1. `gen_rectangle()` создаёт бесконечную последовательность прямоугольников;
2. `map(tr_translate(5, 2), polygons)` сдвигает каждый прямоугольник;
3. `filter(flt_square(10), moved)` оставляет только фигуры с площадью меньше `10`;
4. `take(7, filtered)` берёт первые 7 подходящих фигур.

---

## 2. Что такое функциональный стиль

Функциональный стиль — это подход, где данные обрабатываются через функции, а не через ручное изменение переменных в циклах.

Обычный императивный стиль выглядел бы так:

```python
result = []

for polygon in polygons:
    moved_polygon = move_polygon(polygon)

    if area(moved_polygon) < 10:
        result.append(moved_polygon)
```

В этом проекте используется функциональный стиль:

```python
moved = map(tr_translate(5, 2), polygons)
filtered = filter(flt_square(10), moved)
result = take(7, filtered)
```

Главные признаки функционального стиля в проекте:

- полигоны не изменяются на месте;
- функции возвращают новые полигоны;
- последовательности обрабатываются как итераторы;
- трансформации применяются через `map`;
- фильтрация выполняется через `filter`;
- агрегирующие функции реализованы через `functools.reduce`;
- используются функции из `itertools`;
- фильтры и трансформации могут использоваться как декораторы.

---

## 3. Структура проекта

```text
functional-polygons/
├── polygon_api/
│   ├── __init__.py
│   ├── core.py
│   └── visualization.py
├── tests/
│   └── test_polygon_api.py
├── examples/
│   └── out/
├── demo.py
├── interactive_case.py
├── README.md
├── requirements.txt
└── pyproject.toml
```

Назначение файлов:

| Файл | Назначение |
|---|---|
| `polygon_api/core.py` | Основная логика: генераторы, трансформации, фильтры, агрегаторы |
| `polygon_api/visualization.py` | Визуализация полигонов через `matplotlib` |
| `polygon_api/__init__.py` | Удобный экспорт функций из пакета |
| `demo.py` | Демонстрация базового задания и дополнительных заданий |
| `interactive_case.py` | Интерактивный запуск через терминал |
| `tests/test_polygon_api.py` | Автоматические тесты |
| `requirements.txt` | Зависимости проекта |
| `examples/out/` | Папка для сохранённых изображений |

---

## 4. Установка

Проект находится в репозитории:

```text
https://github.com/Framyrite/PPP25-26_2sem
```

Сначала нужно скачать репозиторий:

```bash
git clone https://github.com/Framyrite/PPP25-26_2sem
```

После скачивания перейти в папку со второй лабораторной работой:

```bash
cd PPP25-26_2sem/2lab
```

Все следующие команды нужно выполнять именно из папки:

```text
PPP25-26_2sem/2lab
```

Проверить, что вы находитесь в нужной папке, можно командой:

### Windows PowerShell

```powershell
pwd
```

### Linux / macOS

```bash
pwd
```

В папке должны быть файлы и директории:

```text
demo.py
interactive_case.py
requirements.txt
README.md
polygon_api/
tests/
examples/
```

---

### Windows PowerShell

Создать виртуальное окружение:

```powershell
python -m venv venv
```

Активировать виртуальное окружение:

```powershell
.\venv\Scripts\Activate.ps1
```

Если PowerShell запрещает запуск виртуального окружения:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

Установить зависимости:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

---

### Linux / macOS

Создать виртуальное окружение:

```bash
python3 -m venv venv
```

Активировать виртуальное окружение:

```bash
source venv/bin/activate
```

Установить зависимости:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

---

### Проверка установки

После установки зависимостей можно запустить тесты:

```bash
python -m pytest -q
```

Ожидаемый результат:

```text
9 passed
```

Также можно запустить демонстрацию:

```bash
python demo.py
```

После запуска изображения будут сохранены в папку:

```text
examples/out/
```

## 5. Зависимости

Файл `requirements.txt`:

```text
matplotlib
pytest
```

Назначение зависимостей:

| Библиотека | Для чего нужна |
|---|---|
| `matplotlib` | Для визуализации полигонов |
| `pytest` | Для запуска автоматических тестов |

---

## 6. Быстрая проверка проекта

Запустить тесты:

```bash
pytest -q
```

Ожидаемый результат:

```text
9 passed
```

Запустить демонстрацию:

```bash
python demo.py
```

После запуска изображения появятся в папке:

```text
examples/out/
```

---

## 7. Интерактивный запуск

Файл `interactive_case.py` нужен для удобного ручного запуска.

Запуск:

```bash
python interactive_case.py
```

После запуска программа сама спрашивает параметры:

```text
Сколько фигур-кандидатов сгенерировать до фильтрации?
Сколько полигонов вывести после фильтрации?
Выберите сценарий генерации
Применить дополнительные трансформации?
Применить фильтры?
Куда сохранить изображение?
```

Если подходит значение по умолчанию, можно просто нажать `Enter`.

Строки в квадратных скобках показывают значения по умолчанию:

```text
[y/n, default: n]
[rectangle_line]
[21]
[7]
[0.0]
```

Например:

```text
Сколько полигонов вывести после фильтрации? [7]:
```

Если нажать `Enter`, будет использовано значение `7`.

---

## 8. Сценарии интерактивного запуска

В `interactive_case.py` доступны такие сценарии:

| Сценарий | Что делает |
|---|---|
| `rectangle_line` | Генерирует последовательность прямоугольников |
| `triangle_line` | Генерирует последовательность треугольников |
| `hexagon_line` | Генерирует последовательность шестиугольников |
| `mixed_base_sequences` | Генерирует rectangle, triangle и hexagon в трёх рядах |
| `parallel_bands` | Создаёт несколько параллельных лент под углом |
| `crossing_bands` | Создаёт две пересекающиеся ленты |
| `symmetric_triangles` | Создаёт две симметричные ленты треугольников |
| `scaled_quads_between_rays` | Создаёт четырёхугольники между двумя прямыми |
| `zipped_triangles` | Склеивает верхние и нижние треугольники через `zip_polygons` |

Пример выбора:

```text
Выберите сценарий генерации
1. rectangle_line
2. triangle_line
3. hexagon_line
4. mixed_base_sequences
5. parallel_bands
6. crossing_bands
7. symmetric_triangles
8. scaled_quads_between_rays
9. zipped_triangles
Выберите вариант [rectangle_line]:
```

Можно ввести номер:

```text
5
```

или название:

```text
parallel_bands
```

---

## 9. Пример интерактивного запуска

Команда:

```bash
python interactive_case.py
```

Пример работы:

```text
Функциональный API для работы с полигонами
=========================================

Сколько фигур-кандидатов сгенерировать до фильтрации? [21]:
Сколько полигонов вывести после фильтрации? [7]:

Выберите сценарий генерации
1. rectangle_line
2. triangle_line
3. hexagon_line
4. mixed_base_sequences
5. parallel_bands
6. crossing_bands
7. symmetric_triangles
8. scaled_quads_between_rays
9. zipped_triangles
Выберите вариант [rectangle_line]: 5

=== Настройки parallel_bands ===
Количество параллельных лент [3]:
Угол наклона лент в градусах [22.0]:
Расстояние между лентами по Y [0.8]:
Ширина rectangle [0.8]:
Высота rectangle [0.35]:
Расстояние между rectangle внутри ленты [0.25]:

=== Дополнительные трансформации ===
Применить параллельный перенос? [y/n, default: n]:
Применить поворот? [y/n, default: n]:
Применить гомотетию / масштабирование? [y/n, default: n]:
Применить симметрию? [y/n, default: n]:

=== Фильтры ===
Оставить только выпуклые полигоны? [y/n, default: n]:
Фильтровать по площади? [y/n, default: n]:
Фильтровать по кратчайшей стороне? [y/n, default: n]:
Фильтровать по точке внутри полигона? [y/n, default: n]:
```

После завершения программа:

1. выводит координаты полигонов;
2. выводит агрегирующие значения;
3. сохраняет изображение.

По умолчанию изображение сохраняется сюда:

```text
examples/out/interactive_case.png
```

---

## 10. Генераторы полигонов

Реализованы три бесконечных генератора непересекающихся фигур:

| Функция | Что генерирует |
|---|---|
| `gen_rectangle` | Прямоугольники |
| `gen_triangle` | Равносторонние треугольники |
| `gen_hexagon` | Правильные шестиугольники |

Пример:

```python
from polygon_api import gen_rectangle, take

rectangles = take(
    7,
    gen_rectangle(width=2, height=1, gap=0.5)
)

print(rectangles)
```

Важно: генераторы бесконечные.

Нельзя делать так:

```python
list(gen_rectangle())
```

Такой код будет выполняться бесконечно.

Правильно:

```python
take(7, gen_rectangle())
```

---

## 11. Трансформации

Трансформации изменяют положение или размер полигона.

Реализованы функции:

| Функция | Что делает |
|---|---|
| `tr_translate(dx, dy)` | Параллельный перенос |
| `tr_rotate(angle)` | Поворот на угол в градусах |
| `tr_symmetry(axis)` | Симметрия относительно `x`, `y`, `origin` или произвольной прямой |
| `tr_homothety(k)` | Гомотетия / масштабирование |

Пример переноса:

```python
from polygon_api import gen_rectangle, tr_translate, take

polygons = gen_rectangle(width=2, height=1)

moved = map(
    tr_translate(5, 2),
    polygons,
)

result = take(7, moved)

print(result)
```

Пример нескольких трансформаций:

```python
from polygon_api import gen_rectangle, tr_translate, tr_rotate, tr_homothety, take

polygons = gen_rectangle(width=2, height=1)

translated = map(tr_translate(5, 2), polygons)
rotated = map(tr_rotate(30), translated)
scaled = map(tr_homothety(1.5), rotated)

result = take(7, scaled)

print(result)
```

---

## 12. Фильтры

Фильтры оставляют только те полигоны, которые подходят под условие.

Реализованы все 6 фильтров из задания:

| Функция | Что делает |
|---|---|
| `flt_convex_polygon` | Оставляет выпуклые полигоны |
| `flt_angle_point(point)` | Оставляет полигоны с вершиной в заданной точке |
| `flt_square(max_area)` | Оставляет полигоны с площадью меньше заданной |
| `flt_short_side(max_length)` | Оставляет полигоны с кратчайшей стороной меньше заданной |
| `flt_point_inside(point)` | Оставляет выпуклые полигоны, содержащие заданную точку |
| `flt_polygon_angles_inside(other_polygon)` | Оставляет полигоны, содержащие хотя бы одну вершину другого полигона |

Пример фильтрации по площади:

```python
from polygon_api import gen_rectangle, flt_square, take

polygons = gen_rectangle(width=2, height=2)

filtered = filter(
    flt_square(10),
    polygons,
)

result = take(7, filtered)

print(result)
```

Пример фильтрации по кратчайшей стороне:

```python
from polygon_api import gen_rectangle, flt_short_side, take

polygons = gen_rectangle(width=3, height=1)

filtered = filter(
    flt_short_side(2),
    polygons,
)

result = take(7, filtered)

print(result)
```

---

## 13. Визуализация

Для визуализации используется функция:

```python
plot_polygons
```

Пример:

```python
from polygon_api import gen_rectangle, take, plot_polygons

polygons = take(7, gen_rectangle(width=2, height=1))

plot_polygons(
    polygons,
    title="Rectangles",
    save_path="examples/out/rectangles.png",
)
```

Изображение будет сохранено в файл:

```text
examples/out/rectangles.png
```

---

## 14. Агрегирующие функции

Агрегирующие функции принимают последовательность полигонов и возвращают одно итоговое значение.

Реализованы функции:

| Функция | Что считает |
|---|---|
| `agr_origin_nearest(polygons)` | Вершину, ближайшую к началу координат |
| `agr_max_side(polygons)` | Самую длинную сторону |
| `agr_min_area(polygons)` | Минимальную площадь |
| `agr_perimeter(polygons)` | Суммарный периметр |
| `agr_area(polygons)` | Суммарную площадь |

Пример:

```python
from polygon_api import (
    gen_rectangle,
    take,
    agr_area,
    agr_perimeter,
    agr_max_side,
    agr_min_area,
    agr_origin_nearest,
)

polygons = take(5, gen_rectangle(width=2, height=1))

print("Суммарная площадь:", agr_area(polygons))
print("Суммарный периметр:", agr_perimeter(polygons))
print("Самая длинная сторона:", agr_max_side(polygons))
print("Минимальная площадь:", agr_min_area(polygons))
print("Ближайшая вершина к началу координат:", agr_origin_nearest(polygons))
```

Внутри эти функции реализованы через `functools.reduce`.

---

## 15. Декораторы

Фильтры и трансформации могут использоваться не только через `filter` и `map`, но и как декораторы.

Пример фильтра-декоратора:

```python
from polygon_api import flt_convex_polygon

@flt_convex_polygon
def collect(polygons):
    return tuple(polygons)
```

Пример трансформации-декоратора:

```python
from polygon_api import tr_translate

@tr_translate(10, 0)
def collect(polygons):
    return tuple(polygons)
```

Это значит, что итератор полигонов будет обработан до попадания внутрь функции.

---

## 16. Склейка полигонов

Функция:

```python
zip_polygons(iterator1, iterator2, ...)
```

склеивает полигоны из нескольких последовательностей.

Пример:

```python
from polygon_api import zip_polygons

first = [
    ((1, 1), (2, 2), (3, 1)),
    ((11, 11), (12, 12), (13, 11)),
]

second = [
    ((1, -1), (2, -2), (3, -1)),
    ((11, -11), (12, -12), (13, -11)),
]

result = list(zip_polygons(first, second))

print(result)
```

Результат:

```python
[
    ((1, 1), (2, 2), (3, 1), (1, -1), (2, -2), (3, -1)),
    ((11, 11), (12, 12), (13, 11), (11, -11), (12, -12), (13, -11)),
]
```

---

## 17. Дополнительные утилиты

Также реализованы функции:

| Функция | Что делает |
|---|---|
| `count_2D(start, step)` | Генерирует бесконечную последовательность точек |
| `zip_tuple(*tuples)` | Склеивает несколько кортежей в один |
| `take(n, iterator)` | Берёт первые `n` элементов из итератора |

Пример `count_2D`:

```python
from polygon_api import count_2D, take

points = take(
    3,
    count_2D(start=(1, 2), step=(2, -1)),
)

print(points)
```

Результат:

```python
((1, 2), (3, 1), (5, 0))
```

Пример `zip_tuple`:

```python
from polygon_api import zip_tuple

result = zip_tuple((1, 2), (3,), (4, 5))

print(result)
```

Результат:

```python
(1, 2, 3, 4, 5)
```

---

## 18. Демонстрация задания

Файл `demo.py` создаёт изображения для базового задания и дополнительных заданий.

Запуск:

```bash
python demo.py
```

После запуска изображения сохраняются в папку:

```text
examples/out/
```

Создаются изображения:

| Файл | Что показывает |
|---|---|
| `01_base_sequences.png` | 7 фигур каждого типа: rectangle, triangle, hexagon |
| `02_parallel_bands.png` | Три параллельные ленты под острым углом |
| `03_crossing_bands.png` | Две пересекающиеся ленты не в начале координат |
| `04_symmetric_triangles.png` | Две симметричные ленты треугольников |
| `05_quads_between_rays.png` | Четырёхугольники разного масштаба между двумя прямыми |
| `06_filter_exactly_six.png` | Фильтрация, где на выходе ровно 6 фигур |
| `07_filter_short_side.png` | Фильтрация по кратчайшей стороне |
| `08_filter_intersections.png` | Фильтрация пересекающихся фигур |
| `09_zip_polygons.png` | Пример склейки полигонов через `zip_polygons` |

---

## 19. Тесты

В проекте есть автоматические тесты.

Файл с тестами:

```text
tests/test_polygon_api.py
```

Запуск тестов:

```bash
pytest -q
```

Ожидаемый результат:

```text
9 passed
```

Тесты проверяют основные части проекта:

- генераторы;
- трансформации;
- фильтры;
- декораторы;
- агрегирующие функции;
- дополнительные утилиты.

---

## 20. Дополнительные задания

Для максимальной оценки нужно выполнить дополнительные задания на сумму не менее 5 баллов.

В проекте выполнены:

| № | Дополнительное задание | Статус | Баллы |
|---|---|---|---:|
| 1 | Расширенные фильтры: все 6 фильтров | Выполнено | 2 |
| 2 | Все 3 сценария применения фильтров | Выполнено в `demo.py` | 1 |
| 3 | Полный набор декораторов | Выполнено | 1 |
| 4 | Агрегирующие функции через `reduce` | Выполнено | 1 |

Итого:

```text
2 + 1 + 1 + 1 = 5 баллов
```

Дополнительно сверх минимума реализованы:

- все 5 агрегирующих функций;
- `zip_polygons`;
- `count_2D`;
- `zip_tuple`.

---

## 21. Минимальная проверка перед сдачей

Перед сдачей достаточно выполнить:

```bash
pytest -q
python demo.py
python interactive_case.py
```

Нужно убедиться, что:

1. тесты проходят;
2. изображения появляются в `examples/out/`;
3. интерактивный запуск работает;
4. программа выводит полигоны и агрегирующие значения;
5. изображения открываются нормально.

---

## 22. Краткий пример самостоятельного использования

```python
from polygon_api import (
    gen_rectangle,
    tr_translate,
    tr_rotate,
    flt_square,
    take,
    plot_polygons,
    agr_area,
    agr_perimeter,
)

polygons = gen_rectangle(width=2, height=1, gap=0.5)

translated = map(tr_translate(5, 2), polygons)
rotated = map(tr_rotate(30), translated)
filtered = filter(flt_square(20), rotated)

result = take(7, filtered)

print("Полигоны:")
print(result)

print("Суммарная площадь:", agr_area(result))
print("Суммарный периметр:", agr_perimeter(result))

plot_polygons(
    result,
    title="Custom example",
    save_path="examples/out/custom_example.png",
)
```

Этот пример показывает полный функциональный pipeline:

```text
generator → map → map → filter → take → print → plot
```

---

## 23. Информация об авторе

Автор: Framyrite

GitHub: [`ССЫЛКА_НА_GITHUB`](https://github.com/Framyrite)

Репозиторий проекта: [`ССЫЛКА_НА_РЕПОЗИТОРИЙ`](https://github.com/Framyrite/PPP25-26_2sem)

Email: framyrite@yandex.ru

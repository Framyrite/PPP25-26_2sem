from __future__ import annotations

from collections.abc import Iterable
from itertools import chain
from pathlib import Path
from typing import Any

from matplotlib import pyplot as plt
from matplotlib.patches import Polygon as MplPolygon

from .core import Polygon


def plot_polygons(
    polygons: Iterable[Polygon],
    *,
    title: str | None = None,
    ax: Any | None = None,
    show: bool = False,
    save_path: str | Path | None = None,
    facecolor: str = "none",
    edgecolor: str = "black",
    alpha: float = 0.8,
    linewidth: float = 1.8,
) -> Any:
    """Visualize polygons from any iterator.

    The iterator is materialized once because matplotlib needs the full set of
    shapes to calculate axes limits.
    """

    data = tuple(polygons)
    if ax is None:
        _, ax = plt.subplots(figsize=(8, 5))

    for poly in data:
        patch = MplPolygon(
            poly,
            closed=True,
            facecolor=facecolor,
            edgecolor=edgecolor,
            alpha=alpha,
            linewidth=linewidth,
        )
        ax.add_patch(patch)

    if data:
        xs = tuple(map(lambda p: p[0], chain.from_iterable(data)))
        ys = tuple(map(lambda p: p[1], chain.from_iterable(data)))
        x_pad = max((max(xs) - min(xs)) * 0.08, 0.5)
        y_pad = max((max(ys) - min(ys)) * 0.08, 0.5)
        ax.set_xlim(min(xs) - x_pad, max(xs) + x_pad)
        ax.set_ylim(min(ys) - y_pad, max(ys) + y_pad)

    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, linewidth=0.4, alpha=0.4)
    if title:
        ax.set_title(title)

    if save_path is not None:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        ax.figure.savefig(save_path, bbox_inches="tight", dpi=150)

    if show:
        plt.show()

    return ax

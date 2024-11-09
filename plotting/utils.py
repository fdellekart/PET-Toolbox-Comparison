import re

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import Formatter


get_blocklable = lambda block_name: re.match(
    r"^([a-zA-Z]+)(?:_itr\d+)?$", block_name
).group(1)


class MyFormatter(Formatter):
    def __call__(self, x, pos=0):
        minutes = int(x // 60)
        seconds = int(x % 60)
        assert seconds == 0
        return f"{minutes}"


def add_blocks_to_ax(ax: plt.Axes, frame_timings: pd.Series):
    """Add vspan colorings to axes for individual blocks inside frame timings.

    :param ax: the mpl axes object to draw on
    :param frame_timings: A series with a multiindex with block names on
        first level and 'start' or 'end' on second level indicating the
        start and end times of the individual blocks in seconds from start.
        Blocks of the format '<block_name>_itr<n>' are labeled and colored
        only once with `block_name`.
    """
    cmap = plt.get_cmap("tab20")
    block_names = frame_timings.index.levels[0].drop("frame")
    block_labels = list({get_blocklable(block_name) for block_name in block_names})
    existing_labels = set()

    for block_name in block_names:
        block_label = get_blocklable(block_name)
        block_start = frame_timings[block_name]["start"]
        block_end = frame_timings[block_name]["end"]
        if block_start == block_end:
            continue

        ax.axvspan(
            frame_timings[block_name]["start"],
            frame_timings[block_name]["end"],
            alpha=0.3,
            label=(block_label if block_label not in existing_labels else None),
            color=cmap(block_labels.index(get_blocklable(block_name))),
        )
        existing_labels.add(block_label)

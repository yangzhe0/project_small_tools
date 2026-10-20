"""Approved map-first layout: world map, China inset and concise system titles.

Red markers identify Chinese ground sites, not team membership. Symbol areas
represent selected mapped catalogue entries and are not unique exposure counts.
"""
import sys
sys.dont_write_bytecode = True

import hashlib
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon, Rectangle
import numpy as np
import pandas as pd
from paths import DATA, FIGURES, RESOURCES

CONFIG = [
    ('total_obs', 'All systems', 'global_satellite_observations_map.png'),
    ('J6-13', 'J6–J13', 'map_J6-J13_jupiter_satellites.png'),
    ('S1-8', 'S1–S8', 'map_S1-S8_saturn_satellites.png'),
    ('S9', 'S9', 'map_S9_phoebe.png'),
    ('U1-5', 'U1–U5', 'map_U1-U5_uranus_satellites.png'),
    ('N1', 'N1', 'map_N1_triton.png'),
    ('N2', 'N2', 'map_N2_nereid.png'),
]


def symbols(counts, maximum):
    return 10 + 95 * (np.log10(np.asarray(counts) + 1) / np.log10(maximum + 1)) ** 2


BLUE = '#427fa9'
RED = '#d34c55'
INK = '#243746'
OCEAN = '#f0f6fa'
LAND = '#f9f8f3'
NAMES = {'286': 'Kunming', '337': 'Sheshan', 'O44': 'Lijiang', 'O49': 'Yaoan', '327': 'Xinglong', 'D29': 'Xuyi', '334': 'Qingdao'}
CHINA = (97.0, 125.5, 21.0, 43.5)
LABELS = {'O44': (98.5, 29.2, 'left'), 'O49': (99.0, 22.8, 'left'), '286': (105.1, 25.0, 'left'), '337': (122.7, 28.9, 'right'), 'D29': (115.7, 32.2, 'right'), '334': (122.8, 36.5, 'right'), '327': (114.5, 40.2, 'right')}

def polygons():
    features = json.loads((RESOURCES / 'ne_110m_admin_0_countries.geojson').read_text(encoding='utf-8'))['features']
    result = []
    for feature in features:
        geometry = feature['geometry']
        parts = [geometry['coordinates']] if geometry['type'] == 'Polygon' else geometry['coordinates']
        for part in parts:
            result.append(np.asarray(part[0]))
    return result

def base_map(ax, geometry, bounds, *, local=False):
    ax.set_facecolor(OCEAN if not local else '#fbfcfc')
    patches = [Polygon(part, closed=True) for part in geometry]
    ax.add_collection(PatchCollection(patches, facecolor=LAND, edgecolor='#bbc9cf', linewidth=0.45 if local else 0.32, zorder=1))
    ax.set_xlim(bounds[0:2])
    ax.set_ylim(bounds[2:4])
    ax.set_aspect('equal', adjustable='box')
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_color('#c6d3d9')
        spine.set_linewidth(0.65)
    if not local:
        for x in range(-120, 180, 60):
            ax.axvline(x, color='#dbe5eb', linewidth=0.4, zorder=0)
        for y in [-30, 0, 30, 60]:
            ax.axhline(y, color='#dbe5eb', linewidth=0.4, linestyle='--' if y == 0 else '-', zorder=0)

def scatter_sites(ax, frame, key, maximum, *, local=False):
    for is_china, color in [(False, BLUE), (True, RED)]:
        rows = frame[(frame.country == 'China') == is_china]
        ax.scatter(rows.longitude, rows.latitude, s=symbols(rows[key].to_numpy(), maximum) * (1.45 if local else 1.12), facecolors=color, edgecolors='white', linewidths=0.6, alpha=0.9 if is_china else 0.68, zorder=4 if is_china else 3)

def draw_detail(fig, position, geometry, china, key, maximum, label, *, inset_on):
    bounds = CHINA
    ax = inset_on.inset_axes(position)
    base_map(ax, geometry, bounds, local=True)
    rows = china[(china.longitude >= bounds[0]) & (china.longitude <= bounds[1]) & (china.latitude >= bounds[2]) & (china.latitude <= bounds[3])]
    scatter_sites(ax, rows, key, maximum, local=True)
    ax.text(0.035, 0.96, label, transform=ax.transAxes, va='top', fontsize=8.5, color=INK, fontweight='bold', zorder=6)
    labels = []
    for _, row in rows.iterrows():
        x, y, ha = LABELS[row.code]
        annotation = ax.annotate(f'{row.code}  {NAMES[row.code]}', xy=(row.longitude, row.latitude), xytext=(x, y), ha=ha, va='center', fontsize=7.4, color='#a53e48', arrowprops=dict(arrowstyle='-', linewidth=0.55, color='#b76b73', shrinkA=3, shrinkB=4), bbox=dict(facecolor='#fbfcfc', edgecolor='none', alpha=0.84, pad=0.8), zorder=7)
        labels.append(annotation)
    return (ax, labels, rows.code.tolist())

def legend(fig, maximum):
    handles = [Line2D([], [], color=BLUE, marker='o', linestyle='', markersize=5, label='Other ground sites'), Line2D([], [], color=RED, marker='o', linestyle='', markersize=5, label='Chinese ground sites')]
    box = fig.legend(handles=handles, loc='lower left', bbox_to_anchor=(0.025, 0.06), ncol=2, frameon=True, facecolor='white', edgecolor='#CBD5E1', fontsize=11, borderpad=0.65, handletextpad=0.5, columnspacing=1.5, labelcolor='#1E293B')
    box.get_frame().set_boxstyle('round,pad=0.25,rounding_size=0.2')
    fig.text(0.4, 0.079, 'Entry count (log scale)', fontsize=10.5, color='#334155')
    positions = [0.61, 0.71, 0.82]
    for x, value in zip(positions, [100, 1000, 10000]):
        marker = np.sqrt(float(symbols([value], maximum)[0]) * 1.12)
        fig.add_artist(Line2D([x], [0.083], marker='o', markersize=marker, markerfacecolor=BLUE, markeredgecolor='white', linestyle='', alpha=0.68, transform=fig.transFigure))
        fig.text(x + 0.013, 0.079, f'{value:,}', fontsize=10.5, fontweight='bold', color='#334155')

def draw(key, title, filename, frame, stats, geometry):
    sub = frame[frame[key] > 0].copy()
    china = sub[sub.country == 'China']
    mapped = int(sub[key].sum())
    cn_count = int(china[key].sum())
    maximum = max(int(sub[key].max()), 1)
    selected = int(stats.selected_entries.sum()) if key == 'total_obs' else int(stats.loc[stats.system == key, 'selected_entries'].iloc[0])
    space = int(stats.space_entries.sum()) if key == 'total_obs' else int(stats.loc[stats.system == key, 'space_entries'].iloc[0])
    unresolved = int(stats.unresolved_entries.sum()) if key == 'total_obs' else int(stats.loc[stats.system == key, 'unresolved_entries'].iloc[0])
    expected_ground = int(stats.mapped_entries.sum()) if key == 'total_obs' else int(stats.loc[stats.system == key, 'mapped_entries'].iloc[0])
    assert mapped == expected_ground
    fig = plt.figure(figsize=(18.4, 9), dpi=2350 / 9, facecolor='white')
    summary = f'{len(sub):,} ground sites  /  {mapped:,} mapped entries  /  China {cn_count:,} ({100 * cn_count / mapped:.1f}%)'
    fig.text(0.5, 0.985, f'Geographic Distribution of Astrometric Observations\n{title}', fontsize=21.5, color='#0F172A', fontweight='bold', ha='center', va='top', linespacing=1.12)
    fig.text(0.5, 0.886, summary, fontsize=13.5, fontweight='bold', ha='center', color='#0369A1')
    annotations = []
    details = []
    labelled = []
    world = fig.add_axes([0.025, 0.116, 0.95, 0.757])
    base_map(world, geometry, (-180, 180, -60, 85))
    scatter_sites(world, sub, key, maximum)
    detail, texts, codes = draw_detail(fig, [0.028, 0.03, 0.245, 0.435], geometry, china, key, maximum, 'CHINA DETAIL', inset_on=world)
    details.append(detail)
    annotations += texts
    labelled += codes
    world.add_patch(Rectangle((CHINA[0], CHINA[2]), CHINA[1] - CHINA[0], CHINA[3] - CHINA[2], facecolor='none', edgecolor=RED, linewidth=0.65, linestyle=(0, (4, 3)), zorder=2))
    legend(fig, maximum)
    fig.text(0.03, 0.025, 'Mapped ground entries; known overlaps adjusted; not certified unique observations.', fontsize=9.5, color='#334155')
    fig.text(0.975, 0.025, 'Data Source: IMCCE/NSDC + published supplement | MPC | Natural Earth', fontsize=10.5, fontweight='bold', color='#1E293B', ha='right')
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    from matplotlib.text import Text
    label_boxes = [Text.get_window_extent(a, renderer) for a in annotations]
    text_collisions = [(annotations[i].get_text(), annotations[j].get_text()) for i in range(len(label_boxes)) for j in range(i + 1, len(label_boxes)) if label_boxes[i].overlaps(label_boxes[j])]
    assert not text_collisions, ('A_world_focus', key, text_collisions)
    figure_texts = fig.texts
    boxes = [t.get_window_extent(renderer) for t in figure_texts]
    assert all((fig.bbox.contains(box.x0, box.y0) and fig.bbox.contains(box.x1, box.y1) for box in boxes)), (key, 'figure text clipped')
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            assert not boxes[i].overlaps(boxes[j]), (key, 'header/footer overlap', figure_texts[i].get_text(), figure_texts[j].get_text())
    assert fig.legends[0].get_window_extent(renderer).y1 < world.get_window_extent(renderer).y0, (key, 'legend overlaps map')
    assert sorted(labelled) == sorted(china.code.tolist()), ('A_world_focus', key, 'missing Chinese site label')
    hidden = []
    panel = details[0].get_window_extent(renderer)
    for _, row in sub.iterrows():
        if panel.contains(*world.transData.transform((row.longitude, row.latitude))):
            hidden.append(row.code)
    assert not hidden, ('Inset hides world sites', hidden)
    output_variant = 'A_typography_refined'
    target = FIGURES / filename
    target.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(target, dpi=2350 / 9, facecolor='white')
    plt.close(fig)
    return dict(variant=output_variant, key=key, title=title, file=filename, sites=len(sub), mapped_entries=mapped, china_entries=cn_count, selected_entries=selected, space_entries=space, unresolved_entries=unresolved, china_label_codes=sorted(labelled), text_collisions=text_collisions, obscured_world_sites=hidden)


def main():
    frame = pd.read_csv(DATA / 'observatory_satellite_summary.csv', dtype={'code': str})
    stats = pd.read_csv(DATA / 'satellite_statistics.csv')
    geometry = polygons()
    result = [draw(*config, frame, stats, geometry) for config in CONFIG]
    metadata = dict(
        input_sha256=hashlib.sha256((DATA / 'observatory_satellite_summary.csv').read_bytes()).hexdigest(),
        layout='approved_A_map_first',
        scope='Worldwide mapped ground catalogue entries; red=Chinese sites, blue=other sites; not team membership',
        style_reference='figures/number.png',
        maps=result,
    )
    (DATA / 'map_metadata.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Generated seven approved A maps, 4804 x 2350 px, from unchanged ground-entry statistics.')


if __name__ == '__main__':
    main()

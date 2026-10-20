"""Shared project paths; scripts work independently of the launch directory."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INPUTS = ROOT / 'inputs'
RESOURCES = INPUTS / 'resources'
DATA = ROOT / 'data'
FIGURES = ROOT / 'figures'
REPORTS = ROOT / 'reports'
CACHE = ROOT / '.cache'

for directory in (DATA, FIGURES, REPORTS):
    directory.mkdir(parents=True, exist_ok=True)

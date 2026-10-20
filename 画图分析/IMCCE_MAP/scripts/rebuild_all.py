"""Rebuild the current data, eight figures and reports using this interpreter."""
from pathlib import Path
import os
import subprocess
import sys
sys.dont_write_bytecode = True
from paths import ROOT, REPORTS


def main():
    scripts = Path(__file__).resolve().parent
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    for name in ['generate_global_map_data.py', 'plot_imcce_number.py', 'generate_all_satellite_maps.py']:
        subprocess.run([sys.executable, str(scripts/name)], check=True, env=env)
    result = subprocess.run([sys.executable, str(scripts/'verify_all.py')], capture_output=True, text=True, env=env)
    log = result.stdout + result.stderr
    (REPORTS/'verification.log').write_text(log, encoding='utf-8')
    print(log)
    result.check_returncode()
    subprocess.run([sys.executable, str(scripts/'build_delivery_report.py')], check=True, env=env)


if __name__ == '__main__':
    main()

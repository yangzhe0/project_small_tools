"""Build shared statistics and map inputs from a single source ledger."""
from imcce_pipeline import build

if __name__ == '__main__':
    result=build()
    print('Source-ledger pipeline complete:', result['totals'])
    print('Unknown rows retained; no proportional allocation. Limits: pipeline_manifest.json')

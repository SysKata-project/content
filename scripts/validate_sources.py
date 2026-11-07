"""CI validation of the authoring fixture and every checked-in release source."""
import json
from pathlib import Path
import subprocess

from compile_bundle import compile_bundle, load_source, check_references

root = Path(__file__).resolve().parents[1]
commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
sources = [root / 'fixtures/authoring/catalog.yaml', *sorted((root / 'releases').glob('*/catalog.yaml'))]
for source in sources:
    catalog = load_source(source)
    release = source.is_relative_to(root / 'releases')
    if release and source.parent.name != catalog['bundle_version']:
        raise ValueError('release directory and bundle version must match')
    cases = json.loads(source.with_name('assessment-cases.json').read_text())
    compile_bundle(catalog, cases, commit, release=release)
    check_references(catalog)
    print(f'Validated schema, assessment fixtures and reference links: {source.relative_to(root)}')

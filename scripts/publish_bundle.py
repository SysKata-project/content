"""Publish a new content version once; never replace a release, tag or asset."""
import argparse
import json
from pathlib import Path
import re
import subprocess

try:
    from .compile_bundle import verify_bundle, release_files
except ImportError:
    from compile_bundle import verify_bundle, release_files

REPOSITORY = 'SysKata-project/content'


def gh(*args):
    return subprocess.check_output(['gh', *args], text=True).strip()


def verify_source(directory, version):
    source = Path('releases') / version / 'catalog.yaml'
    _, rebuilt = release_files(source, source.parent / 'assessment-cases.json')
    if any((directory / name).read_bytes() != data for name, data in rebuilt.items()):
        raise ValueError('bundle differs from the clean, reviewed source checkout')


def publish(directory, expected_manifest_hash):
    manifest = verify_bundle(directory, expected_manifest_hash)
    if manifest['release_eligible'] is not True:
        raise ValueError('fixture/development bundles cannot be published')
    version = manifest['bundle_version']
    if not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+', version):
        raise ValueError('invalid bundle version')
    verify_source(directory, version)
    tag = 'content-v' + version
    api = f'repos/{REPOSITORY}'
    settings = json.loads(gh('api', api + '/immutable-releases'))
    if settings.get('enabled') is not True:
        raise ValueError('enable GitHub release immutability before publishing')
    # A successful registry read is mandatory. Network/auth errors never mean absent.
    releases = json.loads(gh('api', '--paginate', '--slurp', api + '/releases?per_page=100'))
    if any(r['tag_name'] == tag for page in releases for r in page):
        raise ValueError('bundle version already exists, including drafts')
    refs = json.loads(gh('api', api + '/git/matching-refs/tags/' + tag))
    if any(ref['ref'] == 'refs/tags/' + tag for ref in refs):
        raise ValueError('bundle tag already exists')
    # Only reviewed/merged source may be released, even if run outside Actions.
    comparison = json.loads(gh('api', api + '/compare/' + manifest['source_commit'] + '...main'))
    if comparison['status'] not in ('ahead', 'identical'):
        raise ValueError('source commit is not on main')
    files = [str(directory / name) for name in ('learner.json', 'assessment.json', 'manifest.json')]
    gh('release', 'create', tag, *files, '--repo', REPOSITORY, '--draft',
       '--target', manifest['source_commit'], '--title', 'Content ' + version,
       '--notes', 'Immutable content bundle. Manifest SHA-256: ' + expected_manifest_hash)
    # Upload completion precedes publication, because immutable assets lock then.
    gh('release', 'edit', tag, '--repo', REPOSITORY, '--draft=false', '--latest=false')
    released = json.loads(gh('api', api + '/releases/tags/' + tag))
    if released.get('immutable') is not True or released.get('draft') is not False:
        raise ValueError('release publication/immutability could not be confirmed')
    print(released['html_url'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--manifest-sha256', required=True)
    args = parser.parse_args()
    try:
        publish(args.directory, args.manifest_sha256)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f'{exc}\n')


if __name__ == '__main__':
    main()

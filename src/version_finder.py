import json
from urllib.error import HTTPError
import requests

from pathlib import Path
from urllib.request import urlopen

from src.config import ManifestType, PricoHost


def find_version(host: PricoHost, default_version: int) -> int:
    max_test_amount = 30
    test_multiplier = 10
    version = default_version

    s = requests.session

    i = 0
    while i < max_test_amount:
        guess = version + i * test_multiplier
        url = f'http://{host.value}/{ManifestType.ASSET.value % (guess, "manifest_assetmanifest")}'
        try:
            response = urlopen(url)
            if response.code == 200:
                version = guess
                i = 0
        except HTTPError as err:
            if err.code != 403:
                raise err
        i += 1
    return version


def find_version_fallback(host: PricoHost) -> int:
    if host == PricoHost.JP:
        r = requests.get("https://redive.estertion.win/last_version_jp.json")
        latest = json.loads(r.content)
    else:
        raise "could not find version"
    return int(latest["TruthVersion"])


def get_latest_version(host: PricoHost) -> int:
    print("Finding latest version")
    default_version = 10047000
    versions = {}
    path = Path("versions.json")
    if path.exists():
        versions = json.loads(path.read_text())
        default_version = versions.get(host.value, default_version)
    try:
        version = find_version(host, default_version)
    except Exception as e:
        print(e, "using fallback version finder")
        version = find_version_fallback(host)

    versions[host.value] = version
    path.write_text(json.dumps(versions))
    print(f"{version=}")
    return version

import json
from pathlib import Path

from requests_futures.sessions import FuturesSession

from src.config import ManifestType, PricoHost


def find_version(host: PricoHost, default_version: int) -> int:
    max_test_amount = 30
    test_multiplier = 10
    version = default_version

    s = FuturesSession()
    while True:
        urls = [
            f'http://{host.value}/{ManifestType.ASSET.value % (version + (i + 1) * test_multiplier, "manifest_assetmanifest")}'
            for i in range(max_test_amount)
        ]
        responses = [s.get(url) for url in urls]
        results = [r.result().status_code == 200 for r in responses]
        if not any(results):
            return version
        version += (max_test_amount - results[::-1].index(True)) * test_multiplier


def find_version_fallback(host: PricoHost) -> int:
    s = FuturesSession()
    if host == PricoHost.JP:
        r = s.get("https://redive.estertion.win/last_version_jp.json").result()
        latest = json.loads(r.content)
    else:
        raise "could not find version"
    return int(latest["TruthVersion"])


def get_latest_version(host: PricoHost) -> int:
    print("Finding latest version")
    default_version = 10047400
    versions = {}
    path = Path("versions.json")
    if path.exists():
        versions = json.loads(path.read_text())
        default_version = versions.get(host.value, default_version)
    try:
        version = find_version(host, default_version)
    except Exception as e:
        print(e, "\nusing fallback version finder")
        version = find_version_fallback(host)

    versions[host.value] = version
    path.write_text(json.dumps(versions))
    print(f"{version=}")
    return version

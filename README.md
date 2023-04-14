# Princess Connect Asset Extractor

Yet another tool to download, extract and convert assets from Princess Connect! Re: Dive.

## Features

- Downloads files from the games server with optional filters

  - assetbundles (.unity3d)
  - audio (.awb / .acb)
  - video (.usm)

- Extracts / Converts above formats

  - .unity3d -> .png / .txt
  - .awb / .acb -> .wav
  - .usm -> .mp4

- Reconstructs .skel from .cysp files for SD (playable) units (experimental)

## Install

- Clone this repo or download the latest release's source code
- cmd `python -m pip install -r requirements.txt`
- Make sure you have usmtoolkit (see section below)

## Requires

[UsmToolkit](https://github.com/Rikux3/UsmToolkit) (audio and video) : Download in the release page and put it in the root folder or if you already have it somewhere edit the paths in `src/config.py` instead

## Depends on

[latest TruthVersion](https://redive.estertion.win/last_version_jp.json) : `Dataminer(version=<version>)` if you want to provide the verion number yourself  
[master.db](https://github.com/lskyset/nozomi-cb-data/blob/main/master.db)

## Basic use

- run `python priconne_asset_extractor.py` once to download all the manifests
- Edit the filters in priconne_asset_extractor.py

```py
    # Example: to download all background assets from bg2_assetmanifest
    dm.datamine(
        manifest_filter="bg",
        assetbundle_filter="",
        file_filter="",
    )
```

For more examples see `example.py`

## TODO

- Extract from DMM install
- Story data extraction
- Make the tool more user friendly
- Add more configs
- Remove dependecies

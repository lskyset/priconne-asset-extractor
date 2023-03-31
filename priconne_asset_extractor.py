from src import Dataminer


def main():
    dm = Dataminer()

    # Running as is will download all the manifests.
    # They are just text files with file names so you can open them and adjust your filters.
    # Files ending with .unity3d are assetbundles (containing more files) which you filter with assetbundle_filter
    # Leaving filters empty will download / extract everything so make sure you have enough disk space when dealing with sound and movie files.
    dm.datamine(
        manifest_filter="",  # (empty) manifest_name
        assetbundle_filter="assetbundle_name",
        file_filter="file_name",
    )


if __name__ == "__main__":
    # keep all scripting in this scope to avoid bugs with multiprocessing
    main()

from src import Dataminer


def examples():
    # initializes the dataminer
    dm = Dataminer()

    # Extracting a whole manifest
    dm.datamine(
        manifest_filter="wac",
        assetbundle_filter="",
        file_filter="",
    )

    # Extracting images
    dm.datamine(
        manifest_filter="bg",
        assetbundle_filter=r"still_unit_1001[0-9]{2}",
        file_filter=r"still_unit_1001[0-9]{2}\.png",
    )

    # Sound and Movie manifests only contain regular files so the assetbundle filter isn't needed.
    dm.datamine(
        manifest_filter="sound",
        assetbundle_filter="",
        file_filter=r"bgm_M36\.",
    )
    dm.datamine(
        manifest_filter="sound",
        assetbundle_filter="",
        file_filter="bgm_M152",
    )
    dm.datamine(
        manifest_filter="movie",
        assetbundle_filter="",
        file_filter=r"character_1001[0-9]{2}",
    )

    def sd_skel_example():
        # 000000 files contains animations shared by all units
        dm.datamine(
            manifest_filter="spine",
            assetbundle_filter="000000",
            file_filter="cysp",
        )

        # the common cysp contain animations shared by units from the same same class (eg. sword units)
        dm.datamine(
            manifest_filter="spine",
            assetbundle_filter="common",
            file_filter="cysp",
        )

        # filters for the specific unit animations, include all uncap versions
        dm.datamine(
            manifest_filter="spine",
            assetbundle_filter=r"1001[0-9]{2}",
            file_filter=r"1001[0-9]{2}",
        )

        # assemble .cysp files into a .skel file for a given unit_id
        dm.get_skel(100111)

    sd_skel_example()


if __name__ == "__main__":
    # keep all scripting in this scope to avoid bugs with multiprocessing
    examples()

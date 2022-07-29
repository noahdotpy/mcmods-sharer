from functions import export_mods, import_mods

import argparse


def main():

    parser = argparse.ArgumentParser(
        description="Scans your specified folder for mods downloaded with the PacMC package manager and outputs all valid PacMC mods in the folder."
    )

    parser.add_argument(
        "--log",
        "-l",
        help="Log output to a file",
        nargs=1,
        metavar=("<file_path>"),
        action="store",
    )

    subparsers = parser.add_subparsers(help="commands")

    # Export command
    export_parser = subparsers.add_parser("export", help="List contents")

    export_parser.add_argument(
        "--game-version",
        "-gv",
        action="store",
        default=[""],
        nargs=1,
        metavar=("<game_version>",),
        help="Minecraft version.",
        required=True,
    )

    export_parser.add_argument(
        "--mod-loader",
        "-ml",
        action="store",
        default=[""],
        nargs=1,
        metavar=("<mod_loader>",),
        help="Minecraft mod loader.",
        required=True,
    )

    export_parser.add_argument(
        "mods_folder", help="Path to the archive you are pulling mods from."
    )

    export_parser.add_argument(
        "--file",
        "-f",
        action="store",
        default=[""],
        nargs=1,
        metavar=("<file_path>",),
        help="Write mod list to a file.",
    )

    export_parser.add_argument(
        "--copy",
        "-c",
        action="store_true",
        default=False,
        help="Copy mod list to clipboard.",
    )

    export_parser.set_defaults(func=export_mods)

    # Import command
    import_parser = subparsers.add_parser("import", help="List contents")

    import_parser.add_argument("file_path", help="File to import from (json).")

    import_parser.set_defaults(func=import_mods)

    py_args = parser.parse_args()

    py_args.func(py_args)


if __name__ == "__main__":
    main()

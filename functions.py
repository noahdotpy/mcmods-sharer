from os import listdir
from os.path import isfile, join

import json

import pyperclip

import subprocess
import platform

from sys import exit

import logging

# Logging config
FMT = "[ {levelname} ]: {message}"
FORMATS = {
    logging.DEBUG: FMT,
    logging.INFO: f"\33[36m{FMT}\33[0m",
    logging.WARNING: f"\33[33m{FMT}\33[0m",
    logging.ERROR: f"\33[31m{FMT}\33[0m",
    logging.CRITICAL: f"\33[1m\33[31m{FMT}\33[0m",
}


GITHUB_REPO = "https://github.com/noahdotpy/mcmods-sharer/"


class CustomFormatter(logging.Formatter):
    def format(self, record):
        log_fmt = FORMATS[record.levelno]
        formatter = logging.Formatter(log_fmt, style="{")
        return formatter.format(record)


handler = logging.StreamHandler()
handler.setFormatter(CustomFormatter())
logging.basicConfig(level=logging.DEBUG, handlers=[handler])

log = logging.getLogger()


class ModLoaderUnsupportedError(ValueError):
    pass


def open_browser(link, unsupported_then_show_link=False):
    user_os = platform.system()

    if user_os == "Linux":
        subprocess.run(f"xdg-open {link}", shell=True, check=True)
    elif user_os == "Windows":
        subprocess.run(f"start {link}")
    elif user_os == "Darwin":
        subprocess.run(f"open {link}", shell=True, check=True)
    else:
        log.warning("Opening sites in default browser not supported in this OS.")
        if unsupported_then_show_link:
            print(f"Link: {link}")


def export_mods(py_args):

    try:
        if py_args.mod_loader[0] not in ["fabric", "quilt", "forge"]:
            raise ModLoaderUnsupportedError
    except ModLoaderUnsupportedError:
        log.exception("Unsupported mod loader specified.")
    else:
        log.info("Mod loader supported.")

    mods = {"pacmc": {}, "manual": {}, "http_dl": {}}
    files = [
        f
        for f in listdir(py_args.archive_path)
        if isfile(join(py_args.archive_path, f))
    ]

    mods["game_version"] = py_args.game_version
    mods["mod_loader"] = py_args.mod_loader

    # Adding mods to mods dictionary
    for mod_file in files:
        # PacMC
        if mod_file.endswith(".pacmc.jar"):
            # modrinth
            if "_mr_" in mod_file:
                splitted = mod_file.split("_mr_")
                mod_repo = "modrinth"

            # curseforge
            if "_cf_" in mod_file:
                splitted = mod_file.split("_cf_")
                mod_repo = "curseforge"

            mod_slug = splitted[0]
            mods["pacmc"][mod_slug] = {
                "repo": mod_repo,
            }

        if mod_file == (".mcmods.json"):
            # Manual
            with open(f"{py_args.archive_path}/{mod_file}", "r") as f:
                mcmods_mods = json.load(f)

            for mod in mcmods_mods["manual"]:
                mods["manual"][mod] = {"link": mcmods_mods["manual"][mod]["link"]}

            # HTTP DL
            with open(f"{py_args.archive_path}/{mod_file}", "r") as f:
                mcmods_mods = json.load(f)

            for mod in mcmods_mods["http_dl"]:
                mods["http_dl"][mod] = {"link": mcmods_mods["http_dl"][mod]["link"]}

    # Render the output
    json_dump = json.dumps(mods)

    if py_args.file[0]:
        with open(py_args.file[0], "w") as out_file:
            print(json_dump, file=out_file)
            log.info("Created file at: " + py_args.file[0])

    if py_args.copy:
        pyperclip.copy(json_dump)
        log.info("Mod list copied to clipboard")


def import_mods(py_args):
    """
    Implement auto PacMC downloading (pacmc install sodium) with user choosing archive to download to
    Implement auto opening manual and HTTP_DL in browser
    cmd_syntax = {
        "linux": "xdg-open https://google.com",
        "windows": "start https://google.com",
        "macos": "open https://google.com"
    }
    """
    with open(py_args.file_path, "r") as f:
        mods = json.load(f)

    log.info(
        f"This modlist is meant to be used with {mods['mod_loader']} for {mods['game_version']}"
    )

    # PACMC
    # Installing mods with PACMC
    if len(mods["pacmc"]) > 0:
        print()
        log.info(
            f"You are about to install {len(mods['pacmc'])} mods into the default archive with pacmc..."
        )
        pacmc_install_confirm = (
            input("Are you sure you want to do this (Y/n)? ").strip().lower()
        )
        if pacmc_install_confirm in ["n", "no"]:
            log.info("Skipping section: pacmc...")
        else:
            log.info("Installing mods with pacmc...")
            subprocess.run(
                f"pacmc install {' '.join([mods['pacmc'][mod]['repo']+'/'+mod for mod in mods['pacmc']])}",
                shell=True,
                check=True,
            )
    else:
        log.info("\nNo PacMC mods, skipping...")

    # MANUAL
    if len(mods["manual"]) > 0:
        print()
        log.info(
            f"You are about to open {len(mods['manual'])} mod links in the default browser (manually download)..."
        )
        manual_install_confirm = (
            input("Are you sure you want to do this (Y/n)? ").strip().lower()
        )
        if manual_install_confirm in ["n", "no"]:
            log.info("Skipping section: manual...")
        else:
            log.info("Opening links in browser...")
            for mod in mods["manual"]:
                open_browser(
                    mods["manual"][mod]["link"], unsupported_then_show_link=True
                )
    else:
        log.info("\nNo manual install mods, skipping...")

    # HTTP_DL
    if len(mods["manual"]) > 0:
        print()
        log.info(
            f"You are about to download {len(mods['manual'])} mods from an untrusted source..."
        )
        http_dl_install_confirm = (
            input("Are you sure you trust these links (Y/n)? ").strip().lower()
        )
        if http_dl_install_confirm in ["n", "no"]:
            log.info("Skipping section: http_dl...")
        else:
            log.info("Opening download links in browser...")
            for mod in mods["http_dl"]:
                open_browser(
                    mods["http_dl"][mod]["link"], unsupported_then_show_link=True
                )
    else:
        log.info("\nNo http_dl mods, skipping...")

from os import listdir
from os.path import isfile, join

import json

import pyperclip

import subprocess
import platform

from sys import exit


def export_mods(py_args):
    mods = {"pacmc": {}, "manual": {}, "http_dl": {}}
    files = [f for f in listdir(py_args.archive_path) if isfile(
        join(py_args.archive_path, f))]

    mods["game_version"] = py_args.game_version
    mods["mod_loader"] = py_args.mod_loader

    # Adding mods to mods dictionary
    for mod_file in files:
        # PacMC
        if mod_file.endswith('.pacmc.jar'):
            # modrinth
            if '_mr_' in mod_file:
                splitted = mod_file.split('_mr_')
                mod_repo = "modrinth"

            # curseforge
            if '_cf_' in mod_file:
                splitted = mod_file.split('_cf_')
                mod_repo = "curseforge"

            mod_slug = splitted[0]
            mods["pacmc"][mod_slug] = {
                "repo": mod_repo,
            }

        if mod_file == ('.mcmods.json'):
            # Manual
            with open(f"{py_args.archive_path}/{mod_file}", 'r') as f:
                mcmods_mods = json.load(f)

            for mod in mcmods_mods["manual"]:
                mods["manual"][mod] = {
                    "link": mcmods_mods["manual"][mod]["link"]}

            # HTTP DL
            with open(f"{py_args.archive_path}/{mod_file}", 'r') as f:
                mcmods_mods = json.load(f)

            for mod in mcmods_mods["http_dl"]:
                mods["http_dl"][mod] = {
                    "link": mcmods_mods["http_dl"][mod]["link"]}

    # Render the output
    json_dump = json.dumps(mods)

    if py_args.file[0]:
        with open(py_args.file[0], 'w') as out_file:
            print(json_dump, file=out_file)
            print("INFO: Created file at: " + py_args.file[0])

    if py_args.copy:
        pyperclip.copy(json_dump)
        print("INFO: Mod list copied to clipboard!")


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
    with open(py_args.file_path, 'r') as f:
        mods = json.load(f)

    user_os = platform.system()
    
    if user_os == 'Linux':
        open_site_command = "xdg-open"
    elif user_os == 'Windows':
        open_site_command = "start"
    elif user_os == 'Darwin':
        open_site_command = "open"
    else:
        raise Exception(f"{user_os} is not currently supported.")

    print(f"WARNING: This modlist is meant to be used with {mods['mod_loader']} for {mods['game_version']}!!")
    
    # PACMC
    # Installing mods with PACMC
    if len(mods["pacmc"]) > 0:
        pacmc_install_confirm = input(
            f"\nYou are about to install {len(mods['pacmc'])} mods into the default archive with pacmc...\nAre you sure you want to do this (Y/n)? ").strip().lower()
        if pacmc_install_confirm in ["n", "no"]:
            print("Not installing mods with pacmc...")
        else:
            print("Installing mods with pacmc...")
            subprocess.run(f"pacmc install {' '.join([mods['pacmc'][mod]['repo']+'/'+mod for mod in mods['pacmc']])}",
                        shell=True, check=True)
    else:
        print("\nNo PacMC mods, skipping...")

    # MANUAL
    if len(mods["manual"]) > 0:
        manual_install_confirm = input(
            f"\nYou are about to open {len(mods['manual'])} mod links in the default browser (manually download)...\nAre you sure you want to do this (Y/n)? ").strip().lower()
        if manual_install_confirm in ["n", "no"]:
            print("Not opening links in browser...")
        else:
            print("Opening links in browser...")
            for mod in mods["manual"]:
                subprocess.run(f"{open_site_command} {mods['manual'][mod]['link']}", shell=True, check=True)
    else:
        print("\nNo manual install mods, skipping...")
    
    # HTTP_DL
    if len(mods["manual"]) > 0:
        http_dl_install_confirm = input(
            f"\nYou are about to download {len(mods['manual'])} mods from an untrusted source...\nAre you sure you trust these links (Y/n)? ").strip().lower()
        if http_dl_install_confirm in ["n", "no"]:
            print("Not opening links in browser...")
        else:
            print("Opening download links in browser...")
            for mod in mods["http_dl"]:
                subprocess.run(f"{open_site_command} {mods['http_dl'][mod]['link']}", shell=True, check=True)
    else:
        print("\nNo http_dl mods, skipping...")

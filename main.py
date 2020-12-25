from __future__ import print_function, unicode_literals

import glob
import hashlib
import argparse
import os
import inquirer

cache = {}


def md5(data):
    return hashlib.md5(data.encode("utf-8")).hexdigest()


def md5file(filename):
    return hashlib.md5(open(filename, "rb").read()).hexdigest()


def confirm(filenames):
    print(
        "Confirm to delete {} files selected above? [y/n]".format(len(filenames)), end="")
    answer = input().strip().lower()
    return answer == "" or answer.startswith("y")


def choose(choices):
    questions = [
        inquirer.Checkbox('files_to_be_deleted',
                          message="Which files you want to delete?",
                          choices=choices,
                          ),
    ]
    answers = inquirer.prompt(questions)
    return answers


def argparser_initialize():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--folder", help="folder to scan, eg: ./Download/", required=True)
    args = parser.parse_args()
    return args


def main():
    args = argparser_initialize()
    # Bug dirty fix for: https://bugs.python.org/issue39845
    folder = args.folder
    if folder.endswith('"'):
        folder = folder[:-1]
    if not folder.endswith(os.path.sep):
        folder += os.path.sep
    # Scan files in folder and calculate md5 for file content
    for filename in glob.iglob('{}**{}*'.format(folder, os.path.sep), recursive=True):
        if os.path.isfile(filename):
            key = md5file(filename)
            if not key in cache.keys():
                cache[key] = []
            cache[key].append(filename)
    deleted_files = []
    total_duplicated_file = 0
    # Detect duplicated files
    for _, v in cache.items():
        if len(v) > 1:
            # Choose files to delete
            total_duplicated_file += len(v) - 1
            result = choose(v)
            files_to_be_deleted = result['files_to_be_deleted']
            if len(files_to_be_deleted) == 0:
                continue
            # Confirm to delete
            if confirm(files_to_be_deleted):
                for filename in files_to_be_deleted:
                    # Remove files selected
                    os.remove(filename)
                    deleted_files.append(filename)
    print("{}/{} duplicate files deleted.".format(len(deleted_files),
                                                  total_duplicated_file))


if __name__ == "__main__":
    main()

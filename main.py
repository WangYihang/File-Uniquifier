from __future__ import print_function, unicode_literals

import glob
import hashlib
import argparse
import os
from whaaaaat import prompt, print_json

cache = {}

def md5(data):
    return hashlib.md5(data.encode("utf-8")).hexdigest()

def md5file(filename):
    return hashlib.md5(open(filename, "rb").read()).hexdigest()

def confirm(filenames):
    questions = [
        {
            'type': 'confirm',
            'name': 'confirm',
            'message': 'Confirm to delete files selected above?',
        }
    ]
    answers = prompt(questions)
    return answers

def choose(choices):
    c = [{"name": i} for i in choices]
    questions = [
        {
            'type': 'checkbox',
            'name': 'files_to_be_deleted',
            'message': 'Which files you want to delete?',
            'choices': c,
        }
    ]
    answers = prompt(questions)
    return answers

def argparser_initialize():
    parser = argparse.ArgumentParser() 
    parser.add_argument("--folder", help="folder to scan, eg: ./Download/")
    args = parser.parse_args()
    return args

def main():
    args = argparser_initialize()
    # Bug dirty fix for: https://bugs.python.org/issue39845
    folder = args.folder
    if folder.endswith('"'):
        folder = folder[:-1]
    if not folder.endswith('\\'):
        folder += "\\"
    # Scan files in folder and calculate md5 for file content
    for filename in glob.iglob('{}**{}*'.format(folder, os.path.sep), recursive=True):
        if os.path.isfile(filename):
            key = md5file(filename)
            if not key in cache.keys():
                cache[key] = []
            cache[key].append(filename)
    deleted_files = []
    # Detect duplicated files
    for _, v in cache.items():
        if len(v) > 1:
            # Choose files to delete
            result = choose(v)
            files_to_be_deleted = result['files_to_be_deleted']
            # Confirm to delete
            result = confirm(files_to_be_deleted)
            con = result['confirm']
            if con:
                for filename in files_to_be_deleted:
                    # Remove files selected
                    os.remove(filename)
                    deleted_files.append(filename)
    print("{} duplicate files deleted.".format(len(deleted_files)))

if __name__ == "__main__":
    main()



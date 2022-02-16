import hashlib
import argparse
import os
import inquirer
import humanize

cache = {}


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
    parser.add_argument("-f", "--folders", nargs="+", help="folder to scan, eg: ./Download/", required=True)
    parser.add_argument("-d", "--dry-run", help="scan without actually remove files", action="store_true")
    args = parser.parse_args()
    return args


def is_duplicate_filename_pattern(filename_0, filename_1):
    fname_0, ext_0 = os.path.splitext(filename_0)
    fname_1, ext_1 = os.path.splitext(filename_1)
    '''
    filename_0 = "foo.jpg"
    filename_1 = "foo(1).jpg"
    '''
    if fname_1.startswith(fname_0):
        print(1)
        r = fname_1[len(fname_0):].strip()
        if r[0] == "(" and r[-1] == ")" and (r[1:-1]).isdigit():
            return True, filename_1
    '''
    filename_0 = "foo(1).jpg"
    filename_1 = "foo.jpg"
    '''
    if fname_0.startswith(fname_1):
        r = fname_0[len(fname_1):].strip()
        if r[0] == "(" and r[-1] == ")" and (r[1:-1]).isdigit():
            return True, filename_0
    return False, None


def uniquify(folder, dry_run):
    tbd = [folder]
    space_saved = 0
    while len(tbd) != 0:
        path = tbd.pop()
        print("Scanning {}".format(path))
        with os.scandir(path) as it:
            # cluster via file size
            sizetable = {}
            for entry in it:
                pathname = entry.path
                if entry.is_dir() and pathname not in [".", ".."]:
                    tbd.append(entry.path)
                elif entry.is_file():
                    size = os.path.getsize(pathname)
                    if size not in sizetable.keys():
                        sizetable[size] = []
                    sizetable[size].append(pathname)
            for k, v in sizetable.items():
                if len(v) != 1:
                    # calculate md5 of a list of files in which the size of files are the same
                    hashtable = {}
                    for filepath in v:
                        h = md5file(filepath)
                        if h not in hashtable.keys():
                            hashtable[h] = []
                        hashtable[h].append(filepath)
                    for hk, hv in hashtable.items():
                        if len(hv) > 1:
                            print("Removing duplicated files ({}) which has md5 {}".format(humanize.naturalsize(k), hk))
                            basepath = None
                            for hvv in hv:
                                if ("(" not in hvv) and (")" not in hvv):
                                    basepath = hvv
                            if basepath != None:
                                print("{} will be safely stored".format(basepath.replace(folder, "")))
                                for hvv in hv:
                                    if hvv != basepath:
                                        print("\tremove {}".format(hvv))
                                        space_saved += os.path.getsize(hvv)
                                        if not dry_run:
                                            os.remove(hvv)
                                        print("{} saved".format(
                                            humanize.naturalsize(space_saved)))
                            print("")
    print("{} saved".format(humanize.naturalsize(space_saved)))


def main():
    # TODO: Specify common file extensions to achieve soundness
    args = argparser_initialize()
    folders = args.folders
    for folder in folders:
        uniquify(folder, args.dry_run)


if __name__ == "__main__":
    main()

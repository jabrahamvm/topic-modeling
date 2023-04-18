# Example: Crawl the files in the GitHub repo
# =====================================================
# > repo='enriquegiottonini/conferencias_matutinas_amlo'
# > tree = get_tree(repo, branch)
# > csv_files = get_csv_files(tree)
# =====================================================
# > csv_files // (1037 csv files)
# ['2023/3-2023/marzo 8, 2023/mananera_08_03_2023.csv',
#  '2023/3-2023/marzo 9, 2023/mananera_09_03_2023.csv',
#  ...]

import os

import requests


def get_tree(repo, branch):
    """Get the tree of a GitHub repo
    :param repo: str, the repo name
    :param branch: str, the branch name
    :return: dict, the tree of the repo (json)
    """
    url = f"https://api.github.com/repos/{repo}/git/trees/{branch}?recursive=1"
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    else:
        return None


def get_csv_files(tree):
    """Get the list of csv files in the GitHub repo
        which goes by the name like 'mananera'
    :param tree: dict, the tree of the repo (json)
    :return: list, the list of csv files
    """
    files = []
    for file in tree["tree"]:
        if file["path"].endswith(".csv") and "mananera" in file["path"]:
            files.append(file["path"] + "\n")
    return files


def file_crawler(repo, branch, dest="utils", log=lambda *_: None):
    """Crawl the files in the GitHub repo
    :param repo: str, the repo name
    :param branch: str, the branch name
    :return: list, the list of csv files
    """
    if not os.path.exists(dest):
        os.makedirs(dest)

    dest_file_path = os.path.join(dest, "cache_paths.txt")
    if os.path.exists(dest_file_path):
        return get_cache(dest)

    tree = get_tree(repo, branch)
    csv_files = get_csv_files(tree)

    log(csv_files)

    return csv_files


def save_cache(paths, dest="utils"):
    """Save the paths of the crawled files
    :param paths: list, the list of paths
    :param dest: str, the destination folder
    """
    dest_file_path = os.path.join(dest, "cache_paths.txt")
    with open(dest_file_path, "w") as f:
        for path in paths:
            f.write(path)


def get_cache(dest="utils"):
    """Get the paths of the crawled files, each path ends with .csv
    :param dest: str, the destination folder
    :return: list, the list of paths
    """
    dest_file_path = os.path.join(dest, "cache_paths.txt")
    paths = []
    with open(dest_file_path, "r") as f:
        for line in f:
            # remove the newline character
            line = line[:-1]
            paths.append(line)
    return paths


def clean_cache(dest="utils"):
    """Clean the cache of the crawler
    :param dest: str, the destination folder
    """
    dest_file_path = os.path.join(dest, "cache_paths.txt")
    if os.path.exists(dest_file_path):
        os.remove(dest_file_path)


def _print_all(paths):
    for path in paths:
        print(path)
    print(len(paths))


def main():
    repo = "enriquegiottonini/conferencias_matutinas_amlo"
    branch = "master"
    dest = "utils"
    csv_files = file_crawler(repo, branch, dest, save_cache)
    print(f"'{csv_files[0]}'")
    print(len(csv_files))


if __name__ == "__main__":
    main()

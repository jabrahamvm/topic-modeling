import io
import os
import shutil
import sys
from datetime import datetime, timedelta

import pandas as pd
import requests

from data_crawler import file_crawler


def noop(*_):
    pass


def fetch_data(repo, branch, dest, start_date, end_date):
    """Fetch the data (text) from the GitHub repo"""

    if os.path.exists(dest) and len(os.listdir(dest)) > 0:
        print("Data already fetched")
        return

    api_url = f"https://raw.githubusercontent.com/{repo}/master"
    paths = file_crawler(repo, branch, dest, log=noop)

    if not os.path.exists(dest):
        os.makedirs(dest)

    weeks = get_weeks(paths, start_date, end_date)
    total: int = len(weeks)
    ibar: int = 1
    for week, paths in weeks.items():
        for path in paths:
            url = f"{api_url}/{path}"
            url = url[:-1]  # get rid of the newline character
            r = requests.get(url)
            if r.status_code == 200:
                week_file = f"{week}.txt"
                week_file_path = os.path.join(dest, week_file)

                with open(week_file_path, "a") as f:
                    for line in requestProcessor(r):
                        f.write(line)
            else:
                print(f"Error: {r.status_code} {r.reason} '{url}'")
                exit(1)  # if one file fails, check the url and fix it
        progress(ibar, total, suffix=f"complete")
        ibar += 1


def processFileCsv(text):
    """Process the csv file, get the text column"""
    df = pd.read_csv(io.StringIO(text), sep=",", engine="python")
    for index, row in df.iterrows():
        yield row["Texto"] + " "


def requestProcessor(request):
    """Process the request, pipeline for another file processor"""
    text = request.text
    yield from processFileCsv(text)


def clean_data(dest):
    """Clean the documents (week files) for a fresh download"""
    if os.path.exists(dest):
        shutil.rmtree(dest)
    os.makedirs(dest)


def get_weeks(paths: list, start_date: str, end_date: str) -> dict:
    """Get the weeks from a list of paths
    :param paths: list, the list of paths
    :param start_date: str like '09-01-2020'
    :param end_date: str, the end date
    :return: dict, weeks and their paths by working days
    """
    weeks = {}
    for path in paths:
        date = file2date(get_file_name(path))
        if start_date <= date <= end_date:
            week = get_week_start(date)
            if week not in weeks:
                weeks[week] = []
            weeks[week].append(path)
    return weeks


def get_week_start(date: str) -> str:
    """Get the week start date from a date
    :param date: str, the date
    :return: str, the week start date
    """
    date = datetime.strptime(date, "%d-%m-%Y")
    week_start = date - timedelta(days=date.weekday())
    return week_start.strftime("%d-%m-%Y")


def get_file_name(path):
    """Get the file name from a path
    :param path: str, the path
    :return: str, the file name
    """
    return path.split("/")[-1]


def file2date(file_name):
    """Get the date from a file name
    :param file_name: str, the file name
    :return: datetime, the date
    """
    day, month, year = file_name.split("_")[1:]
    date = "-".join([day, month, year.split(".")[0]])
    return date


# <script src="https://gist.github.com/vladignatyev/06860ec2040cb497f0f3.js"></script>
def progress(count, total, suffix=""):
    """Print a progress bar of data fetched"""
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = "=" * filled_len + "-" * (bar_len - filled_len)

    sys.stdout.write("[%s] %s%s ...%s\r" % (bar, percents, "%", suffix))
    sys.stdout.flush()  # As suggested by Rom Ruben

"""Deletes old sessions to clear up space."""

import datetime
import os
import sys
import time


def get_files(path):
    """Returns the absolute paths of all files under a path."""
    for walk_information in os.walk("data/sessions/data/container_file/"):
        directory_name, _, file_names = walk_information
        for file_name in file_names:
            full_path = os.path.join(directory_name, file_name)
            yield full_path


def sizeof_fmt(num, suffix="B"):
    for unit in ["","Ki","Mi","Gi","Ti","Pi","Ei","Zi"]:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, "Yi", suffix)


def main():
    """Main."""
    sessions_path = "data/sessions/data/container_file/"
    days = 7
    cutoff = datetime.datetime.now() - datetime.timedelta(days=days)
    print("Calculating size of files older than {} days...".format(days))
    bytes_count = 0

    for file_path in get_files(sessions_path):
        stat = os.stat(file_path)
        if datetime.datetime.fromtimestamp(stat.st_mtime) < cutoff:
            bytes_count += stat.st_size
    print("Files older than {} days comprise {}".format(days, sizeof_fmt(bytes_count)))

    wait_seconds = 5
    print("Cleaning in {} seconds...".format(wait_seconds))
    time.sleep(wait_seconds)
    print("Cleaning")
    for file_path in get_files(sessions_path):
        stat = os.stat(file_path)
        if datetime.datetime.fromtimestamp(stat.st_mtime) < cutoff:
            os.unlink(file_path)


if __name__ == "__main__":
    if sys.version_info.major < 3:
        print("Please use Python 3")
        sys.exit(1)
    main()

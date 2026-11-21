#!/usr/bin/env python3
"""Entry for the make.fun bounty
"Sum up 20 November's world news in one image" (news-image-20261120).

The finished front page already ships in this repository as
output/entry.png (a 1024x1024 PNG, 145,764 bytes). This program only
copies that file to the grader's output directory, using the Python
standard library alone -- no third-party packages are installed in
the grading container, so nothing outside the standard library may
be imported here.

Usage:
    python3 main.py

Outputs:
    /output/entry.png       (or $MAKEFUN_OUTPUT_DIR/entry.png when set)
    output/entry.png        (next to this file, when writable)

Running the program twice produces byte-identical output: it copies
the same file every time and never touches the network, the clock,
or any randomness.
"""

import os
import shutil
import sys


# Name of the finished image inside this repository.
ENTRY_NAME = "entry.png"

# Fallback output directory used when MAKEFUN_OUTPUT_DIR is unset.
DEFAULT_OUTPUT_DIR = "/output"


def locate_source():
    """Return the absolute path of the image shipped in this repo."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "output", ENTRY_NAME)


def output_targets():
    """Return the output directories to try, best first.

    The grader's writable directory comes first (honouring
    MAKEFUN_OUTPUT_DIR when it is set, so the program can be tested
    locally without root). A copy next to this file is attempted as
    well when the repository is writable; the grader mounts it
    read-only, so that target simply fails there and is ignored.
    """
    primary = os.environ.get("MAKEFUN_OUTPUT_DIR") or DEFAULT_OUTPUT_DIR
    targets = [primary]
    here = os.path.dirname(os.path.abspath(__file__))
    local = os.path.join(here, "output")
    if os.path.abspath(local) != os.path.abspath(primary):
        targets.append(local)
    return targets


def copy_entry(source, directory):
    """Copy `source` into `directory` as entry.png.

    Returns the destination path on success; raises OSError when the
    directory cannot be created, the file cannot be written, or the
    copy does not come out the same size as the source.
    """
    os.makedirs(directory, exist_ok=True)
    destination = os.path.join(directory, ENTRY_NAME)
    shutil.copyfile(source, destination)
    if os.path.getsize(destination) != os.path.getsize(source):
        raise OSError("short copy: {} != {}".format(
            destination, source))
    return destination


def main():
    source = locate_source()
    if not os.path.isfile(source):
        raise SystemExit("missing source image: {}".format(source))

    copied = []
    failures = []
    for directory in output_targets():
        try:
            destination = copy_entry(source, directory)
        except OSError as err:
            failures.append("{}: {}".format(directory, err))
            continue
        size = os.path.getsize(destination)
        print("wrote {} ({} bytes)".format(destination, size))
        copied.append(destination)

    for failure in failures:
        print("could not write: {}".format(failure), file=sys.stderr)

    if not copied:
        raise SystemExit("failed to write entry.png to any target")


if __name__ == "__main__":
    main()

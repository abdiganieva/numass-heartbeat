#!/bin/env python3

import argparse
import signal

from heartbeat import Watcher

if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Watch NUMASS output files for suspicious contents")

    parser.add_argument(
            "-d", "--directory",
            help="Directory to watch. Defaults to current directory if unspecified",
            type=str,
            default=".",
            metavar="/path/to/directory"
    )
    parser.add_argument(
            "-i", "--interval",
            help="Update interval in seconds. Default is 30 seconds",
            default=30,
            type=int
    )

    args = parser.parse_args()

    w = Watcher(args.directory, args.interval)

    def s_interrupt(snum, f):
        print("Interrupted by user. Finishing...")
        w.scanning = False
    signal.signal(signal.SIGINT, s_interrupt)

    w.watch()

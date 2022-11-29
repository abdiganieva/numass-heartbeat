import os
import time

from .checker import *

class Watcher:
    # Default warning handler
    WARNING_DEFAULT = lambda mes : print(f"\033[37;41mWARNING\033[0m: {mes}")

    def __init__(self, directory, interval_seconds=30, warning_callback=WARNING_DEFAULT):
        self.directory = directory
        self.interval = interval_seconds
        self.warning_callback = warning_callback
        self.__files = {}
        self.scanning = False

    def watch(self):
        print(f"Start watching directory {self.directory}")

        self.scanning = True
        while self.scanning:
            self.scan_iteration()
            time.sleep(self.interval)

    def scan_iteration(self):
        print("-- Scan iteration")
        # Scan started
        newmod_files = []
        for root, dirs, files in os.walk(self.directory):
            for file in files:
                file_path = os.path.join(root, file)
                mtime = os.stat(file_path).st_mtime

                update = False
                old_status = None
                if file_path not in self.__files:
                    print(f"Have new file:    {file_path}")
                    update = True
                elif self.__files[file_path]["modified"] < mtime:
                    print(f"File modified:    {file_path}")
                    update = True
                    old_status = self.__files[file_path]["status"]

                if update:
                    new_status = check(file_path)

                    if new_status == Status.EMPTY and old_status != Status.EMPTY_CANDIDATE:
                        new_status = Status.EMPTY_CANDIDATE
                    if new_status == Status.INVALID_HEADER and old_status != Status.INVALID_HEADER_CANDIDATE:
                        new_status = Status.INVALID_HEADER_CANDIDATE
                    if new_status == Status.ACQ_STOPPED and old_status != Status.ACQ_STOPPED_CANDIDATE:
                        new_status = Status.ACQ_STOPPED_CANDIDATE
                    if new_status == Status.SUS_DATA and old_status != Status.SUS_DATA_CANDIDATE:
                        new_status = Status.SUS_DATA_CANDIDATE

                    self.__files[file_path] = { "modified": mtime, "status": new_status }
                    newmod_files.append(file_path)

        # If no new files, give a warning
        if len(newmod_files) == 0:
            self.warning_callback(f"{self.interval} seconds passed. No new or updated files detected.")

        for file_path in self.__files:
            if file_path in newmod_files: continue

            if self.__files[file_path]["status"] > 100: # A candidate, but the issue wasn't fixed!
                self.__files[file_path]["status"] -= 100 # Promote to issue!
                newmod_files.append(file_path)

        # Iterate over all files that are either new or have been modified since the last check
        for newmod_file in newmod_files:
            status = self.__files[newmod_file]["status"]

            # If check returns:
            # - OK - All good, save the state
            # - EMPTY, INVALID_HEADER, ACQ_STOPPED or SUS_DATA
            if status == Status.EMPTY:
                self.warning_callback(f"{newmod_file}: is empty")
            elif status == Status.INVALID_HEADER:
                self.warning_callback(f"{newmod_file}: could not parse file header")
            elif status == Status.ACQ_STOPPED:
                self.warning_callback(f"{newmod_file}: acquisition possibly unexpectedly stopped")
            elif status == Status.SUS_DATA:
                self.warning_callback(f"{newmod_file}: suspicious data")
            # - EMPTY_DATA - Header is correct but data size is zero. This is an error, give a warning
            #   immediately
            elif status == Status.EMPTY_DATA:
                self.warning_callback(f"{newmod_file}: data size is zero")

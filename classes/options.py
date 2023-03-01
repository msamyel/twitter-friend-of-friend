import sys


class Options:
    sourcefile_path: str = None
    is_get_usernames_only: bool = False
    is_estimate_only: bool = False

    def __init__(self):
        if len(sys.argv) < 2:
            return
        self.sourcefile_path = sys.argv[1]
        self.is_get_usernames_only = "--usernames-only" in sys.argv
        self.is_estimate_only = "--estimate-only" in sys.argv
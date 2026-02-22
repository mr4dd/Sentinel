import os
import subprocess
#import requests
import time

class journalctlHandler():
    def __init__(self):
        self.buffer = []

    def getLogs(self, n: int)-> list[str]:
        try:
            output = self._runCommand(n)
            if self._trim(output) is True:
                return self.buffer
            else:
                return []
        except ValueError as e:
            print(e)

    def _runCommand(self, n: int)->str:
        journalout = subprocess.run(["journalctl", "-n", f"{n}"], capture_output=True)
        if journalout.stderr == b'':
            return journalout.stdout.decode("utf-8")
        else:
            raise ValueError(journalout.stderr)

    def _trim(self, raw: str)->bool:
        rawList = raw.split("\n")
        if self.buffer == []:
            self.buffer = rawList
        else:
            for i in range(len(self.buffer)):
                index = len(self.buffer)-i
                if rawList[index-1] == self.buffer[index-1]:
                    rawList.pop(index-1)
            if rawList != []:
                self.buffer = rawList
                return True
            else:
                return False

class logcatHandler():
    pass

def getHandler():
    keys = os.environ.keys()
    if "ANDROID_DIR" in keys:
        return logcatHandler()
    else:
        return journalctlHandler()


def main():
    handler = getHandler()
    while True:
        v = handler.getLogs(200)
        if v:
            pass

if __name__ == "__main__":
    main()

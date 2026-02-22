import os
import subprocess
#import requests
import time
import threading

class logCollectionHandler():
    def __init__(self, logType: str):
        self.buffer = []
        self.logType = logType
        self.command = []
        self._setCommand()

    def _setCommand(self):
        if self.logType == "android":
            self.command = ["logcat", "-t"]
        elif self.logType == "gnu":
            self.command = ["journalctl", "-n"]

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
        journalout = subprocess.run([self.command[0], self.command[1], f"{n}"], capture_output=True)
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

class systemMonitor():
    def __init__(self):
        pass

    def stat(self):
        metrics = []
        processes = os.listdir("/proc/")
        for process in processes:
            try:
                with open(os.path.join("/proc",process, "stat"), "r") as fd:
                    data = fd.read()
                    metrics.append(data)
            except OSError as e:
                continue
        return metrics

def getHandler():
    keys = os.environ.keys()
    if "ANDROID_DIR" in keys:
        return "android"
    else:
        return "gnu" 

def main():
    handler = logCollectionHandler(getHandler())
    print(systemMonitor().stat())
    exit()
    while True:
        v = handler.getLogs(200)
        if v:
            pass

if __name__ == "__main__":
    main()

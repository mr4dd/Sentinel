import os
import subprocess
import requests
import time
import threading
from scapy.all import AsyncSniffer, Packet
import json
from queue import Queue
from uuid import uuid1
import argparse

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
        self.packets = []
        self.sniffer = AsyncSniffer(prn=self._packet_callback, store=False)
        self.sniffer.start()

    def getPackets(self)->list[str]:
        packets = self.packets
        self.packets = []
        return packets

    def stat(self)->list[str]:
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

    def _packet_callback(self, packet: Packet):
        self.packets.append(packet.json())
    
    def destroy():
        self.sniffer.stop()

class transportHandler():
    def __init__(self, server: str, log: str='', stats:str='', pcap: str=''):
        self.BackLog = Queue()
        self.server = server
        self.logEndpoint = log
        self.statEndpoint = stats
        self.pcapEndpoint = pcap
        self.id = self.getClientID()

    def post(self, data: str, dataType: str):
        endpointMap = {"log":self.logEndpoint, "stat":self.statEndpoint, "pcap": self.pcapEndpoint}
        endpoint = endpointMap.get(dataType)
        if not endpoint:
            raise Exception("invalid data type")
        try:
            payload = self._buildPayload(data)
            requests.post(f'{server}/{endpoint}', json=payload)
        except requests.exceptions.RequestException as e:
            self.Backlog.put({dataType:data})

    def _buildPayload(self, data: str|list[str])->dict:
        return {"client_id": self.id, "content": data}
    
    def getClientID(self)->str:
        config_path = os.path.join(os.getenv("HOME"), ".config")
        config_file = os.path.join(config_path, "sentinel_client.conf")
        print(config_file)
        # check if file exists and if not create itt
        def _createNewUUID():
            uuid = uuid1().__str__()
            with open(config_file, "w") as cfd:
                cfd.write(f"UUID:{uuid}")
            return uuid

        if not os.path.exists(config_path):
            os.makedirs(config_path)
            return _createNewUUID()
        elif not os.path.exists(config_file):
            return _createNewUUID()
        else:
            with open(config_file, "r") as cfd:
                config = cfd.read()
                uuid = config.split("\n")[0].split(":")[1]
                return uuid

def getHandlerType():
    keys = os.environ.keys()
    if "ANDROID_DIR" in keys:
        return "android"
    else:
        return "gnu" 

def collectLogs(transport: transportHandler):
    handler = logCollectionHandler(getHandlerType())
    while True:
        v = handler.getLogs(200)
        if v:
            logsJson = json.dumps(v)

def monitorSystem(transport: transportHandler):
    monitor = systemMonitor()
    while True:
        s = monitor.stat()
        p = monitor.getPackets()
        if s:
            statJson = json.dumps(s)
        if p:
            pcapJson = json.dumps(p)
            
def main(remote: str, log: str, stat: str, pcap: str):
    transport = transportHandler(remote, log, stat, pcap)
    logThread = threading.Thread(target=collectLogs, args=(transport,))
    systemMonitorThread = threading.Thread(target=monitorSystem, args=(transport,))
    try:
        logThread.start()
        systemMonitorThread.start()
        logThread.join()
        systemMonitorThread.join()
    except KeyboardInterrupt:
        print("keyboard interrupt recieved, shutting down")
        exit()
        # i need to gracefully handle shutdown so data already in thread isnt lost and any connections that are active get closed
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("remote", help="ip address or domain name of the logging server")
    parser.add_argument("log", help="the endpoint for the logs")
    parser.add_argument("stat", help="the endpoint for system metrics")
    parser.add_argument("pcap", help="the endpoint for network capture")
    args = parser.parse_args()

    main(args.remote, args.log, args.stat, args.pcap)

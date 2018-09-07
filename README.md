# omega-iseries-pid-server

This is a telnet server for a computer preferrably running linux, written in python.
The hardware for this PID telnet server comprises of

- Omega PID controller from iSeries, e.g., CNI3244-C24, which was used in development
and testing of the python code

- PC or Raspberry Pi with python-2.

- Serial-to-USB cable that connects the Omega PID to the computer.

- Hot plate that is rewired so that instead of thermostatic switch it is
controlled by a solid state relay, which in turn is controlled by the Omega PID.

- Thermocouple of proper type. If you know hot plates and PID controllers then you
know what I mean.


The server comprise of two files,

- liblab_pid_omega_cni.py , the library for control of the Omega PID over a serial
port

- server.py , executable that loads the library and starts a telnet server on the computer.
# omega-iseries-pid-server

This is a telnet server for a computer preferrably running linux, written in python.
The hardware for this PID telnet server comprises of

- Omega PID controller from iSeries, e.g., CNI3244-C24, which was used in development
and testing of the python code

- PC or Raspberry Pi with python-2. Any linux should do out of the box, with minimal python
post-installation required (only pyserial, to my humble knowledge)

- Serial-to-USB cable that connects the Omega PID to the computer.

- Hot plate that is rewired so that instead of thermostatic switch it is
controlled by a solid state relay, which in turn is controlled by the Omega PID.

- Thermocouple of proper type. If you know hot plates and PID controllers then you
know what I mean.


The server comprise of two files,

- *liblab_pid_omega_cni.py* , the library for control of the Omega PID over a serial
port

- *server.py* , executable that loads the library and starts a telnet server on the computer.


Before the server is started the following needs to be configured:

1. Know the serial number of your serial-to-USB cable. This was verified to work under
linux debian and opensuse. Last checked Windoze version was 7. No guarantee is made that it
still works under Windoze.
The serial number needs to be inserted in *server.py*, line 17 as PID_SN

2. Omega PID serial port communication parameters need to be configured by hand.
This is in file *liblab_pid_omega_cni.py* in line 8 as BAUD




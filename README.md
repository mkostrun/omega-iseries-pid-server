# omega-iseries-pid-server

This provides a computer controlled PID controller controling a hot plate.
It is a telnet server for a computer preferrably running linux, written in python.
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
The serial number needs to be inserted in *server.py*, line 17 as PID_SN.
The file *server.py* has a piece of code that search the serial devices by their
serial number and returns their handle /dev/tty...

2. Omega PID serial port communication parameters need to be configured by hand.
This is in file *liblab_pid_omega_cni.py* in line 8 as BAUD.


Once the server is up and running on localhost on default port 51234, just telnet
to it.
The following is the list of supported commands, that should be typed without spaces.

- *alarm=0,1* - disable/enable alarm

- *standby* - enter standby mode (front panel start to blink 'stby').
The manual (see doc directory) requires user to enter standby every time configuration
of the device changes.

- *run* - enter run mode.

- *val* - report current thermocouple reading.

The following commands can be used to set values or to query existing values.
If the key word is written without '=val' part then it returns current value.
E.g., typing 'timepid' and pressing enter will report current status of the
configuration bits 'timepid' (it appears in OUT1CFG and OUT2CFG, and this sets both
to the same):

- *timepid=0,1* - set configuration bit to enable/disable time proportional PID.

- *full_id* - set 4 digit password that users will have to input to get the access to
the features of the PID controller.

- *sp_id* - set 4 digit password that users will have to input to change the set point
of the PID controller (the temperature that the hot plate should reach).

- *direct=0,1* - set revers (0) or direct (1) type of control for the PID controlled
device. The reverse devices are, e.g., hot plates. The direct devices are, e.g., chillers.

- *autotune* 1






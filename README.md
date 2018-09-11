# omega-iseries-pid-server

This software allows a computer to controll an Omega PID controller iSeries to
control a hot plate.
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


In the installation directory type
```
python server.py
```
to start the telnet server.
Once the server is up and running on localhost on default port 51234, just telnet
to it.

- sending a message prepended by '#' causes the message to be posted in the server
log file called *stove-${hostname}-${pid serial number}.log*.
The messages are posted to log file without '#' character.

The following is the list of supported commands, that should be typed without spaces.

- *alarm=0,1* - disable/enable alarm

- *standby* - enter standby mode (front panel start to blink 'stby').
The manual (see doc directory) requires user to enter standby every time configuration
of the device changes.

- *run* - enter run mode.

- *val* - report current thermocouple reading.

- *restart* - just like its name says.

The following commands can be used to set values or to query existing values.
If the key word is written without '=val' part then it returns current value.
E.g., typing 'timepid' and pressing enter will report current status of the
configuration bits 'timepid' (it appears in OUT1CFG and OUT2CFG, and this sets both
to the same). If the value is set, then the server responds with 'OK'.
The values are always written to RAM (unless they refer to registers, in which case
they are written to EEPROM). To transfer RAM value to EEPROM, user has to use
command *store* 'keyword'.

- *timepid=0,1* - set configuration bit to enable/disable time proportional,
 that is, P in PID.

- *full_id=0000* - set 4 digit password that users will have to input to get the access to
the features of the PID controller.

- *sp_id=0000* - set 4 digit password that users will have to input to change the set point
of the PID controller (the temperature that the hot plate should reach).

- *direct=0,1* - set reverse (0) or direct (1) type of control for the PID controlled
device. The reverse devices are, e.g., hot plates. The direct devices are, e.g., chillers.

- *autotune=0,1* - reques auto tuning of the PID controller, see below for details.

- *anitwindup=0,1* - enable/disable anti-wind-up (integral), that is 'I' in PID.

- *damping=0:7* - set/query damping in the PID control loop.

- *cycle,cycle1,cycle2=0:199* - set/query cycle time (under 7 for SSR controlled hot plates, greater value
for bigger devices). The commands *cycle* and *cycle1* both pertain to control of OUTPUT1.

- *band,band1,band2=0:9999* - set/query proportional band parameter for OUTPUT1 and OUTPUT2.

- *raset,reset1,reset2=0:3999* - set/query reset parameter for OUTPUT1 and OUTPUT2.

- *rate,rate1,rate2=0:3999* - set/query rate parameter for OUTPUT1 and OUTPUT2.

- *sp1,sp2=nnnn.n* - set/query the set point 1 (OUTPUT1) and 2 (OUTPUT2).

The following commands are not really supported by the PID controller, or so
the application engineers claim

- *ramp=0,1* - query/set ramp feature.

- *ramptime=hr,min* - query/set ramp time to that many hours and minutes.

- *soak=0,1* - query/set soak feature.

- *soaktime=hr,min* - set/query soak time in hours and minutes.

## Examples

### Data Logger

The telnet server creates a log file in the same directory in which
all the messages created by the server operation are posted.
Each message is prepended by the time stamp.
These messages comprise of three groups:

- WARNING: messages about progress of the software and some transactions.

- ERROR: error messages when some commands have failed.

- DEBUG: all received communication by the server including commands and their parametes.

- INFO: every 5 seconds the server writes to the log what was the temperature of the hot plate.
Consider a snippet from a logfile
```
2018-09-05T09:16:08-0400 WARNING  Server socket created
2018-09-05T09:16:08-0400 WARNING  Server socket bind complete
2018-09-05T09:16:08-0400 WARNING  Server listening on port 51235
2018-09-05T09:16:12-0400 WARNING  Connected with 11.12.13.14:48288
2018-09-05T09:16:15-0400 DEBUG    standby
2018-09-05T09:16:19-0400 INFO     20.9 C
2018-09-05T09:16:25-0400 INFO     21.3 C
2018-09-05T09:16:26-0400 DEBUG    soak=1
2018-09-05T09:16:31-0400 INFO     20.9 C
2018-09-05T09:16:31-0400 DEBUG    ramp=1
2018-09-05T09:16:37-0400 INFO     21.0 C
2018-09-05T09:16:41-0400 DEBUG    soaktime=[1,20]
2018-09-05T09:16:44-0400 INFO     20.7 C
2018-09-05T09:16:50-0400 INFO     21.3 C
2018-09-05T09:16:56-0400 INFO     20.8 C
2018-09-05T09:16:56-0400 DEBUG    ramptime=[0,30]
2018-09-05T09:17:01-0400 INFO     20.9 C
2018-09-05T09:17:02-0400 DEBUG    soaktime=[0,30]
2018-09-05T09:17:08-0400 INFO     21.2 C
2018-09-05T09:17:08-0400 DEBUG    sp1=30
2018-09-05T09:17:14-0400 INFO     21.2 C
2018-09-05T09:17:20-0400 INFO     20.8 C
2018-09-05T09:17:20-0400 DEBUG    sp2=60
```

### Set Hot Plate to a Temperature 101.3 deg C
```
sp1=101.3
```
Go have coffee (or perhaps, cofefe?)

### Make PID controller auto-tune at a Temperature 101.3 deg C

Disable not needed parameters using commands above.

```
restart
standby
autotune=1
OK
autopid=1
OK
sp1=101.3
OK
store sp1
sp1=101.3 stored
restart
```

Upon exiting the restart the controller enters auto-tune, and stays there until
it figures out the values of the parameters.

User can query progress of auto-tuning by issuing

```
autotune
1
```

When this returns '0' the PID controller has completed auto-tune and the
values of the PID parameters are stored in RAM. To transfer them to
EEPROM issue
```
store reset
reset=nnnn stored
store band
band=mmmm stored
store rate
rate=uuuu stored
```

And that is it.

![image1](https://github.com/mkostrun/omega-iseries-pid-server/blob/master/rlabplus/hotplate-stove-pid.png?raw=true)

The figure shows difference in hot plate temperature for
well tuned vs. poorly tuned PID controller.

### Ramp and Soak Hot Plate from 30 deg C to 60 deg C at 1 deg C/min

#### Take 1 - Telnet client direct control

See rlab code in directory rlabplus.
It establishes a connection to hot plate telnet server and
every so often issues a new set point command so that the
target temperature is reached at the desired rate.

#### Take 2 - Using built-in ramp/soak functionality

In theory the PID controller could ramp the hot plate to set point 1 (previously
set with *sp1=nnnn.n*) 
in amount of time given in *ramptime*, and then maintain the hot plate
temperature at that value for duration of *soaktime*.
Afterwards it would turn-off the hot plate allowing its temperature to drop to
room temperature.

Assuming you have tuned your PID controller at some point,
and these values are *store*d in EEPROM, this is how the story is translated
to commands to the server:
```
sp1=30
```
Now wait for hot plate to reach that temperature.

Once there, go with this
```
standby
soaktime=0,30
OK
ramptime=0,30
OK
soak=1
OK
ramp=1
OK
sp1=60
OK
store sp1
sp1=60.0 stored
restart
```

When PID controller completes the restart, it will first flash the target
value of *sp1* then switch to displaying current thermocouple reading
where the blinking character 'O' (or '0', can't tell) will be prepended.

The user may query progress of the ramp or soak by issuing, e.g., 
```
ramp
1
```
Once *ramp*ing is completed this returns *0*.
Also, upon completion of ramping the blinking '0' dissappears, as well.

Querying the progress of *soak* is done the same way.

Upon completion of soak the PID enters *standby* state,
in which *ramp=1* and *soak=1* again, but the hot plate is turned off.
As there is no internal register that allows the state of the
PID controller to be accessed remotely, one way of figuring out
that the system is in *standby* post *ramp* and *soak* could be;
```
ramp
1
soak
1
sp1
'should report soak temperature'
val
'should report some lower temperature as the stove cools down after being turned off'
```

At this time it is neccessary to turn-off *ramp* and *soak*
and re-set the set point 1 to (the value I prefer of) 22.0 C:
```
ramp=0
OK
soak=0
OK
sp1=22
OK
store sp1
sp1=22.0 stored
restart
```

If *soak* and *ramp* are not set to 0 before *restart*,
the PID controller will report error, and will not proceed with executions of commands.


![image2](https://github.com/mkostrun/omega-iseries-pid-server/blob/master/rlabplus/hotplate-resistor-pid2.png?raw=true)

The figure compares two ways of ramp and soak, one by using built in functionality
and the other via a telnet client that regularly changes *sp1*.
While telnet client allows for better control of starting point (after the controller is
put in *standby* mode OUTPUT1 is no longer active and its temperature may start to drop),
the built-in function may be better in case of crash of the telnet server.
In the former case the ramp/soak of the PID would not be affected,
while in the latter the PID would end up being stuck on the last sp1 command
it received from the client (and possibly burn down the lab, because at that particular
sp1 the stove should not be left for too long unattanded).
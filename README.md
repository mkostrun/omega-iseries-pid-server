# omega-iseries-pid-server

## But First

THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESSED OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
THE REGENTS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.

## About

This software allows a computer to controll an Omega PID controller iSeries to
control a hot plate.

The hot plate is involved, thus disclaimer above. I repeat ...

*Don't do it. Failed or improperly configured PID controllers operating high
temperature stoves, furnaces and burners are known to have caused significant
if not total damage to people's property.
Even though you are so smart (that you are consulting github pages on how to heat
up the things) this could happen to you.
So, don't do it! Go away! Delete stored bookmark to this page and never come back!*

This being said,
it is a telnet server for a computer preferrably running linux, written in python.
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

Note: In theory the PID controller could ramp the hot plate to set point 1 (previously
set with *sp1=nnnn.n*)
in amount of time given in *ramptime*, and then maintain the hot plate
temperature at that value for duration of *soaktime*.
Afterwards it would turn-off the hot plate allowing its temperature to drop to
room temperature.


## Examples

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

### Ramp and Soak Hot Plate from 30 deg C to 60 deg C

See rlab code in directory rlabplus.
It establishes a connection to hot plate telnet server and
every so often issues a new set point command so that the
target temperature is reached at the desired rate.

For well tuned PID controller, the ramp rate is
achieavable within 1% error, and so is the target temperature.

For poorly tuned PID controller, well...
see illustration in the directory.





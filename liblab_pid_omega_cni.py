import serial
import serial.tools.list_ports as slp
import sys
import array
from   time import sleep
from   numpy import *

BAUD = 9600
TIMEOUT = 1.0
PARITY = serial.PARITY_NONE
EOL = '\r'
REC_CHAR = "*"
READ_CMD = "R"
GET_CMD = "G"
ENABLE_CMD = "E"
DISABLE_CMD = "D"
WRITE_CMD = "W"
PUT_CMD = "P"
ECHO = 1

#
# Configuration registers
#
OUT1CNG_AUTOTUNE      = 32
OUT1CNG_ANTI_WIND_UP  = 16
OUT1CNG_AUTOPID       = 4
OUT1CNG_DIRECT        = 2
OUT1CNG_TIME_PROP_PID = 1
#
OUT2CNG_DAMPING = 32
OUT2CNG_SOAK    = 16
OUT2CNG_RAMP    = 8
OUT2CNG_AUTOPID = 4
OUT2CNG_DIRECT  = 2
OUT2CNG_TIME_PROP_PID = 1
#
MISC_SP_DEV   = 128
MISC_SELF     = 16
MISC_FULL_ID  = 8
MISC_SP_ID    = 4

# provided serial number of device as a string
# find which port this device is attached to
# if None there is no such device
def find_port_from_sn(sernum=None):
  mds = slp.comports() # danger: in windoze this is list generator, in linux it is list
  for md in mds:
    if 'linux' in sys.platform:
      # linux: extract vid,pid,sn,port
      port = md[0] # port
      feat = md[2] # features
      if 'n/a' in feat:
        continue
      if 'USB' not in feat:
        continue
      a = feat.split(" ")
      vid,pid = a[1].split("=")[1].split(":")
      sn = a[2].split("=")[1]
    else:
      if 'PCI' in md[2]: # system ports that we don't know about
        continue
      # windoze processing: extract sn,port
      port = md[0]
      a = md[2].split("\\")[1]
      sn  = a.split("+")[2]
    if sernum.upper() in sn.upper(): # danger: windoze attaches A to serial numbers of devices
      return port
  return None

class omega_pid:
  def __init__ (self, sernum=None, port=None):
    if (sernum is None) and (port is None):
      sys.exit(2)
    if port is None:
      port = find_port_from_sn(sernum)
    if port is None:
      sys.exit(2)
    self.device = port
    self.serial = serial.Serial(port, BAUD, \
    timeout=TIMEOUT, parity=PARITY, stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS)
    self.read   = self.serial.read
    self.write  = self.serial.write
    self.readline = self.serial.readline
    self.state = None
    sleep(2)

  def restart(self):
    self.write(REC_CHAR + 'Z02' + EOL)
    return 0

  def val(self):
    self.readline() # clean serial buffer
    # momentary temperature of the thermocouple
    cmd='X01'
    self.write(REC_CHAR + cmd + EOL)
    reply = self.readline()
    if (len(reply)>1):
      if (cmd in reply):
        rval = float(reply[3:-1])
      else:
        rval = float(reply[:-1])
    else:
      rval = None
    return rval

  def misccnf(self,sp_dev=None,enable_self=None,full_id=None,sp_id=None):
    self.readline() # clean serial buffer
    # configuration register
    global MISC_SP_DEV,MISC_SELF,MISC_FULL_ID,MISC_SP_ID
    cmd='24'
    self.write(REC_CHAR + READ_CMD + cmd + EOL)
    reply = self.readline()
    if (len(reply)>1):
      if (READ_CMD+cmd in reply):
        rval = int(reply[3:-1],16)
      else:
        rval = int(reply[:-1],16)
      rval_new = rval
      if (sp_dev is not None):
        e1 = int(rval_new/MISC_SP_DEV) % 2
        if ((sp_dev == 1) and (e1==0)):
          rval_new += MISC_SP_DEV
        if ((sp_dev == 0) and (e1==1)):
          rval_new -= MISC_SP_DEV
      if (enable_self is not None):
        e1 = int(rval_new/MISC_SELF) % 2
        if ((enable_self == 1) and (e1==0)):
          rval_new += MISC_SELF
        if ((enable_self == 0) and (e1==1)):
          rval_new -= MISC_SELF
      if (full_id is not None):
        e1 = int(rval_new/MISC_FULL_ID) % 2
        if ((full_id == 1) and (e1==0)):
          rval_new += MISC_FULL_ID
        if ((full_id == 0) and (e1==1)):
          rval_new -= MISC_FULL_ID
      if (sp_id is not None):
        e1 = int(rval_new/MISC_SP_ID) % 2
        if ((sp_id == 1) and (e1==0)):
          rval_new += MISC_SP_ID
        if ((sp_id == 0) and (e1==1)):
          rval_new -= MISC_SP_ID
      if (rval_new != rval):
        rval='{:02X}'.format(int(rval_new))
        self.write(REC_CHAR + WRITE_CMD +  cmd + rval + EOL)
    else:
      rval = None
    return rval

  def out1cnf(self,enable_autotune=None,anti_wind_up=None,enable_autopid=None,enable_direct=None,
    time_prop=None):
    self.readline() # clean serial buffer
    # configuration register
    global OUT1CNG_AUTOTUNE,OUT1CNG_ANTI_WIND_UP,OUT1CNG_AUTOPID,OUT1CNG_DIRECT,OUT1CNG_TIME_PROP_PID
    cmd='0C'
    self.write(REC_CHAR + READ_CMD + cmd + EOL)
    reply = self.readline()
    if (len(reply)>1):
      if (cmd in reply):
        rval = int(reply[3:-1],16)
      else:
        rval = int(reply[:-1],16)
      rval_new = rval
      if (enable_autotune is not None):
        e1 = int(rval_new/OUT1CNG_AUTOTUNE) % 2
        #print 'out2cnf:',enable_soak,e1
        if ((enable_autotune == 1) and (e1==0)):
          rval_new += OUT1CNG_AUTOTUNE
        if ((enable_autotune == 0) and (e1==1)):
          rval_new -= OUT1CNG_AUTOTUNE
      if (anti_wind_up is not None):
        e1 = int(rval_new/OUT1CNG_ANTI_WIND_UP) % 2
        #print 'out2cnf:',enable_ramp,e1
        if ((anti_wind_up == 1) and (e1==0)):
          rval_new += OUT1CNG_ANTI_WIND_UP
        if ((anti_wind_up == 0) and (e1==1)):
          rval_new -= OUT1CNG_ANTI_WIND_UP
      if (enable_autopid is not None):
        e1 = int(rval_new/OUT1CNG_AUTOPID) % 2
        if ((enable_autopid == 1) and (e1==0)):
          rval_new += OUT1CNG_AUTOPID
        if ((enable_autopid == 0) and (e1==1)):
          rval_new -= OUT1CNG_AUTOPID
      if (enable_direct is not None):
        e1 = int(rval_new/OUT1CNG_DIRECT) % 2
        if ((enable_direct == 1) and (e1==0)):
          rval_new += OUT1CNG_DIRECT
        if ((enable_direct == 0) and (e1==1)):
          rval_new -= OUT1CNG_DIRECT
      if (time_prop is not None):
        e1 = int(rval_new/OUT1CNG_TIME_PROP_PID) % 2
        if ((time_prop == 1) and (e1==0)):
          rval_new += OUT1CNG_TIME_PROP_PID
        if ((time_prop == 0) and (e1==1)):
          rval_new -= OUT1CNG_TIME_PROP_PID
      if (rval_new != rval):
        rval='{:02X}'.format(int(rval_new))
        self.write(REC_CHAR + WRITE_CMD +  cmd + rval + EOL)
    else:
      rval = None
    return rval

  def out2cnf(self,enable_soak=None,enable_ramp=None,enable_autopid=None,enable_direct=None,
    time_prop=None,damping=None):
    self.readline() # clean serial buffer
    # configuration register
    global OUT2CNG_SOAK,OUT2CNG_RAMP,OUT2CNG_AUTOPID,OUT2CNG_DIRECT,OUT2CNG_TIME_PROP_PID
    cmd='0D'
    self.write(REC_CHAR + READ_CMD + cmd + EOL)
    reply = self.readline()
    if (len(reply)>1):
      if (READ_CMD+cmd in reply):
        rval = int(reply[3:-1],16)
      else:
        rval = int(reply[:-1],16)
      rval_new = rval
      if (enable_soak is not None):
        e1 = int(rval_new/OUT2CNG_SOAK) % 2
        #print 'out2cnf:',enable_soak,e1
        if ((enable_soak == 1) and (e1==0)):
          rval_new += OUT2CNG_SOAK
        if ((enable_soak == 0) and (e1==1)):
          rval_new -= OUT2CNG_SOAK
      if (enable_ramp is not None):
        e1 = int(rval_new/OUT2CNG_RAMP) % 2
        #print 'out2cnf:',enable_ramp,e1
        if ((enable_ramp == 1) and (e1==0)):
          rval_new += OUT2CNG_RAMP
        if ((enable_ramp == 0) and (e1==1)):
          rval_new -= OUT2CNG_RAMP
      if (enable_autopid is not None):
        e1 = int(rval_new/OUT2CNG_AUTOPID) % 2
        if ((enable_autopid == 1) and (e1==0)):
          rval_new += OUT2CNG_AUTOPID
        if ((enable_autopid == 0) and (e1==1)):
          rval_new -= OUT2CNG_AUTOPID
      if (enable_direct is not None):
        e1 = int(rval_new/OUT2CNG_DIRECT) % 2
        if ((enable_direct == 1) and (e1==0)):
          rval_new += OUT2CNG_DIRECT
        if ((enable_direct == 0) and (e1==1)):
          rval_new -= OUT2CNG_DIRECT
      if (time_prop is not None):
        e1 = int(rval_new/OUT2CNG_TIME_PROP_PID) % 2
        if ((time_prop == 1) and (e1==0)):
          rval_new += OUT2CNG_TIME_PROP_PID
        if ((time_prop == 0) and (e1==1)):
          rval_new -= OUT2CNG_TIME_PROP_PID
      if (damping is not None):
        d = damping % 8
        e1 = int(rval_new/OUT2CNG_DAMPING) % 8
        if (d != e1):
          rval_new -= e1 * OUT2CNG_DAMPING
          rval_new += d  * OUT2CNG_DAMPING
      if (rval_new != rval):
        rval='{:02X}'.format(int(rval_new))
        self.write(REC_CHAR + WRITE_CMD +  cmd + rval + EOL)
    else:
      rval = None
    return rval

  def sp(self,val=None,save=None,index=1):
    # set point 1
    #   temperature to which the stove should be at
    self.readline()
    if (index==1):
      cmd='01'
    else:
      cmd='02'
    if val is None:
      self.write(REC_CHAR + GET_CMD +  cmd + EOL)
      reply = self.readline()
      if (len(reply)>1):
        if (GET_CMD+cmd in reply):
          reply = reply[3:-1]
        else:
          reply = reply[:-1]
        val = int(reply,16)
        d = int(val / 1048576)%8 - 1
        val = val - (d+1) * 1048576
        val = float(val) / 10.0**float(d)
    else:
      rval='{:06X}'.format(int(val)*10+1048576*2)
      if (save is None):
        self.write(REC_CHAR + PUT_CMD +  cmd + rval + EOL)
      else:
        self.write(REC_CHAR + WRITE_CMD +  cmd + rval + EOL)
    return float(val)

  def standby(self,status=1):
    cmd='03'
    if (status==1):
      self.write(REC_CHAR + DISABLE_CMD +  cmd + EOL)
    else:
      self.write(REC_CHAR + ENABLE_CMD +  cmd + EOL)
    return (status==1)

  def alarm(self,status=1,index=1):
    if (index==1):
      cmd='01'
    else:
      cmd='02'
    if (status!=1):
      self.write(REC_CHAR + DISABLE_CMD +  cmd + EOL)
    else:
      self.write(REC_CHAR + ENABLE_CMD +  cmd + EOL)
    return (status==1)

  def ramptime(self,val=None):
    self.readline()
    cmd='0E'
    if val is None:
      self.write(REC_CHAR + READ_CMD + cmd + EOL)
      reply = self.readline()
      if (len(reply)>1):
        if (reply[0] != '?'):
          if (READ_CMD+cmd in reply):
            reply = reply[3:-1]
          else:
            reply = reply[:-1]
          val = int(reply,16)
          hr  = int(val/100)
          mi  = val%100
          val = [hr,mi]
    else:
      if (len(val)>1):
        while (val[1] >= 60):
          val[0] += 1
          val[1] -= 60
        rval='{:04X}'.format(int(val[0]*100+val[1]))
        self.write(REC_CHAR + WRITE_CMD + cmd + rval + EOL)
    return val

  def soaktime(self,val=None,save=None):
    self.readline()
    cmd='1E'
    if val is None:
      self.write(REC_CHAR + READ_CMD + cmd + EOL)
      reply = self.readline()
      if (len(reply)>1):
        if ('R'+cmd in reply):
          reply = reply[3:-1]
        else:
          reply = reply[:-1]
        val = int(reply,16)
        hr  = int(val/100)
        mi  = val%100
        val = [hr,mi]
    else:
      if (len(val)==2):
        while (val[1] >= 60):
          val[0] += 1
          val[1] -= 60
        rval='{:04X}'.format(int(val[0]*100+val[1]))
        self.write(REC_CHAR + WRITE_CMD + cmd + rval + EOL)
    return val

  def cycle(self,val=None,save=None,index=1):
    self.readline()
    if (index==1):
      cmd='1A'
    else:
      cmd='1D'
    if val is None:
      self.write(REC_CHAR + GET_CMD +  cmd + EOL)
      reply = self.readline()
      if (len(reply)>1):
        if (GET_CMD+cmd in reply):
          val = int(reply[3:-1],16)
        else:
          val = int(reply[:-1],16)
    else:
      if (val>=0 and val<=199):
        rval='{:02X}'.format(int(val))
        if (save is None):
          print
          self.write(REC_CHAR + PUT_CMD + cmd + rval + EOL)
        else:
          self.write(REC_CHAR + WRITE_CMD + cmd + rval + EOL)
    return val

  def band(self,val=None,save=None,index=1):
    self.readline()
    if (index==1):
      cmd='17'
    else:
      cmd='1C'
    if val is None:
      self.write(REC_CHAR + GET_CMD +  cmd + EOL)
      reply = self.readline()
      if (len(reply)>1):
        if ('G'+cmd in reply):
          val = int(reply[3:-1],16)
        else:
          val = int(reply[:-1],16)
    else:
      if (val>=0 and val<=9999):
        rval='{:04X}'.format(int(val))
        if (save is None):
          self.write(REC_CHAR + PUT_CMD + cmd + rval + EOL)
        else:
          self.write(REC_CHAR + WRITE_CMD + cmd + rval + EOL)
    return val

  def reset(self,val=None,save=None):
    self.readline()
    cmd='18'
    if val is None:
      self.write(REC_CHAR + GET_CMD +  cmd + EOL)
      reply = self.readline()
      if (len(reply)>1):
        if (GET_CMD+cmd in reply):
          val = int(reply[3:-1],16)
        else:
          val = int(reply[:-1],16)
      else:
        val = -1
    else:
      if (val>=0 and val<=3999):
        rval='{:04X}'.format(int(val))
        if (save is None):
          self.write(REC_CHAR + PUT_CMD + cmd + rval + EOL)
        else:
          self.write(REC_CHAR + WRITE_CMD + cmd + rval + EOL)
    return val

  def rate(self,val=None,save=None):
    self.readline()
    cmd='19'
    if val is None:
      self.write(REC_CHAR + GET_CMD +  cmd + EOL)
      reply = self.readline()
      if (len(reply)>1):
        if ('G'+cmd in reply):
          val = int(reply[3:-1],16)
        else:
          val = int(reply[:-1],16)
      else:
        val = -1
    else:
      if (val>=0 and val<=3999):
        rval='{:04X}'.format(int(val))
        if (save is None):
          self.write(REC_CHAR + PUT_CMD + cmd + rval + EOL)
        else:
          self.write(REC_CHAR + WRITE_CMD + cmd + rval + EOL)
    return val

  def id(self,val=None):
    self.readline()
    cmd='05'
    if val is None:
      self.write(REC_CHAR + READ_CMD +  cmd + EOL)
      reply = self.readline()
      if (len(reply)>1):
        if (READ_CMD+cmd in reply):
          val = int(reply[3:-1],16)
        else:
          val = int(reply[:-1],16)
      else:
        val = 0
    else:
      if (val>=0 and val<=9999):
        rval='{:04X}'.format(int(val))
        self.write(REC_CHAR + PUT_CMD + cmd + rval + EOL)
    return val


















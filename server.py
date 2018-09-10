#!/usr/bin/python
#
# This file is part of the omega-iseries-pid-server
# Copyright M. Kostrun 2017,2018
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESSED OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
# THE REGENTS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#

import socket
import sys
from thread import *
from time import time

#
# initialize server logger
#
# setup telnet server:
PORT = 51234
HOST = ''     # Symbolic name, meaning all available interfaces
SOCKET_TIMEOUT_S = 2

# setup device:
#PID_SN = 'AI02C685'
PID_SN = 'A501IJOL'
LOG_TIME_DT_S = 5
LOG_FILENAME = './stove-'+socket.gethostname()+'-'+PID_SN+'.log'

import logging
import subprocess

def setup_custom_logger(name):
  # time zone information for the local system
  tz = subprocess.check_output(['date', '+%z'])
  tz = tz[:-1]
  formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S' + tz)
  handler = logging.FileHandler(LOG_FILENAME, mode='a',delay=False)
  handler.setFormatter(formatter)
  logger = logging.getLogger(name)
  logger.setLevel(logging.DEBUG)
  logger.addHandler(handler)
  return logger

#
# create logger
#
logger = setup_custom_logger('server')

#
# initialize omega PID cn-series controller on serial port
#
try:
  stove  # if 'fm' is not defined this fails with NameError
except NameError:
  execfile('liblab_pid_omega_cni.py')
  stove = omega_pid(PID_SN)
  sleep(1)


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(SOCKET_TIMEOUT_S)
logger.warning( 'Server socket created' )
num_connections=0

# Bind socket to local host and port
try:
  s.bind((HOST, PORT))
except socket.error as msg:
  logger.error( 'Server socket bind failed: ' + msg[1] + ', error no. ' + str(msg[0]))
  sys.exit()
logger.warning( 'Server socket bind complete' )

# Start listening on socket
s.listen(10)
logger.warning( 'Server listening on port ' + str(PORT) )

# Function for handling connections. This will be used to create threads
def clientthread(conn):
  global num_connections,LOG_TIME_DT_S
  #
  # only one thread can communicate with the stove
  #
  num_connections+=1
  if (num_connections>1):
    num_connections-=1
    conn.sendall('Connection rejected: Client number reached!\n')
    conn.close()
    exit()
  t_0_s = time()
  #
  # repetio ad infimum
  #
  conn.settimeout(SOCKET_TIMEOUT_S)
  while True:
    #
    # log the status of the stove
    #
    t_now_s = time()
    if (t_now_s - t_0_s > LOG_TIME_DT_S):
      t_0_s = t_now_s
      rval = stove.val()
      logger.info(str(rval) + ' C')
    #
    # non-blocking receive from client
    #   if times out, just try again
    #
    try:
      data = conn.recv(1024)
    except socket.timeout,e:
      err = e.args[0]
      if (err == 'timed out'):
        continue
      else:
        logger.error( e )
        break
    except socket.error,e:
      logger.error( e )
      break
    if (len(data)==0):
      break
    # chomp '\r' or '\n' from the end of it
    data = data[:-1]
    # client is allowed to directly write to the log
    # if the message is prepended with '#'
    if (data[0] == "#")
      logger.debug(data[1:])
      continue
    logger.debug(data)
    if ('quit' in data):
      break
    #
    #
    #
    if (('alarm' in data) or ('alarm1' in data) or ('alarm2' in data)):
      if ('alarm1' in data):
        off=1
        idx=1
      elif ('alarm' in data):
        off=0
        idx=1
      elif ('alarm2' in data):
        off=1
        idx=2
      if (data.find('=') == 5+off):
        # process cycle=nnn
        try:
          val = int(data[6+off:])
        except ValueError:
          conn.sendall('?'+'\n')
          continue
        stove.alarm(status=(val!=0),index=idx)
        conn.sendall('OK'+'\n')
      continue
    #
    #
    #
    if 'standby' in data:
      stove.standby(status=1)
      conn.sendall('OK'+'\n')
      continue
    #
    #
    #
    if 'run' in data:
      stove.standby(status=0)
      conn.sendall('OK'+'\n')
      continue
    #
    #
    #
    if 'val' in data:
      rval = stove.val()
      conn.sendall(str(rval)+'\n')
      logger.debug(str(rval))
    #
    #
    #
    if ('timepid' in data):
      if (data.find('=') == 7):
        # process cycle=nnn
        try:
          val = int(data[8:])
        except ValueError:
          conn.sendall('?'+'\n')
          continue
        stove.out1cnf(time_prop=(val!=0))
        stove.out2cnf(time_prop=(val!=0))
        conn.sendall('OK'+'\n')
      else:
        rval1 = int(stove.out1cnf()%2)
        rval2 = int(stove.out2cnf()%2)
        if (rval1==rval2):
          conn.sendall(str(rval1)+'\n')
          logger.debug(str(rval1))
        else:
          conn.sendall(str(rval1)+'!='+str(rval2)+'\n')
          logger.debug(str(rval1)+'!='+str(rval2))
    #
    #
    #
    if ('full_id' in data):
      if (data.find('=') == 7):
        # process cycle=nnn
        try:
          val = int(data[8:])
        except ValueError:
          conn.sendall('?'+'\n')
          continue
        stove.misccnf(full_id=(val!=0))
        conn.sendall('OK'+'\n')
      else:
        rval1 = int(stove.misccnf()/MISC_FULL_ID)%2
        conn.sendall(str(rval1)+'\n')
        logger.debug(str(rval1))
      continue
    #
    #
    #
    if ('sp_id' in data):
      if (data.find('=') == 5):
        # process cycle=nnn
        try:
          val = int(data[6:])
        except ValueError:
          conn.sendall('?'+'\n')
          continue
        stove.misccnf(sp_id=(val!=0))
        conn.sendall('OK'+'\n')
      else:
        rval1 = int(stove.misccnf()/MISC_SP_ID)%2
        conn.sendall(str(rval1)+'\n')
        logger.debug(str(rval1))
      continue
    #
    #
    #
    if ('direct' in data):
      if (data.find('=') == 6):
        # process cycle=nnn
        try:
          val = int(data[7:])
        except ValueError:
          conn.sendall('?'+'\n')
          continue
        stove.out1cnf(enable_direct=(val!=0))
        stove.out2cnf(enable_direct=(val!=0))
        conn.sendall('OK'+'\n')
      else:
        rval1 = int(stove.out1cnf()/OUT1CNG_DIRECT)%2
        rval2 = int(stove.out2cnf()/OUT2CNG_DIRECT)%2
        if (rval1==rval2):
          conn.sendall(str(rval1)+'\n')
          logger.debug(str(rval1))
        else:
          conn.sendall(str(rval1)+'!='+str(rval2)+'\n')
          logger.debug(str(rval1)+'!='+str(rval2))
    #
    #
    #
    if ('autotune' in data):
      if (data.find('=') == 8):
        # process cycle=nnn
        try:
          val = int(data[9:])
        except ValueError:
          conn.sendall('?'+'\n')
          continue
        stove.out1cnf(enable_autotune=(val!=0))
        conn.sendall('OK'+'\n')
      else:
        rval1 = int(stove.out1cnf()/OUT1CNG_AUTOTUNE)%2
        conn.sendall(str(rval1)+'\n')
        logger.debug(str(rval1))
    #
    #
    #
    if ('antiwindup' in data):
      if (data.find('=') == 10):
        # process cycle=nnn
        try:
          val = int(data[11:])
        except ValueError:
          conn.sendall('?'+'\n')
          continue
        stove.out1cnf(anti_wind_up=(val!=0))
        conn.sendall('OK'+'\n')
      else:
        rval1 = int(stove.out1cnf()/OUT1CNG_ANTI_WIND_UP)%2
        conn.sendall(str(rval1)+'\n')
        logger.debug(str(rval1))
      continue
    #
    #
    #
    if ('autopid' in data):
      if (data.find('=') == 7):
        # process cycle=nnn
        try:
          val = int(data[8:])
        except ValueError:
          conn.sendall('?'+'\n')
          continue
        stove.out1cnf(enable_autopid=(val!=0))
        stove.out2cnf(enable_autopid=(val!=0))
        conn.sendall('OK'+'\n')
      else:
        rval1 = int(stove.out1cnf()/OUT1CNG_AUTOPID)%2
        rval2 = int(stove.out2cnf()/OUT2CNG_AUTOPID)%2
        if (rval1==rval2):
          conn.sendall(str(rval1)+'\n')
          logger.debug(str(rval1))
        else:
          conn.sendall(str(rval1)+'!='+str(rval2)+'\n')
          logger.debug(str(rval1)+'!='+str(rval2))
      continue
    #
    #
    #
    if ('damping' in data):
      if (data.find('=') == 7):
        # process cycle=nnn
        try:
          val = int(data[8:])
        except ValueError:
          conn.sendall('?'+'\n')
          continue
        stove.out2cnf(damping=(val%8))
        conn.sendall('OK'+'\n')
      else:
        rval = (stove.out2cnf()/OUT2CNG_DAMPING)%8
        conn.sendall(str(rval)+'\n')
        logger.debug(str(rval))
      continue
    #
    #
    #
    if ('ramptime' in data):
      if (data.find('=') == 8):
        # process ramptime=[hr,min]
        try:
          val = eval('['+data[9:-1]+']')
          if (len(val)!=2):
            conn.sendall('?'+'\n')
            continue
        except ValueError:
          conn.sendall('?'+'\n')
          continue
        stove.ramptime(val)
        conn.sendall('OK'+'\n')
      else:
        rval = stove.ramptime()
        conn.sendall(str(rval)+'\n')
        logger.debug(str(rval))
      continue
    #
    #
    #
    if ('ramp' in data):
      if (data.find('=') == 4):
        # process ramp=1,0
        try:
          val = int(data[5:])
        except ValueError:
          conn.sendall('?'+'\n')
          continue
        val = (val>0)
        #print 'stove.out2cnf',val
        stove.out2cnf(enable_ramp=val)
        conn.sendall('OK'+'\n')
      else:
        rval = stove.out2cnf()
        rval = int(rval/OUT2CNG_RAMP)%2
        conn.sendall(str(rval)+'\n')
        logger.debug(str(rval))
      continue
    if ('soaktime' in data):
      if (data.find('=') == 8):
        # process soaktime=[hr,min]
        try:
          val = eval('[' + data[9:-1] + '')
          if (len(val)!=2):
            conn.sendall('?'+'\n')
            continue
        except ValueError:
          conn.sendall('?'+'\n')
          continue
        #print 'stove.out2cnf',val
        stove.soaktime(val)
        conn.sendall('OK'+'\n')
      else:
        rval = stove.soaktime()
        conn.sendall(str(rval)+'\n')
        logger.debug(str(rval))
      continue
    #
    #
    #
    if ('soak' in data):
      if (data.find('=') == 4):
        # process soak=1,0
        try:
          val = int(data[5:])
        except ValueError:
          conn.sendall('?'+'\n')
          continue
        val = (val>0)
        stove.out2cnf(enable_soak=val)
        conn.sendall('OK'+'\n')
      else:
        rval = stove.out2cnf()
        rval = int(rval/OUT2CNG_SOAK)%2
        conn.sendall(str(rval)+'\n')
        logger.debug(str(rval))
      continue
    #
    #
    #
    if (('cycle' in data) or ('cycle1' in data) or ('cycle2' in data)):
      if ('cycle' in data):
        off=0
        idx=1
      if ('cycle1' in data):
        off=1
        idx=1
      if ('cycle2' in data):
        off=1
        idx=2
      if (data.find('=') == 5+off):
        # process cycle=nnn
        try:
          val = int(data[6+off:])
        except ValueError:
          conn.sendall('?'+'\n')
          continue
        stove.cycle(val,index=idx)
        conn.sendall('OK'+'\n')
      else:
        rval = stove.cycle(index=idx)
        if ('store' in data):
          stove.cycle(rval,save=1,index=idx)
          conn.sendall('cycle'+str(idx)+'='+str(rval)+' stored\n')
          logger.info('cycle'+str(idx)+'='+str(rval) + ' stored')
        else:
          conn.sendall(str(rval)+'\n')
          logger.debug(str(rval))
      continue
    #
    #
    #
    if (('band' in data) or ('band1' in data) or ('band2' in data)):
      if ('band' in data):
        off=0
        idx=1
      if ('band1' in data):
        off=1
        idx=1
      if ('band2' in data):
        off=1
        idx=2
      if (data.find('=') == 4+off):
        # process cycle=nnn
        if (len(data)>6):
          val = int(data[5+off:])
          stove.band(val,index=idx)
          conn.sendall('OK'+'\n')
        else:
          conn.sendall('?'+'\n')
          continue
      else:
        rval = stove.band(index=idx)
        if ('store' in data):
          stove.band(rval,save=1,index=idx)
          conn.sendall('band'+str(idx)+'='+str(rval)+' stored\n')
          logger.debug('band'+str(idx)+'='+str(rval) + ' stored')
        else:
          conn.sendall(str(rval)+'\n')
          logger.debug(str(rval))
      continue
    #
    #
    #
    if 'reset' in data:
      if (data.find('=') == 5):
        # process cycle=nnn
        if (len(data)>6):
          val = int(data[6:])
          stove.reset(val)
          conn.sendall('OK'+'\n')
        else:
          conn.sendall('?'+'\n')
          continue
      else:
        rval = stove.reset()
        if ('store' in data):
          stove.reset(rval,1)
          conn.sendall('reset='+str(rval)+' stored\n')
          logger.debug('reset='+str(rval) + ' stored')
        else:
          conn.sendall(str(rval)+'\n')
          logger.debug(str(rval))
      continue
    #
    #
    #
    if 'rate' in data:
      if (data.find('=') == 4):
        # process cycle=nnn
        try:
          val = int(data[5:])
        except ValueError:
          conn.sendall('?'+'\n')
          continue
        stove.rate(val)
        conn.sendall('OK'+'\n')
      else:
        rval = stove.rate()
        if ('store' in data):
          stove.rate(rval,1)
          conn.sendall('rate='+str(rval)+' stored\n')
          logger.debug('rate='+str(rval) + ' stored')
        else:
          conn.sendall(str(rval)+'\n')
          logger.debug(str(rval))
      continue
    #
    #
    #
    if (('sp1' in data) or ('sp2' in data)):
      if ('sp1' in data):
        idx=1
      if ('sp2' in data):
        idx=2
      if (data.find('=') == 3):
        # process sp1=xxxxxx
        try:
          val = float(data[4:])
        except ValueError:
          conn.sendall('?'+'\n')
          continue
        stove.sp(val,index=idx)
        conn.sendall('OK'+'\n')
      else:
        rval=stove.sp(index=idx)
        if ('store' in data):
          stove.sp(rval,save=1,index=idx)
          conn.sendall('sp'+str(idx)+'='+str(rval) + ' stored\n')
          logger.debug('sp'+str(idx)+'='+str(rval) + ' stored')
        else:
          conn.sendall(str(rval)+'\n')
          logger.debug(str(rval))
    #
    #
    #
    if 'restart' in data:
      stove.restart()
      conn.sendall('OK'+'\n')
    #
    #
    #
    if ('id' in data):
      if (data.find('=') == 2):
        # process cycle=nnn
        try:
          val = int(data[3:])
        except ValueError:
          conn.sendall('?'+'\n')
          continue
        #stove.id(val)
        conn.sendall('OK'+'\n')
      else:
        rval = stove.id()
        conn.sendall(str(rval)+'\n')
        logger.debug(str(rval))
      continue

  # came out of loop
  logger.warning('Client disconnected')
  num_connections-=1
  conn.close()
  exit()

#
# server loop:
#   if no connections, then monitor the temperature of the stove
t_0_s = time()
while 1:
  #
  # wait to accept a connection - blocking call
  #
  try:
    conn, addr = s.accept()
  except socket.timeout,e:
    err = e.args[0]
    if (err == 'timed out'):
      #
      # log the status of the stove
      #
      if (num_connections == 0):
        t_now_s = time()
        if (t_now_s - t_0_s > LOG_TIME_DT_S):
          t_0_s = t_now_s
          rval = stove.val()
          logger.info(str(rval) + ' C')
      continue
    else:
      logger.error( err )
      break
  except socket.error,e:
    err = e.args[0]
    logger.error( err )
    break

  logger.warning( 'Connected with ' + addr[0] + ':' + str(addr[1]) )
  # start new thread takes 1st argument as a function name to be run,
  # second is the tuple of arguments to the function.
  start_new_thread(clientthread ,(conn,))

s.close()
logger.warning('Server stopped')

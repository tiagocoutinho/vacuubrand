import serial
import logging
import re
import taurus

class CommType(object):
    Serial = 'serial'
    DS_Serial = 'serialDS'

UNITS = { '0': 'mbar',
          '1': 'Torr',
          '2': 'hPa'   
          }

class VaccumDCP300(object):
    
    def __init__(self, comm, dsname=None, port='/dev/ttyS0', baudrate=19200, # baud rate
                 bytesize=serial.EIGHTBITS,    # number of data bits
                 parity=serial.PARITY_NONE,    # enable parity checking
                 stopbits=serial.STOPBITS_ONE, # number of stop bits
                 timeout=3,          # set a timeout value, None to wait forever
                 rtscts=True,  ):
        
        if comm == CommType.Serial:
            self._comm = serial.Serial(port, baudrate=baudrate, 
                                       bytesize=bytesize,
                                       parity=parity, stopbits=stopbits, 
                                       timeout=timeout, rtscts=rtscts)
            self.read = self._readSerial
            self.write = self._writeSerial
            
        elif comm == CommType.DS_Serial:
            self.device = taurus.Device(dsName)
            self.read = self._readDS
            self.write = self._writeDS
            
        else:
            msg="This CommType is not allowed"
            raise ValueError(msg)
            
        logging.debug('Created VaccumDCP300 object') 

    def _readDS(self):
        pass
    
    def _readSerial(self):
        try:
            logging.debug('Reading response')
            result = self._comm.readline()
            logging.debug('Read %s Value', repr(result))

        except Exception, e:
            result = None
        return result

    def _writeDS(self):
        pass
    
    def _writeSerial(self, data):
        
        try:
            logging.debug('Writing command')
            data = data + '\n'
            self._comm.write(data)
        except Exception, e:
            return False
        return True

    def sendCmd(self, cmd):
        logging.debug('Sending %s command', cmd)
        if self.write(cmd):
            return self.read()
        return None
    
    def _openCom(self):
        logging.debug('Opening Port')
        self._comm.open()
            
    def _closeCom(self):
        logging.debug('Closing Port')
        self._comm.close()
                 
    def _getUnit(self):
        
        cfg_cmd= 'IN_CFG'
        cfg = self.sendCmd(cfg_cmd)
        unit = UNITS[cfg[1]]
        logging.debug('Unit: %s', unit)

        return unit
        
    def _getValueFromResponse(self,data):
        
        data = (re.findall("\d+.\d+",data))[0]
        logging.debug('Cleaned response:  %s ', data)
        
        return data    
            
if __name__ == '__main__':
    format ='%(asctime)s %(levelname)s:%(message)s'
    level = logging.DEBUG
    logging.basicConfig(format=format,level=level)
    
    port = sys.arg[1]
    cmd_test= 'IN_PV_1'
    a = VaccumDCP300(commType=CommType.Serial, port=port)
    r = a.sendCmd(cmd_test)
    a._getValueFromResponse(r)
    a._getUnit()
    
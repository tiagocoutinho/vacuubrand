#   '$Name:  $pp`';
#   '$Header:  $';
#=============================================================================
#
# file :       PyDsVacuuBrand.py 
#
# description : The device server is to communicate with the VacuuBrand.  
#
# project :     TANGO Device Server
#
# $Author:  $
#
# $Revision:  $
#
# $Log:  $
#
# copyleft :    Alba Synchrotron Radiation Facility
#               Cerdanyola del Valles
#               Spain
#
#
#         (c) - Controls group - ALBA
#=============================================================================

import PyTango
import sys
import time
from VacuumbrandLib import VaccumDCP300 

class PyDsVacuuBrandClass(PyTango.DeviceClass):
#   Class Properties
    class_property_list = {
        }

    #   Device Properties
    device_property_list = {
        'port':[PyTango.DevString, 'Serial port name', '/dev/ttyS0' ],  
        'baudrate': [PyTango.DevLong, 'Serial port bautrate', 19200 ],
        }

    #   Command definitions
    cmd_list = {}
   
    attr_list = {
                 'Pressure':[[PyTango.ArgType.DevFloat, 
                              PyTango.AttrDataFormat.SCALAR,
                              PyTango.AttrWriteType.READ]],
                 'Unit':[[PyTango.ArgType.DevString, 
                              PyTango.AttrDataFormat.SCALAR,
                              PyTango.AttrWriteType.READ]],}
    
    def __init__(self, name):
        PyTango.DeviceClass.__init__(self, name)
        self.set_type("PyDsVacuuBrand")
        
class PyDsVacuuBrand(PyTango.Device_4Impl):

    #@PyTango.DebugIt()
    def __init__(self,cl,name):
        PyTango.Device_4Impl.__init__(self, cl, name)
        self.info_stream('In PyDsVacuuBrand.__init__')
        PyDsVacuuBrand.init_device(self)
        self.set_state(PyTango.DevState.ON)

    @PyTango.DebugIt()
    def init_device(self):
        self.info_stream('In Python init_device method')
        self.get_device_properties(self.get_device_class())
        self.info_stream('port: %s baudrate: %s' % (self.port, self.baudrate))
        self.vacuum_device = VaccumDCP300(port=self.port, baudrate=self.baudrate)


    #------------------------------------------------------------------

    @PyTango.DebugIt()
    def delete_device(self):
        self.info_stream('PyDsVacuuBrand.delete_device')
        self.vacuum_device._close()
        
    #------------------------------------------------------------------
    # ATTRIBUTES
    #------------------------------------------------------------------

    @PyTango.DebugIt()
    def read_Pressure(self, the_att):
        self.info_stream("read_Pressure")
        #Current Pressure command
        cmd = 'IN_PV_1'
        pressure = self.vacuum_device.sendCmd(cmd)
        pressure = self.vacuum_device._getValueFromResponse(pressure)
        the_att.set_value(float(pressure))

    @PyTango.DebugIt()
    def is_Pressure_allowed(self, req_type):
        return self.get_state() in (PyTango.DevState.ON,)
       
    def read_Unit(self, the_att):
        the_att.set_value(self.vacuum_device._getUnit())

if __name__ == '__main__':
    util = PyTango.Util(sys.argv)
    util.add_class(PyDsVacuuBrandClass, PyDsVacuuBrand)

    U = PyTango.Util.instance()
    U.server_init()
    U.server_run()

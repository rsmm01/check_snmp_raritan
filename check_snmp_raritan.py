#!/usr/bin/python
# check_snmp_raritan.py - Check a Raritan Dominition PX PDU (Power Distribution Unit), the outlets and the connected sensors
# example command: ./check_snmp_raritan.py -H 172.29.1.2 -t power
# example command: ./check_snmp_raritan.py -H 172.29.1.2 -t sensor -i 1


# Copyright (C) 2016 rsmuc rsmuc@mailbox.org
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with check_snmp_raritan.py.  If not, see <http://www.gnu.org/licenses/>.

# Import PluginHelper and some utility constants from the Plugins module
from pynag.Plugins import PluginHelper,ok,warning,critical,unknown
import sys
import netsnmp
import math
import base64

# function for snmpget and walk
def get_data(host, version, community, oid):
    var = netsnmp.Varbind(oid)
    data = netsnmp.snmpget(var, Version=version, DestHost=host, Community=community)
    value = data[0]
    return value

def walk_data(host, version, community, oid):
    var = netsnmp.Varbind(oid)
    data = netsnmp.snmpwalk(var, Version=version, DestHost=host, Community=community)
    return data

# function to calculate the real value
def real_value(value, digit):
    return str(float(value) / math.pow(10, float(digit)))

# Create an instance of PluginHelper()
helper = PluginHelper()

# define the command line options
helper.parser.add_option('-H', help="Hostname or ip address", dest="hostname")
helper.parser.add_option('-C', '--community', dest='community', help='SNMP community of the SNMP service on target host.', default='public')
helper.parser.add_option('-V', '--snmpversion', dest='version', help='SNMP version. (1 or 2)', default=2, type='int')
helper.parser.add_option('-t', help="The type you want to monitor (inlet, outlet, sensor)", default="inlet", dest="typ")
helper.parser.add_option('-i', help="The id of the outlet / sensor you want to monitor (1-99)", default="1", dest="id")
helper.parse_arguments()

# get the options
id = helper.options.id
typ = helper.options.typ
host = helper.options.hostname
version = helper.options.version
community = helper.options.community

# verify that there is a hostname set
if host == "" or host == None:
    helper.exit(summary="Hostname must be specified", exit_code=unknown, perfdata='')

# these dicts we need to get human readable values

names = {
	'C': 'Current',
	'V': 'Voltage',
	'c': 'Current',
	'v': 'Voltage',
	'P': 'Power',
	'p': 'Power',
	}

sensors = {
    0: "rmsCurrent",
    2: "unbalancedCurrent",
    3: "rmsVoltage", 
    4: "activePower",
    5: "apparentPower",
    6: "powerFactor",
    7: "activeEnergy",
    8: "apparentEnergy"
}
    
type = {
	'C': '.1',
	'V': '.4',
	'c': '.1',
	'v': '.4',
	'p': '.5',
	'P': '.5',
	}	
	
states = {
	-1: "unavailable",
	0 : "open",
	1 : "closed",
	2 : "belowLowerCritical",
	3 : "belowLowerWarning",
	4 : "normal",
	5 : "aboveUpperWarning",
	6 : "aboveUpperCritical",
	7 : "on",
	8 : "off",
	9 : "detected",
	10: "notDetected",
	11: "alarmed",
	12: "ok",
	13: "marginal",
	14: "fail",
	15: "yes",
	16: "no",
	17: "standby",
	18: "one",
	19: "two",
	20: "inSync",
	21: "outOfSync"
    }
	
units =  {
	-1: "",
	0 : "other",
	1 : "V",
	2 : "A",
	3 : "W",
	4 : "VA",
	5 : "Wh",
	6 : "Vh",
	7 : "C",
	8 : "Hz",
	9 : "%",
	10: "ms",
	11: "Pa",
	12: "psi",
	13: "g",
	14: "F",
	15: "feet",
	16: "inches",
	17: "cm",
	18: "meters",
	19: "rpm",
	20: "degrees",
}

## here the logic for the inlet check begins
if typ.lower() == "inlet":
    # OIDs for Inlet from PDU2-MIB
    #oid_inlet_sensors            = '.1.3.6.1.4.1.13742.6.3.3.4.1.25' # all sensors that are available
    oid_inlet_value              = '.1.3.6.1.4.1.13742.6.5.2.3.1.4' # the value from the sensor (must be devided by the digit)
    oid_inlet_unit               = '.1.3.6.1.4.1.13742.6.3.3.4.1.6' # the unit of the value
    oid_inlet_digits             = '.1.3.6.1.4.1.13742.6.3.3.4.1.7' # the digit we need for the real_value
    oid_inlet_state              = '.1.3.6.1.4.1.13742.6.5.2.3.1.3' # the state if this is ok or not ok
    #oid_inlet_enabled_thresholds = '.1.3.6.1.4.1.13742.6.3.3.4.1.25' # enabled threholds
    oid_inlet_warning_lower      = '.1.3.6.1.4.1.13742.6.3.3.4.1.22' # warning_lower_threshold (must be divided by the digit)
    oid_inlet_warning_upper      = '.1.3.6.1.4.1.13742.6.3.3.4.1.24' # warning_upper_threhsold (must be divided by the digit)
    oid_inlet_critical_lower     = '.1.3.6.1.4.1.13742.6.3.3.4.1.21' # critical_lower_threshold (must be divided by the digit)
    oid_inlet_critical_upper     = '.1.3.6.1.4.1.13742.6.3.3.4.1.23' # critical_upper_threhold (must be divided by the digit)
    
    # walk the data
    #inlet_sensors               = walk_data(host, version, community, oid_inlet_sensors)
    inlet_values                = walk_data(host, version, community, oid_inlet_value)
    inlet_units                 = walk_data(host, version, community, oid_inlet_unit)
    inlet_digits                = walk_data(host, version, community, oid_inlet_digits)
    inlet_states                = walk_data(host, version, community, oid_inlet_state)
    #inlet_enabled_thresholds    = walk_data(host, version, community, oid_inlet_enabled_thresholds)
    inlet_warning_lowers        = walk_data(host, version, community, oid_inlet_warning_lower)
    inlet_warning_uppers        = walk_data(host, version, community, oid_inlet_warning_upper)
    inlet_critical_lowers       = walk_data(host, version, community, oid_inlet_critical_lower)
    inlet_critical_uppers       = walk_data(host, version, community, oid_inlet_critical_upper)
    


    # all list must have the same length, if not something went wrong. that makes it easier and we need less loops    
    # translate the data in human readable units    
    for x in range(len(inlet_values)):            
        #inlet_sensor            = sensors[int(inlet_sensors[x])]
        inlet_unit              = units[int(inlet_units[x])]
        inlet_digit             = inlet_digits[x]
        inlet_state             = states[int(inlet_states[x])]
        #inlet_enabled_threshold = inlet_enabled_thresholds[x]
        inlet_value             = real_value(inlet_values[x], inlet_digit)        
        inlet_warning_lower     = real_value(inlet_warning_lowers[x], inlet_digit)
        inlet_warning_upper     = real_value(inlet_warning_uppers[x], inlet_digit)
        inlet_critical_lower    = real_value(inlet_critical_lowers[x], inlet_digit)
        inlet_critical_upper    = real_value(inlet_critical_uppers[x], inlet_digit)
                
        print "sensor" + "\t" + inlet_value + "\t" + inlet_unit + "\t" + inlet_state +  "\t" + "\t" + inlet_warning_lower + "\t" +  inlet_warning_upper + "\t" + inlet_critical_lower + "\t" + inlet_critical_upper
        
    
if typ.lower() == "outlet":
    # here we need the id
    base_oid_outlet_name    = '.1.3.6.1.4.1.13742.6.3.5.3.1.3.1' 		# Name
    base_oid_outlet_state   = '.1.3.6.1.4.1.13742.6.5.4.3.1.3.1' 		# Value
    oid_outlet_name         = base_oid_outlet_name + "." + id           # here we add the id, to get the name
    oid_outlet_state        = base_oid_outlet_state + "." + id + ".14"   # here we add the id, to get the name
    print oid_outlet_state

    # we just want to receive the status of one sensor
    outlet_name                = get_data(host, version, community, oid_outlet_name)
    outlet_state               = get_data(host, version, community, oid_outlet_state)
    print outlet_name
    print states[int(outlet_state)]
    
if typ.lower() == "sensor":
    oid_sensor_names    =   '.1.3.6.1.4.1.13742.6.3.6.3.1.4.1' 		#Name
    oid_sesor_units     =   '.1.3.6.1.4.1.13742.6.3.6.3.1.16.1' 		#Unit
    oids_sensor_digits  =   '.1.3.6.1.4.1.13742.6.3.6.3.1.17.1' 		#Digits
    oids_sensor_states  =   '.1.3.6.1.4.1.13742.6.5.5.3.1.3.1'			#State
    oids_sensor_values  =   '.1.3.6.1.4.1.13742.6.5.5.3.1.4.1'			#Value
    oids_sensor_types   =   '.1.3.6.1.4.1.13742.6.3.6.3.1.2.1'			#Type

    sensor_names        = walk_data(host, version, community, oid_sensor_names)
    sensor_units        = walk_data(host, version, community, oid_sesor_units)
    sensor_digits       = walk_data(host, version, community, oids_sensor_digits)
    sensor_states       = walk_data(host, version, community, oids_sensor_states)
    sensor_values       = walk_data(host, version, community, oids_sensor_values)
    sensor_types        = walk_data(host, version, community, oids_sensor_types)

    print sensor_names
    print sensor_units
    print sensor_digits
    print sensor_states
    print sensor_values
    print sensor_types

 
# The default return value should be always OK
helper.status(ok)

##############
## here we just want to print the current GPS position
##############

## clenaup: don't know if we really want to show the position in the summary or if we should move it to the long output

#gps_position = get_data(host, version, community, gps_position)
#helper.add_summary(gps_position)


#############
## here we check the ntp state for the new Meinbergs
#############
#ntp_status_int = get_data(host, version, community, ntp_current_state_int)

## convert the ntp_status integer value in a human readable value
#try:
#    ntp_status_string = ntp_status[ntp_status_int]
#except KeyError:
#    # if we receive an value, that is not in the dict
#    helper.exit(summary="received an undefined value from device: " + ntp_status_int, exit_code=unknown, perfdata='')

     
## the ntp status should be synchronized (new MIB) or normalOperation (old mib)
#if ntp_status_string != "synchronized" and ntp_status_string != "normalOperationPPS":
    
#    # that is a critical condition, because the time reference will not be reliable anymore
#    helper.status(critical)
#    helper.add_summary("NTP status: " + ntp_status_string)

###########
## here we check the status of the GPS
##########

#gps_status_int = get_data(host, version, community, gps_mode_int)

#try:
#    gps_mode_string = gps_mode[gps_status_int]
#except KeyError:
#    # if we receive an value, that is not in the dict
#    helper.exit(summary="received an undefined value from device: " + gps_status_int, exit_code=unknown, perfdata='')

#if gps_mode_string != "normalOperation" and gps_mode_string != "gpsSync" :
#    # that is a warning condition, NTP could still work without the GPS antenna
#    helper.status(warning)
#    helper.add_summary("GPS status: " + gps_mode_string)

##############
## check the amount of good satellites
##############

## here we get the value for the satellites
#good_satellites = get_data(host, version, community, gps_satellites_good)

## Show the summary and add the metric and afterwards check the metric
#helper.add_summary("Good satellites: %s" % good_satellites)
#helper.add_metric(label='satellites',value=good_satellites) 

#helper.check_all_metrics()

## Print out plugin information and exit nagios-style
#helper.exit()

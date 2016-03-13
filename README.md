# check_snmp_raritan.py
---

Check a Raritan Dominition PX PDU (Power Distribution Unit):
    * the outlets (On, Off)
    * the inlet (Power, Current, Voltage)
    * and the connected sensors

* Tested device: PX2-2486
* Tested sensors: Temperature, Humidity, Contact Closure, Air Pressure

# under development (do not use the plugin)

The plugin requires pynag (https://github.com/pynag/pynag) and python-netsnmp.


### Example:

#### Check the Inlet Power:

 ```./check_snmp_raritan.py -H 172.29.1.2 -t inlet```
 
 ```=> 
Warning - 3 0.003 W is belowLowerWarning | '3'=0.003W;0.003;0.003;;
 ```
#### Monitor Sensor with ID 1:

 ```./check_snmp_raritan.py -H 172.29.1.2 -t sensor -i 1```

 ``` 
=> 
Warning - 3 0.003 W is belowLowerWarning | '3'=0.003W;0.003;0.003;;
 ```


#### Monitor Outlet with ID 3:

 ```./check_snmp_raritan.py -H 172.29.1.2 -t outlet -i 3```

```
Critical - Outlet 3 - '3' is: OFF
```

## Parameters
 ```
Options:
  -h, --help            show this help message and exit
  -H HOSTNAME           Hostname or ip address
  -C COMMUNITY, --community=COMMUNITY
                        SNMP community of the SNMP service on target host.
  -V VERSION, --snmpversion=VERSION
                        SNMP version. (1 or 2)
  -t TYP                The type you want to monitor (inlet, outlet, sensor)
  -i ID                 The id of the outlet / sensor you want to monitor
                        (1-99)
 ``` 

## TODO:
* Implement SNMPv3
* Maybe it should be possible to monitor all services / sensors in one check
* Cleanup the code
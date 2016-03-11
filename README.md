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

 ```./check_snmp_raritan.py -H 172.29.1.2 -t power```
 
 ```=> 
OK - GPS Position: 48.1275 11.6126 623m. Good satellites: 10 | 'satellites'=10;;;;
 ```
#### Monitor Sensor with ID 1:

 ```./check_snmp_raritan.py -H 172.29.1.2 -t sensor -i 1```

 ``` 
=> 
OK - GPS Position: 48.1275 11.6126 623m. Good satellites: 9 | 'satellites'=9;8:;2:;;
 ```


#### Monitor Sensor with ID 1:

 ```./check_snmp_raritan.py -H 172.29.1.2 -t sensor -i 1```

## Parameters
 ```
- -H HOSTNAME           Hostname or ip address
-  --version=VERSION     SNMP version (default: 2)
-  --community=COMMUNITY SNMP community (default: public)
-  -m MIB                Version of the MIB (NG = MBG-LANTIME-NG-MIB.mib) 
 ``` 

## TODO:
* Implement SNMPv3

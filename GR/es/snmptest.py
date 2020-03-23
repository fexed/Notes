#!/usr/bin/python3

# Documentation
# Author: Federico Matteoni
#
# Installation
# pip install pysnmp
#
# Example: python snmptest.py public demo.snmplabs.com

# Imports
import sys
from time import sleep
from datetime import datetime, timedelta
from pysnmp.hlapi import *

# Params check
if len(sys.argv) < 3:
    print("usage:\t\t" + sys.argv[0] + " community hostname [port]")
    print("example:\t" + sys.argv[0] + " public demo.snmplabs.com")
else:
    hostname = sys.argv[2]
    community = sys.argv[1]
    if len(sys.argv) >= 4: #If no port is given, use the default one
        port = int(sys.argv[3])
    else:
        port = 161    
    print("Requesting " + hostname + ":" + str(port) + "\n")
    now = datetime.now()

# hostname
    currtime = now.strftime("%H.%M.%S") #Timestamp
    errInd, errName, errIndex, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData(community),
               UdpTransportTarget((hostname, port)),
               ContextData(),
               ObjectType(ObjectIdentity('iso.3.6.1.2.1.1.5.0')) #SNMPv2-MIB::sysName.0
               )
        )

    print(currtime + "\n")
    if errInd:
        print(errInd)
    elif errName:
        print('Errore %s@[%s]' % (errName, varBinds[int(errIndex) - 1][0]))
    else:
        targetname = varBinds[0].prettyPrint().split("=")[1].strip()
        print(targetname)

# hostdescr
    errInd, errName, errIndex, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData(community),
               UdpTransportTarget((hostname, port)),
               ContextData(),
               ObjectType(ObjectIdentity('iso.3.6.1.2.1.1.1.0')) #SNMPv2-MIB::sysDescr.0
               )
        )

    if errInd:
        print(errInd)
    elif errName:
        print('Errore %s@[%s]' % (errName, varBinds[int(errIndex) - 1][0]))
    else:
        target = varBinds[0].prettyPrint().split("=")[1].strip()
        print("\t" + target)

# uptime
    print("\tUptime\t", end = '')
    errInd, errName, errIndex, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData(community),
               UdpTransportTarget((hostname, port)),
               ContextData(),
               ObjectType(ObjectIdentity('iso.3.6.1.2.1.1.3.0')) #DISMAN-EVENT-MIB::sysUpTimeInstance
               )
        )

    if errInd:
        print(errInd)
    elif errName:
        print('Errore %s@[%s]' % (errName, varBinds[int(errIndex) - 1][0]))
    else:
        ticks = int(varBinds[0].prettyPrint().split("=")[1].strip())
        secs = ticks/100
        uptimestr = timedelta(seconds=secs)
        print("\t" + str(uptimestr) + " (" + str(ticks) + ")")

# ssCpuIdle
    print("\tCPU\t\t", end = '')
    errInd, errName, errIndex, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData(community),
               UdpTransportTarget((hostname, port)),
               ContextData(),
               ObjectType(ObjectIdentity('UCD-SNMP-MIB', 'ssCpuIdle', 0))
               )
        )

    if errInd:
        print(errInd)
    elif errName:
        print('Errore %s@[%s]' % (errName, varBinds[int(errIndex) - 1][0]))
    else:
        cpuIdle = varBinds[0].prettyPrint().split("=")[1].strip()
        print(cpuIdle + "%")

# memTotalReal
    print("\tMem total\t", end = '')
    errInd, errName, errIndex, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData(community),
               UdpTransportTarget((hostname, port)),
               ContextData(),
               ObjectType(ObjectIdentity('UCD-SNMP-MIB', 'memTotalReal', 0))
               )
        )
    
    if errInd:
        print(errInd)
    elif errName:
        print('Errore %s@[%s]' % (errName, varBinds[int(errIndex) - 1][0]))
    else:
        memTotal = varBinds[0].prettyPrint().split("=")[1].strip()
        print(memTotal + " KB")
    
# memAvailReal
    print("\tMem avail.\t", end = '')
    errInd, errName, errIndex, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData(community),
               UdpTransportTarget((hostname, port)),
               ContextData(),
               ObjectType(ObjectIdentity('UCD-SNMP-MIB', 'memAvailReal', 0))
               )
        )
    
    if errInd:
        print(errInd)
    elif errName:
        print('Errore %s@[%s]' % (errName, varBinds[int(errIndex) - 1][0]))
    else:
        memAvail = varBinds[0].prettyPrint().split("=")[1].strip()
        print(memAvail + " KB")

# loop
    for i in range(5):
        sleep(1)
        now = datetime.now()
        currtime = now.strftime("%H.%M.%S")
        print("\n" + str(i+1) + " (" + currtime + ")\t######")
        print("\tCPU\t\t", end = '');
        errInd, errName, errIndex, varBinds = next(
            getCmd(SnmpEngine(),
                   CommunityData(community),
                   UdpTransportTarget((hostname, port)),
                   ContextData(),
                   ObjectType(ObjectIdentity('UCD-SNMP-MIB', 'ssCpuIdle', 0))
                   )
            )

        if errInd:
            print(errInd)
        elif errName:
            print('Errore %s@[%s]' % (errName, varBinds[int(errIndex) - 1][0]))
        else:
            cpuIdle = varBinds[0].prettyPrint().split("=")[1].strip()
            print(cpuIdle + "%")

        print("\tMem\t\t", end = '')
        errInd, errName, errIndex, varBinds = next(
            getCmd(SnmpEngine(),
                   CommunityData(community),
                   UdpTransportTarget((hostname, port)),
                   ContextData(),
                   ObjectType(ObjectIdentity('UCD-SNMP-MIB', 'memAvailReal', 0))
                   )
            )
        
        if errInd:
            print(errInd)
        elif errName:
            print('Errore %s@[%s]' % (errName, varBinds[int(errIndex) - 1][0]))
        else:
            memAvail = varBinds[0].prettyPrint().split("=")[1].strip()
            print(memAvail + "/" + memTotal + " KB")


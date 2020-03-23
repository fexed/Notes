#!/usr/bin/python3

# Documentation
# Author: Federico Matteoni
# Date: 20/03/2020
#
# Installation
# pip install pysnmp
#
# Example: python snmptest.py public demo.snmplabs.com

# Imports
import sys
from pysnmp.hlapi import *

# Params check
if len(sys.argv) != 3:
    print("usage: " + sys.argv[0] + " <community> <hostname>")
else:
    print("Requesting...")
    hostname = sys.argv[2]
    community = sys.argv[1]
####

# ssCpuIdle
    errInd, errName, errIndex, varBinds = next(getCmd(SnmpEngine(), CommunityData(community, mpModel=0), UdpTransportTarget((hostname, 161)), ContextData(), ObjectType(ObjectIdentity('UCD-SNMP-MIB', 'ssCpuIdle', 0))))

    if errInd:
        print(errInd)
    elif errName:
        print('Errore %s@[%s]' % (errName, varBinds[int(errIndex) - 1][0]))
    else:
        cpuIdle = varBinds[0].prettyPrint().split("=")[1].strip()
        print("CPU =\t\t" + cpuIdle + "%")
    
# memAvailReal
    errInd, errName, errIndex, varBinds = next(getCmd(SnmpEngine(), CommunityData(community, mpModel=0), UdpTransportTarget((hostname, 161)), ContextData(), ObjectType(ObjectIdentity('UCD-SNMP-MIB', 'memAvailReal', 0))))
    
    if errInd:
        print(errInd)
    elif errName:
        print('Errore %s@[%s]' % (errName, varBinds[int(errIndex) - 1][0]))
    else:
        memAvail = varBinds[0].prettyPrint().split("=")[1].strip()
        print("Mem avail. =\t" + memAvail + " KB")

# memTotalReal
    errInd, errName, errIndex, varBinds = next(getCmd(SnmpEngine(), CommunityData(community, mpModel=0), UdpTransportTarget((hostname, 161)), ContextData(), ObjectType(ObjectIdentity('UCD-SNMP-MIB', 'memTotalReal', 0))))
    
    if errInd:
        print(errInd)
    elif errName:
        print('Errore %s@[%s]' % (errName, varBinds[int(errIndex) - 1][0]))
    else:
        memTotal = varBinds[0].prettyPrint().split("=")[1].strip()
        print("Mem total =\t" + memTotal + " KB")

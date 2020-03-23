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
from pysnmp.hlapi import *

# Params check
if len(sys.argv) != 3:
    print("usage: " + sys.argv[0] + " <community> <hostname>")
else:
    print("Requesting...\n\n")
    hostname = sys.argv[2]
    community = sys.argv[1]

# hostname
    errInd, errName, errIndex, varBinds = next(getCmd(SnmpEngine(), CommunityData(community, mpModel=0), UdpTransportTarget((hostname, 161)), ContextData(), ObjectType(ObjectIdentity('iso.3.6.1.2.1.1.5.0'))))

    if errInd:
        print(errInd)
    elif errName:
        print('Errore %s@[%s]' % (errName, varBinds[int(errIndex) - 1][0]))
    else:
        targetname = varBinds[0].prettyPrint().split("=")[1].strip()
        print(targetname)

# hostname
    errInd, errName, errIndex, varBinds = next(getCmd(SnmpEngine(), CommunityData(community, mpModel=0), UdpTransportTarget((hostname, 161)), ContextData(), ObjectType(ObjectIdentity('iso.3.6.1.2.1.1.1.0'))))

    if errInd:
        print(errInd)
    elif errName:
        print('Errore %s@[%s]' % (errName, varBinds[int(errIndex) - 1][0]))
    else:
        target = varBinds[0].prettyPrint().split("=")[1].strip()
        print("\t" + target)

# ssCpuIdle
    errInd, errName, errIndex, varBinds = next(getCmd(SnmpEngine(), CommunityData(community, mpModel=0), UdpTransportTarget((hostname, 161)), ContextData(), ObjectType(ObjectIdentity('UCD-SNMP-MIB', 'ssCpuIdle', 0))))

    if errInd:
        print(errInd)
    elif errName:
        print('Errore %s@[%s]' % (errName, varBinds[int(errIndex) - 1][0]))
    else:
        cpuIdle = varBinds[0].prettyPrint().split("=")[1].strip()
        print("\tCPU\t\t" + cpuIdle + "%")

# memTotalReal
    errInd, errName, errIndex, varBinds = next(getCmd(SnmpEngine(), CommunityData(community, mpModel=0), UdpTransportTarget((hostname, 161)), ContextData(), ObjectType(ObjectIdentity('UCD-SNMP-MIB', 'memTotalReal', 0))))
    
    if errInd:
        print(errInd)
    elif errName:
        print('Errore %s@[%s]' % (errName, varBinds[int(errIndex) - 1][0]))
    else:
        memTotal = varBinds[0].prettyPrint().split("=")[1].strip()
        print("\tMem total\t" + memTotal + " KB")
    
# memAvailReal
    errInd, errName, errIndex, varBinds = next(getCmd(SnmpEngine(), CommunityData(community, mpModel=0), UdpTransportTarget((hostname, 161)), ContextData(), ObjectType(ObjectIdentity('UCD-SNMP-MIB', 'memAvailReal', 0))))
    
    if errInd:
        print(errInd)
    elif errName:
        print('Errore %s@[%s]' % (errName, varBinds[int(errIndex) - 1][0]))
    else:
        memAvail = varBinds[0].prettyPrint().split("=")[1].strip()
        print("\tMem avail.\t" + memAvail + " KB")

# loop
for i in range(5):
    sleep(1)
    print("\n" + str(i+1) + "\t######")
    errInd, errName, errIndex, varBinds = next(getCmd(SnmpEngine(), CommunityData(community, mpModel=0), UdpTransportTarget((hostname, 161)), ContextData(), ObjectType(ObjectIdentity('UCD-SNMP-MIB', 'ssCpuIdle', 0))))

    if errInd:
        print(errInd)
    elif errName:
        print('Errore %s@[%s]' % (errName, varBinds[int(errIndex) - 1][0]))
    else:
        cpuIdle = varBinds[0].prettyPrint().split("=")[1].strip()
        print("\tCPU\t\t" + cpuIdle + "%")

    errInd, errName, errIndex, varBinds = next(getCmd(SnmpEngine(), CommunityData(community, mpModel=0), UdpTransportTarget((hostname, 161)), ContextData(), ObjectType(ObjectIdentity('UCD-SNMP-MIB', 'memAvailReal', 0))))
    
    if errInd:
        print(errInd)
    elif errName:
        print('Errore %s@[%s]' % (errName, varBinds[int(errIndex) - 1][0]))
    else:
        memAvail = varBinds[0].prettyPrint().split("=")[1].strip()
        print("\tMem\t" + memAvail + "/" + memTotal + " KB")


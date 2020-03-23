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
if len(sys.argv) < 3:
    print("usage:\t\t" + sys.argv[0] + " community hostname [port]")
    print("example:\t" + sys.argv[0] + " public demo.snmplabs.com")
else:
    hostname = sys.argv[2]
    community = sys.argv[1]
    if len(sys.argv) >= 4:
        port = int(sys.argv[3])
    else:
        port = 161    
    print("Requesting " + hostname + ":" + str(port) + "\n")

# hostname
    errInd, errName, errIndex, varBinds = next(getCmd(SnmpEngine(), CommunityData(community, mpModel=0), UdpTransportTarget((hostname, port)), ContextData(), ObjectType(ObjectIdentity('iso.3.6.1.2.1.1.5.0'))))

    if errInd:
        print(errInd)
    elif errName:
        print('Errore %s@[%s]' % (errName, varBinds[int(errIndex) - 1][0]))
    else:
        targetname = varBinds[0].prettyPrint().split("=")[1].strip()
        print(targetname)

# hostname
    errInd, errName, errIndex, varBinds = next(getCmd(SnmpEngine(), CommunityData(community, mpModel=0), UdpTransportTarget((hostname, port)), ContextData(), ObjectType(ObjectIdentity('iso.3.6.1.2.1.1.1.0'))))

    if errInd:
        print(errInd)
    elif errName:
        print('Errore %s@[%s]' % (errName, varBinds[int(errIndex) - 1][0]))
    else:
        target = varBinds[0].prettyPrint().split("=")[1].strip()
        print("\t" + target)

# ssCpuIdle
    print("\tCPU\t\t", end = '')
    errInd, errName, errIndex, varBinds = next(getCmd(SnmpEngine(), CommunityData(community, mpModel=0), UdpTransportTarget((hostname, port)), ContextData(), ObjectType(ObjectIdentity('UCD-SNMP-MIB', 'ssCpuIdle', 0))))

    if errInd:
        print(errInd)
    elif errName:
        print('Errore %s@[%s]' % (errName, varBinds[int(errIndex) - 1][0]))
    else:
        cpuIdle = varBinds[0].prettyPrint().split("=")[1].strip()
        print(cpuIdle + "%")

# memTotalReal
    print("\tMem total\t", end = '')
    errInd, errName, errIndex, varBinds = next(getCmd(SnmpEngine(), CommunityData(community, mpModel=0), UdpTransportTarget((hostname, port)), ContextData(), ObjectType(ObjectIdentity('UCD-SNMP-MIB', 'memTotalReal', 0))))
    
    if errInd:
        print(errInd)
    elif errName:
        print('Errore %s@[%s]' % (errName, varBinds[int(errIndex) - 1][0]))
    else:
        memTotal = varBinds[0].prettyPrint().split("=")[1].strip()
        print(memTotal + " KB")
    
# memAvailReal
    print("\tMem avail.\t", end = '')
    errInd, errName, errIndex, varBinds = next(getCmd(SnmpEngine(), CommunityData(community, mpModel=0), UdpTransportTarget((hostname, port)), ContextData(), ObjectType(ObjectIdentity('UCD-SNMP-MIB', 'memAvailReal', 0))))
    
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
        print("\n" + str(i+1) + "\t######")
        print("\tCPU\t\t", end = '');
        errInd, errName, errIndex, varBinds = next(getCmd(SnmpEngine(), CommunityData(community, mpModel=0), UdpTransportTarget((hostname, port)), ContextData(), ObjectType(ObjectIdentity('UCD-SNMP-MIB', 'ssCpuIdle', 0))))

        if errInd:
            print(errInd)
        elif errName:
            print('Errore %s@[%s]' % (errName, varBinds[int(errIndex) - 1][0]))
        else:
            cpuIdle = varBinds[0].prettyPrint().split("=")[1].strip()
            print(cpuIdle + "%")

        print("\tMem\t\t", end = '')
        errInd, errName, errIndex, varBinds = next(getCmd(SnmpEngine(), CommunityData(community, mpModel=0), UdpTransportTarget((hostname, port)), ContextData(), ObjectType(ObjectIdentity('UCD-SNMP-MIB', 'memAvailReal', 0))))
        
        if errInd:
            print(errInd)
        elif errName:
            print('Errore %s@[%s]' % (errName, varBinds[int(errIndex) - 1][0]))
        else:
            memAvail = varBinds[0].prettyPrint().split("=")[1].strip()
            print(memAvail + "/" + memTotal + " KB")


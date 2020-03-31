#!/usr/bin/python3

# #####
#
# Documentation
# Author: Federico Matteoni
# This is a simple script that queries a SNMP server and
# reads some simple informations. The script populates a RRD database
# and plots a graph
#
# Installation
# sudo apt install python3 python3-pip rrdtool librrd8 librrd-dev
# pip3 install pysnmp
# pip3 install rrdtool
# 
# Usage
# python3 snmptest.py community hostname [port]
#
# Example
# python3 snmptest.py public demo.snmplabs.com
#
# #####

# Imports
import sys
import rrdtool as rrd
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
    rrdname = "cpu_" + hostname + ".rrd"
    try:
        f = open(rrdname)
        f.close()
    except FileNotFoundError:
        print("Creating rrd \"" + rrdname + "\"")
        rrd.create(
            rrdname,
            "--start", "now",
            "--step", "1",
            "RRA:AVERAGE:0.5:1:3600",
            "DS:cpu:GAUGE:5:0:100")
    print("Requesting " + hostname + ":" + str(port) + "\n")
    now = datetime.now()

# hostname
    currtime = now.strftime("%H.%M.%S") #Timestamp
    errInd, errName, errIndex, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData(community, mpModel=0),
               UdpTransportTarget((hostname, port)),
               ContextData(),
               ObjectType(ObjectIdentity('iso.3.6.1.2.1.1.5.0')) #SNMPv2-MIB::sysName.0
               )
        )

    print(currtime + "\n")
    if errInd:
        print(errInd)
    elif errName:
        print('Error %s@[%s]' % (errName, varBinds[int(errIndex) - 1][0]))
    else:
        targetname = varBinds[0].prettyPrint().split("=")[1].strip()
        print(targetname)

# hostdescr
    errInd, errName, errIndex, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData(community, mpModel=0),
               UdpTransportTarget((hostname, port)),
               ContextData(),
               ObjectType(ObjectIdentity('iso.3.6.1.2.1.1.1.0')) #SNMPv2-MIB::sysDescr.0
               )
        )

    if errInd:
        print(errInd)
    elif errName:
        print('Error %s@[%s]' % (errName, varBinds[int(errIndex) - 1][0]))
    else:
        target = varBinds[0].prettyPrint().split("=")[1].strip()
        print("\t" + target)

# uptime
    print("\tUptime\t", end = '')
    errInd, errName, errIndex, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData(community, mpModel=0),
               UdpTransportTarget((hostname, port)),
               ContextData(),
               ObjectType(ObjectIdentity('iso.3.6.1.2.1.1.3.0')) #DISMAN-EVENT-MIB::sysUpTimeInstance
               )
        )

    if errInd:
        print(errInd)
    elif errName:
        print('Error %s@[%s]' % (errName, varBinds[int(errIndex) - 1][0]))
    else:
        ticks = int(varBinds[0].prettyPrint().split("=")[1].strip())
        secs = ticks/100
        uptimestr = timedelta(seconds=secs)
        print("\t" + str(uptimestr) + " (" + str(ticks) + ")")

# ssCpuIdle
    ucdCpu = False
    print("\tCPU\t\t", end = '')
    errInd, errName, errIndex, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData(community, mpModel=0),
               UdpTransportTarget((hostname, port)),
               ContextData(),
               ObjectType(ObjectIdentity('UCD-SNMP-MIB', 'ssCpuIdle', 0))
               )
        )

    if errInd:
        print(errInd)
    elif errName:
        print('Error %s@[%s]' % (errName, varBinds[int(errIndex) - 1][0]))
    else:
        ucdCpu = True
        cpuIdle = varBinds[0].prettyPrint().split("=")[1].strip()
        rrd.update([rrdname, "--template", "cpu", "N:" + str(100 - int(cpuIdle))])
        print(str(100 - int(cpuIdle)) + "%")

# memTotalReal
    ucdMemTot = False
    print("\tMem total\t", end = '')
    errInd, errName, errIndex, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData(community, mpModel=0),
               UdpTransportTarget((hostname, port)),
               ContextData(),
               ObjectType(ObjectIdentity('UCD-SNMP-MIB', 'memTotalReal', 0))
               )
        )
    
    if errInd:
        print(errInd)
    elif errName:
        print('Error %s@[%s]' % (errName, varBinds[int(errIndex) - 1][0]))
    else:
        ucdMemTot = True
        memTotal = varBinds[0].prettyPrint().split("=")[1].strip()
        print(memTotal + " KB")
    
# memAvailReal
    ucdMemAvail = False
    print("\tMem avail.\t", end = '')
    errInd, errName, errIndex, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData(community, mpModel=0),
               UdpTransportTarget((hostname, port)),
               ContextData(),
               ObjectType(ObjectIdentity('UCD-SNMP-MIB', 'memAvailReal', 0))
               )
        )
    
    if errInd:
        print(errInd)
    elif errName:
        print('Error %s@[%s]' % (errName, varBinds[int(errIndex) - 1][0]))
    else:
        ucdMemAvail = True
        memAvail = varBinds[0].prettyPrint().split("=")[1].strip()
        print(memAvail + " KB")

# loop
    sleep(1)
    print("\n\n\n") # Moving down to not erase previous output
    for i in range(60):
        start = datetime.now().timestamp()
        now = datetime.now()
        currtime = now.strftime("%H.%M.%S")
        # "\033[K" clear to the end of the line
        # "\033[F" moves cursor up one line
        print("\r\033[F\033[K\033[F\033[K\033[F" + str(i+1) + " (" + currtime + ")")
        print("\tCPU\t\t", end = '');
        if ucdCpu:
            errInd, errName, errIndex, varBinds = next(
                getCmd(SnmpEngine(),
                       CommunityData(community, mpModel=0),
                       UdpTransportTarget((hostname, port)),
                       ContextData(),
                       ObjectType(ObjectIdentity('UCD-SNMP-MIB', 'ssCpuIdle', 0))
                       )
                )

            if errInd:
                print(errInd)
            elif errName:
                print('Error %s@[%s]' % (errName, varBinds[int(errIndex) - 1][0]))
            else:
                cpuIdle = varBinds[0].prettyPrint().split("=")[1].strip()
                rrd.update([rrdname, "--template", "cpu", "N:" + str(100 - int(cpuIdle))])
                print(str(100 - int(cpuIdle)) + "%")
        else:
            print("skip")


        print("\tMem\t\t", end = '')
        if ucdMemAvail:
            errInd, errName, errIndex, varBinds = next(
                getCmd(SnmpEngine(),
                       CommunityData(community, mpModel=0),
                       UdpTransportTarget((hostname, port)),
                       ContextData(),
                       ObjectType(ObjectIdentity('UCD-SNMP-MIB', 'memAvailReal', 0))
                       )
                )
            
            if errInd:
                print(errInd)
            elif errName:
                print('Error %s@[%s]' % (errName, varBinds[int(errIndex) - 1][0]))
            else:
                memAvail = varBinds[0].prettyPrint().split("=")[1].strip()
                print(memAvail + "/" + memTotal + " KB")
        else:
            print("skip")
        end = datetime.now().timestamp()
        slptm = 1 - (end - start)/1000
        sleep(slptm)

    # RRD Graph
    graphv_args = [
        rrdname + '.png',
        '--title', hostname + " CPU",
        '--start', 'now-1h',
        '--end', 'now',
        '--slope-mode',
        '--font', 'DEFAULT:7:',
        '--upper-limit', '100',
        '--lower-limit', '0',
        'DEF:CPU=' + rrdname + ':cpu:MAX',
        'LINE1:CPU#0000FF:CPU',
        'GPRINT:CPU:LAST:Last value\: %5.2lf'
    ]
    
    rrd.graphv(*graphv_args)
    print("CPU graph: " + rrdname + ".png")


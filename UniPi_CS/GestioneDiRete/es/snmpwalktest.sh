#!/bin/bash

GRP=$1
HST=$2

if [[ ! ( $1 && $2 ) ]]; then
	echo "usage: $0 <group> <hostname>"
	exit
fi

hoststr=$(snmpwalk -v 1 -OvQU -c $1 $2 iso.3.6.1.2.1.1.1.0)
hostnamestr=$(snmpwalk -v 1 -OvQU -c $1 $2 iso.3.6.1.2.1.1.5.0)
uptimestr=$(snmpwalk -v 1 -Ovq -c $1 $2 iso.3.6.1.2.1.25.1.1.0)
cpustatusstr=$(snmpget -v 1 -OvQU -c $1 $2 UCD-SNMP-MIB::ssCpuIdle.0)
memavailstr=$(snmpget -v 1 -OvQU -c $1 $2 UCD-SNMP-MIB::memAvailReal.0)
memtotalstr=$(snmpget -v 1 -OvQU -c $1 $2 UCD-SNMP-MIB::memTotalReal.0)

echo "Target name	$hostnamestr"
echo "Host		$hoststr"
echo "Uptime		$(echo $uptimestr | cut -d':' -f 1)d $(echo $uptimestr | cut -d':' -f 2)h $(echo $uptimestr | cut -d':' -f 3)m"
echo "CPU		$cpustatusstr %"
echo "MEM		$memavailstr KB/ $memtotalstr KB"

import pyshark
import json
from pprint import pprint

cap = pyshark.FileCapture("20210302_pkts.pcap")

# Stampa pacchetto
# print(cap[0])
# cap[0].pretty_print()

# Stampa attributi primo e secondo layer pkt
# pprint(vars(cap[0]))
# pprint(vars(cap[0][0]))



list_cpkts = []
for pkt in cap:
    if "IP" in pkt:
        if pkt[2]._layer_name == "tcp" or pkt[2]._layer_name == "udp":
            timestamp = pkt.sniff_timestamp
            pkt_len = pkt.length
            protocol = pkt[2]._layer_name
            ip_src = pkt.ip.src
            ip_dst = pkt.ip.dst
            port_src = pkt[2].srcport
            port_dst = pkt[2].dstport
            cpkt = {
            "timestamp": timestamp,
            "pkt_len" : pkt_len,
            "protocol" : protocol,
            "ip_src" : ip_src,
            "ip_dst" : ip_dst,
            "port_src" : port_src,
            "port_dst" : port_dst
            }
        list_cpkts.append(cpkt)

json_list_cpkts = json.dumps(list_cpkts, indent=4)
print(json_list_cpkts)

list_cpkts0 = json.loads(json_list_cpkts)
print(list_cpkts0)

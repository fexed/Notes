#!\bin\python3

from scapy.all import *
from scapy.utils import PcapWriter
from collections import Counter
from datetime import datetime
import argparse

dt = datetime.now()
pcap = str(dt.year) + str(dt.month) + str(dt.day) + "_pkts.pcap"
pktdump = PcapWriter(pcap, append=True, sync=True)

# Params parsing
def parse_args():
    parser = argparse.ArgumentParser(
        description='Simple script that captures packets and writes trivial data onto a dated pcap')
    parser.add_argument('--interface', type=str, required=False,
                        default='wlp1s0',
                        help='interface from which to sniff packets')
    return parser.parse_args()

def captured(packet):
    global pkts
    global packet_counts
    pkts += 1 # Conteggio
    pktdump.write(packet) # Scrittura su pcap
    # BUG?: se pacchetti ricevuti troppo velocemente, pcap diviene malformato.
    # Cioè in lettura con pyshark dà XMLSyntaxError('invalid character in attribute value, line x, column y')
    # rendendo impossibile lettura del resto del pcap anche se ha ulteriori pacchetti.
    try:
        return f"\r\033[F\033[K #{str(pkts)}: {packet[0][1].src} -> {packet[0][1].dst}" # Output
    except Exception as ex:
        return f"\r\033[F\033[K" + repr(ex) # Output errore

packet_counts = Counter() # Contatore
args = parse_args()
iface = args.interface # Interfaccia da cui ascoltare, default wlp1s0
print("Sniffing on " + iface) # Output
pkts = 0
sniff(prn=captured) # Ascolta e scrive su pcap ogni pacchetto tramite captured(packet)
print(str(pkts) + " packets") # Riepilogo

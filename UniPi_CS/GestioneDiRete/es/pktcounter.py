import pyshark
import rrdtool as rrd
import signal
import sys

rrdname = "streamingpackets.rrd"

try:
    f = open(rrdname)
    f.close()
except FileNotFoundError:
    print("Creating rrd \"" + rrdname + "\"")
    rrd.create(
        rrdname,
        "--start", "now",
        "--step", "5",
        "RRA:AVERAGE:0.5:1:3600",
        "DS:packets:COUNTER:10:0:9999999")
print("Using " + rrdname)

def signal_handler(sig, frame):
    graphv_args = [
        rrdname + '.png',
        '--title', "Packets count",
        '--start', 'now-5h',
        '--end', 'now',
        '--slope-mode',
        '--font', 'DEFAULT:7:',
        'DEF:PKT=' + rrdname + ':packets:MAX',
        'LINE1:PKT#0000FF:PKT',
        'GPRINT:PKT:LAST:Ultimo valore\: %5.2lf'
    ]
    print("\nGraph image: " + rrdname + ".png")
    rrd.graphv(*graphv_args)
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

pkts = 0
def captured(packet):
    global pkts
    pkts += 1
    print("\r\033[F\033[K Captured: " + str(pkts))
    rrd.update([rrdname, "--template", "packets", "N:" + str(pkts)])

capture = pyshark.LiveCapture(interface='wlp1s0')

capture.apply_on_packets(captured)

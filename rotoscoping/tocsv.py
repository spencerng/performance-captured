import argparse, random, sys, time, json

from pythonosc import udp_client

parser = argparse.ArgumentParser()
parser.add_argument("--ip", default="127.0.0.1", help="The ip of the OSC server")
parser.add_argument("--port", type=int, default=6789, help="The port the OSC server is listening on")
args = parser.parse_args()

client = udp_client.SimpleUDPClient(args.ip, args.port)

first = True
for line in sys.stdin:
	a = json.loads(line)
	if (first):
		first = False
		print(",".join(a.keys()))
	print(",".join([str(x) for x in a.values()]))



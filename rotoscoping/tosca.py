import argparse, random, sys, time, json

from pythonosc import udp_client
print("go...?")

parser = argparse.ArgumentParser()
parser.add_argument("--ip", default="127.0.0.1", help="The ip of the OSC server")
parser.add_argument("--port", type=int, default=6789, help="The port the OSC server is listening on")
args = parser.parse_args()

client = udp_client.SimpleUDPClient(args.ip, args.port)

while True:
	line = sys.stdin.readline()
	for k,v in json.loads(line).items():
		print("%s=%s" % (k,v))
		if (len(str(v))>100):
			println(" (to long to send over osc, ignoring) ")
		client.send_message("/"+k, [v])



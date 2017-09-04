#!/usr/bin/python

from pydhcplib.dhcp_network import *
from datetime import datetime
import requests
import time

MAGIC_FORM_URL = 'http://api.cloudstitch.com/tonyspurs/simple-form/datasources/sheet'

currently_showering = False
previous_time = None

def record_event():
    global currently_showering, previous_time

    current_time = datetime.now()
    time_diff = ''
    run_again = False

    if currently_showering:
        print "Fresh again"
        try:
            time_diff = get_delta(current_time, previous_time)
        except MissedError:
            MissedErrorMsg()
            time_diff = "20:00"
            run_again = True
        print 'Showering time=%s' % time_diff
        previous_time = None
    else:
        print "Washing dirt off armpit"
        previous_time = current_time

    if currently_showering:
        data = {
            "Date": current_time.strftime("%d-%m-%Y %H:%M:%S"),
            "Shower Time": time_diff
        }
        requests.post(MAGIC_FORM_URL, data)
        #response = urllib.urlopen(MAGIC_FORM_URL, data=urllib.urlencode(data))

    currently_showering = False if currently_showering else True
    
    if run_again:
        record_event()

netopt = {'client_listen_port':"68", 'server_listen_port':"67", 'listen_address':"0.0.0.0"}

class Server(DhcpServer):
	def __init__(self, options, dashbuttons):
		DhcpServer.__init__(self, options["listen_address"],
								options["client_listen_port"],
								options["server_listen_port"])
		self.dashbuttons = dashbuttons

	def HandleDhcpRequest(self, packet):
		mac = self.hwaddr_to_str(packet.GetHardwareAddress())
		self.dashbuttons.press(mac)


	def hwaddr_to_str(self, hwaddr):
		result = []
		hexsym = ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f']
		for iterator in range(6) :
			result += [str(hexsym[hwaddr[iterator]/16]+hexsym[hwaddr[iterator]%16])]
		return ':'.join(result)

class DashButtons():
	def __init__(self):
		self.buttons = {}

	def register(self, mac, function):
		self.buttons[mac] = function

	def press(self, mac):
		if mac in self.buttons:
			self.buttons[mac]()
			return True
		return False

def get_delta(current, previous):
    
    delta = current - previous
    minutes, seconds = divmod(delta.seconds, 60)
    if minutes > 30:
        raise MissedError()
    return "%s:%s" % (minutes, seconds)

class MissedError(Exception):
    pass

def MissedErrorMsg():
    print "Someone forgot to pressed the button the previous time, set to default average."

		
dashbutton = DashButtons()
dashbutton.register("ac:63:be:85:5f:3a", record_event)
#Tony_dashbutton = DashButtons("ac:63:be:4b:12:67", record_event("Tony"))
#Tony_dashbutton = register("")
server = Server(netopt, dashbutton)

while True :
    server.GetNextDhcpPacket()
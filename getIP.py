# Utility function to look up the current IP address on either the LAN or WAN
#

def IP():
	# Get IP via ip addr show

    from subprocess import *
    import os

    cmd_eth0 = "ip addr show eth0 | grep inet | awk '{print $2}' | cut -d/ -f1"
    cmd_wan0 = "ip addr show wlan0 | grep inet | awk '{print $2}' | cut -d/ -f1"


    p = Popen(cmd_eth0, shell=True, stdout=PIPE)
    output = p.communicate()[0]

    if len(output) < 1:
        p = Popen(cmd_wan0, shell=True, stdout=PIPE)
        output = p.communicate()[0]

	if len(output) < 1:
		output = "not available"

    return output


def IP2():
	# Get IP via SOCKET

	import socket, fcntl, struct

	sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	try:
		ifn = 'wlan0'
	        return socket.inet_ntoa(fcntl.ioctl(sck.fileno(),0x8915,struct.pack('256s', ifn[:15]))[20:24])
	except:
		try:
			ifn = 'eth0'
			return socket.inet_ntoa(fcntl.ioctl(sck.fileno(),0x8915,struct.pack('256s', ifn[:15]))[20:24])
		except:
			return "not available"

def IP3():
	# Get IP via SOCKET... the easy way...
    # But it doesnt work on the pi?

    import socket

    try:
	   return socket.gethostbyname(socket.gethostname())
    except:
        return "not available"



if __name__ == '__main__':
	# test, test

    ipaddr = IP()
    print 'IP {}'.format(ipaddr)
    ipaddr = IP2()
    print 'IP {}'.format(ipaddr)
    ipaddr = IP3()
    print 'IP {}'.format(ipaddr)





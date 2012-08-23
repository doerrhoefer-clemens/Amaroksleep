#!/usr/bin/python
import dbus, gobject, signal, sys, getopt
from dbus.mainloop.glib import DBusGMainLoop

#init
counter = 1
signalmatch = None

dbus_loop = DBusGMainLoop()
bus = dbus.SessionBus(mainloop=dbus_loop)
loop = gobject.MainLoop()

pproxy = bus.get_object('org.freedesktop.PowerManagement', '/modules/powerdevil')
power = dbus.Interface(pproxy, dbus_interface='org.kde.PowerDevil')

#Unregister DBUS Signal Handler and exit program
def quithandler(signum, frame):
	global power, signalmatch
	print 'Powermanager to Powersave'
	power.setProfile('Powersave')
	print 'Removing D-BUS signal'
	signalmatch.remove()
	print 'Good Bye'
	quit()

#Put computer to sleep if end of counter was reached
def sleephandler(item):
	global power, counter
	counter = counter - 1
	if counter == 0:
		signal.signal(signal.SIGALRM, quithandler)
		signal.alarm(10)
		power.suspend(2)

#Print Help
def printUsage():
	print sys.argv[0] +u' [OPTION]'
	print u'OPTIONS'
	print u'-n			Specify the number of titles to be played. Argument must be an integer (default=1)'
	print u'-h, --help		Print this help and exit'
	
#Unix getopts
def readOptions():
	global counter
	opts, args = getopt.getopt(sys.argv[1:], "n:h", ["help"])
	for o, a in opts:
		if o == '-n':
			try:
				counter = int(a)
			except:
				printUsage()
				quit()
		if o in('-h',"--help"):
			printUsage()
			quit()		

def main():
	global signalmatch, power
	try:
		readOptions()
		power.setProfile('Performance')
		signalmatch = bus.add_signal_receiver(sleephandler, 
				signal_name='TrackChange', 
				dbus_interface='org.freedesktop.MediaPlayer', 
				bus_name='org.kde.amarok', 
				path='/Player')
		loop.run()
	except (KeyboardInterrupt, SystemExit):
		if signalmatch != None:
			print 'Powermanager to Powersave'
			power.setProfile('Powersave')
			print 'Removing D-BUS signal'
			signalmatch.remove()
			print 'Good Bye'
			quit()

#run
if __name__== '__main__':
	main()

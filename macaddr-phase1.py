
##Network Automation code to perform Network IOS router's peer devices Vendor(Phase1)##

"""
1. First scans its own network(Network Automation docker) to find all active hosts running - Parallel processing with threading
2. SSH into each device using Napalm and get output of show arp - Parallel processing with threading
3. Grab mac addr and ip from each device and save it in a Dictionary
4. Use Dictionary to perform Vendor MAC addr lookup

**still upgrading code as I type
*Setup contains Network Automation docker connected to Few routers and Internet docker via Hub - using dhcp alloted ip's
"""

##Modules import
import pprint
from getpass import getpass
from napalm import get_network_driver
import json
import requests
import subprocess
import re
import threading
from netaddr import IPNetwork
from netaddr import IPRange



#fucntion to use threading
def run_ssh(ip_active):
    print "\nEnter common password to access each device"
    password = getpass()
    threads = []
    for ip in ip_active:
        th = threading.Thread(target = thread_device, args =([ip,password]))
        th.start()
        threads.append(th)
    for th in threads:
        th.join()


#function to ssh each device and get router output
def thread_device(ip,password):
    driver = get_network_driver('ios')
    device = driver(ip, 'admin', password)
    device.open()

    ##ARP fetch and print code
    arp = device.get_arp_table()
    print "\n\n*******************************************"
    print "Printing Arp Table for host '{}'".format(ip)
    print (json.dumps(arp, sort_keys=True, indent=4))

    dict = {}
    for i in arp:
        #if i["age"] != 0.0:    #ignoring interface mac address
        dict[i["ip"]] = i["mac"]

    #print dict
    print "\nPerforming Peer devices vendor lookup for host '{}'\n".format(ip)
    mac_url = 'https://macvendors.co/api/%s'
    for key, value in dict.iteritems():
        values = value.encode("ascii","replace") #changing unicode type to str
        print ("Vendor details for device with ip '{}' is".format(key))
        mac_find = requests.get(mac_url % "values")
        pprint.pprint(mac_find.json())
        print ("\n")


#Function to scan Device(Network Automation docker) network
def scan_net():
    print "Performing scan in my network..This might take some time."
    inet = subprocess.check_output(['ifconfig','eth1'])
    regx = re.sub("\s+"," ", inet)  #replacing multiple spaces with one
    x = re.search(r"(.+) inet addr:(.+?) (.+) Mask:(.+?) (.+)", regx)
    iprange = IPNetwork(x.group(2),x.group(4))
#   print iprange
#   for ip in iprange.iter_hosts(): #code to get all the hosts in the n/w
#       print ip
    ip_active = active_hosts(iprange, x.group(2))   #calling function to find live hosts in n/w
    return (ip_active)


#Function to call threading to find active device in n/w
def active_hosts(iprange,myself):
    threads = []    
    ip_active = []
    for ip in iprange.iter_hosts():
        th = threading.Thread(target = ping_host, args=(ip, ip_active))
        th.start()
        threads.append(th)
    for th in threads: 
        th.join()
#   print ip_active
    for ip in ip_active:    #removing my own ip from the list
        if ip == myself:
            ip_active.remove(ip)
            ip_active.remove('192.168.122.1')   #for now removing gateway ip manually
#   print "List of active hosts in my network are {}".format(ip_active)
    return (ip_active)


#Function to ping each host - generated list of active hosts
def ping_host(ip, ip_active):
    ip = str(ip)
    ping_check = subprocess.Popen(["ping","-c","1",ip], stdout=subprocess.PIPE)
    ping_check.wait()
    if (ping_check.returncode == 0):
        ip_active.append(ip)


#MAIN Function
if __name__ == "__main__":
    ip_active = scan_net()
    print "List of active hosts in my network {}".format(ip_active)
    run_ssh(ip_active)

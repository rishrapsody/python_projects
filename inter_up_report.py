‘’’

FINAL SCRIPT

This script will performs below tests:

1. Checks its network to find all active/alive devices(scanning) —> Ping with Threading
2. Run multithreading to SSH into each device in parallel
3. Fetch output of “show ip int brief” from each device
4. Get number and name of interfaces in UP/UP state and print them
All the above are done in parallel using Threading feature of Python to save time
‘’’





import subprocess

import re

from netaddr import IPNetwork

from netaddr import IPRange

import threading

from netmiko import ConnectHandler

import pprint



def scan_net():

inet = subprocess.check_output(['ifconfig','eth0'])

regx = re.sub(" +"," ", inet)

regx = re.sub("\n","", regx)

x = re.search(r"(.+) inet addr:(.+?) (.+) Mask:(.+?) (.+)", regx)



#not using the below code as i have limited number of active devices in network

#	iprange = IPNetwork(x.group(2),x.group(4))

#	print(iprange)

iprange = IPRange('192.168.1.1','192.168.1.10')

threads = []

list1 = []

for i in iprange:

t= threading.Thread(target = thread_test, args = (i,list1))

t.start()

threads.append(t)



for t in threads:

t.join()



return(list1,x.group(2))



def thread_test(i,list1):

i=str(i)

ping_check = subprocess.Popen(["ping","-c","1",i], stdout=subprocess.PIPE)

ping_check.wait()

if (ping_check.returncode == 0):

print("%s .." %i)

list1.append(i)

else:

print("%s is DOWN" %i)



def ssh_ip(list):

#threading for ssh

threads_ssh = []

dict = {}

for ip in list:

x = threading.Thread(target = ssh_thread, args = (ip, dict))

x.start()

threads_ssh.append(x)



for x in threads_ssh:

x.join()

return(dict)



#thread function

def ssh_thread(ip, dict):



f=open(r"file_exercise.txt", "rb")

file=f.read()

f.close()

lists=file.split("\n\n")

for list in lists:

inner_list=list.split("\n")

if(inner_list[0] == ip):

print(" ")

print "Fetching data from file for " + inner_list[0]

print("device type: " + inner_list[1])

print("username: " + inner_list[2])

print("password: " + inner_list[3])

print("secret: " + inner_list[4])

print("Logging into device and fetching data.............")

device = ConnectHandler(device_type=inner_list[1], ip=ip, username=inner_list[2], password=inner_list[3], secret=inner_list[4])

device.enable()

device.config_mode()

device.send_command_timing('terminal length 0')

device.exit_config_mode()

output = device.send_command("show ip interface brief")

device.disconnect()

dict[ip] = output







#analyzing data from dictionary

def analyse_data(dict_out):

final = {}

threads_dict = []

for key,value in dict_out.iteritems():

temp_value = value

temp_key = key

q = threading.Thread(target = dict_thread, args = (temp_value,temp_key,final))

q.start()

threads_dict.append(q)



for q in threads_dict:

q.join()

return(final)



#threading for dictionary

def dict_thread(temp_value,temp_key,final):

out2 = temp_value.split("\n")

print("\n")

out2.pop(0)

temp = []

for line in out2:

line=line.encode('ascii','ignore')

line = re.sub(' +',' ', line)

regx =  re.search(r"(.+?) (.+) up up", line)

if (bool(regx) == True):

data = regx.group(1)

temp.append(data)

final[temp_key] = temp



#printing output

def printing(ff):

for key, value in ff.iteritems():

print(" ")

print '#' * 40

print("Router: " + key)

print "This Router has %d interfaces in UP/UP state" %(len(value))

print("They are: ")

for i in value:

print(i)

print '#' * 40

print(" ")







if __name__ == "__main__":



#scanning network and returning list of alive router

list,me = scan_net()

print(" ")

print("List of devices up in my network are:")

print(list)

print(" ")

print("My ip is:")

print(me)

for  i,ip in enumerate(list):

if(ip == me):

list.pop(i)

print(" ")

print("IPs of devices to ssh into:")

print(list)



#ssh into router from list using threading

dict_data = ssh_ip(list)

#	pprint.pprint(dict_data)



#sending dictionary to analyse data

ff = analyse_data(dict_data)

#	pprint.pprint(ff)



#final print

printing(ff)

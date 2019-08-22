#! /usr/bin/env python

"""
author=rishabh.parihar
author_email=rishabh.parihar@aryaka.com
version=1.0
"""

import ipaddress
from inter_dict import dict_inter_name
from pprint import pprint
from jinja2 import Environment, FileSystemLoader
import argparse
from datetime import datetime
from os import system, name 



parser = argparse.ArgumentParser(
formatter_class=argparse.RawTextHelpFormatter,
description=
"""
This is Help section.
Please provide the inputs as per Standard Operation Procedure.
Sample:
Please enter customer name: wabtec
Please enter customer vrf: wabtec_vrf
Please enter POP name(eg.ASH,SIN1): ASH1			#provide POP code as per ASN
Please enter AA value(3rd octet): 50
Please enter ZZZ value(4th octet): 123
Please enter ATAN IP: 199.59.228.1
Please enter vlan id: 3123
Please enter AWS/Azure facing subinterface IP: 169.254.170.1	#Do not provide net id or broadcast
Are you looking for Azure or AWS config?: aws
Please enter AWS password: qwerty
****Your router config is ready and saved in same directory in format 'cloudtype_routerconfig_currenttime.txt****
"""
)
args = parser.parse_args()


def prep_config(dict_temp, third_octet, cloud_type):
	"""
	Router config Prep code. 
	Pick Jinja2 template as per input provided by customer.
	Trigger FileName with CloudType and Current type added in name.
	Save Router config in current working directory.
	"""

	ENV = Environment(loader=FileSystemLoader('.'))
	dict_temp = dict_temp
	if not ('inter_name' in dict_temp.keys()):	
		exit(1)
	cloud_type = cloud_type
	if (third_octet == '50'):
		if (cloud_type == 'aws'):
			baseline = ENV.get_template("aws_pri_template.j2")
		else:
			baseline = ENV.get_template("azure_pri_template.j2")
	else:
		if (cloud_type == 'aws'):
			baseline = ENV.get_template("aws_sec_template.j2")
		else:
			baseline = ENV.get_template("azure_sec_template.j2")
	datestring = datetime.strftime(datetime.now(), '%Y-%m-%d-%H-%M-%S')
	f = open(cloud_type + '_router_config_' + datestring + '.txt', 'w')
	config = baseline.render(dict_temp)
	f.write(config)
	f.close
	print("\n****Your router config is ready and saved in same directory in format 'cloudtype_routerconfig_currenttime.txt'****\n")


def clearscreen(): 
    # for windows 
    if name == 'nt': 
    	system('cls') 
  
    # for mac and linux(here, os.name is 'posix') 
    else: 
        system('clear') 

def banner():
	print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	print("**Welcome to AWS/Azure Agg Router Config Generator**")
	print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")




if __name__ == "__main__":
	
	#clear screen before asking user to provide input
	clearscreen()

	#Banner
	banner()

	#Scripts starts from here-->
	try:
		dict_temp = {}
		
		dict_temp['cust_name'] = input("Please enter customer name: ").strip().lower()
		dict_temp['customer_vrf'] = input("Please enter customer vrf: ").strip().lower()
		pop_name = input("Please enter POP name(eg.ASH,SIN1): ").strip().upper()[:3]
		

		while True:
			third_octet = input("Please enter AA value(3rd octet) in 10.96.AA.ZZZ: ")
		
			if (third_octet == '50') or (third_octet == '60'):
				dict_temp['third_octet'] = third_octet
				break
			else:
				print("Third octet should either be 50 or 60")
				print("Third octet is not as per SOP. Please try again!!")
				pass


		while True:
			fourth_octet = input("Please enter ZZZ value(4th octet) in 10.96.AA.ZZZ: ")
			if (len(fourth_octet) == 3) and (int(fourth_octet) <= 254):
					if (fourth_octet.startswith('0')):
						dict_temp['gre_src'] = fourth_octet[1:3]
						break
					else:
						dict_temp['gre_src'] = fourth_octet
						break
			elif (len(fourth_octet) == 2):
				dict_temp['gre_src'] = fourth_octet
				fourth_octet = '0' + fourth_octet
				dict_temp['fourth_octet'] = fourth_octet
				break
			elif (len(fourth_octet) == 1):
				dict_temp['gre_src'] = fourth_octet
				fourth_octet = '00' + fourth_octet
				dict_temp['fourth_octet'] = fourth_octet
				break
			else:
				print("Invalid input. Please try again. Input should be less than equal to 254")
				pass


		while True:
			try:
				dict_temp['atan_ip'] = str(ipaddress.IPv4Address(input("Please enter ATAN IP: ")))
				break
			except Exception as e:
				print(e)
				print("ATAN input is invalid. Please provide an IP and not a String")
				pass
				

		while True:
			vlan_id = input("Please enter vlan id: ").strip()
			if (len(vlan_id) == 4):
				try: 
					if (isinstance(int(vlan_id), int)) and (vlan_id.startswith('3')):
						dict_temp['vlan_id'] = vlan_id
						break
				except Exception as e:
					print(e)
					print("Vlan id should be an Integer starting with '3' and having length of 4")
					pass
			else:
				print("Vlan id should be an Integer starting with '3' and having length of 4")
				pass


		while True:
			try:
				local_agg = ipaddress.IPv4Address(input("Please enter AWS/Azure facing subinterface IP: "))
				local_agg = str(local_agg)
				last_var = int(local_agg[-1:])
				temp = last_var%2
				if (temp == 1):
					remote_last_var = last_var + 1
				else:
					remote_last_var = last_var - 1
				remote_agg = local_agg[0:-1] + str(remote_last_var)
				dict_temp['local_agg'] = str(local_agg)
				dict_temp['remote_agg'] = str(remote_agg)
				break
			except Exception as e:
				print(e)
				print("Input is incorrect or a String. Please try again")
				pass
		
		
		while True:
			cloud_service = input("Are you looking for Azure or AWS config?: ").strip().lower()
			if(cloud_service == 'aws'):
				cloud_type = 'aws'
				dict_temp['aws_pass'] = input("Please enter AWS password: ")
				break
			elif (cloud_service == 'azure'):
				cloud_type = 'azure'
#				print("No PassKey required for Azure")
				break
			else:
				print("Input should either be Azure or Aws. Please try again.")
				pass
			

		
		try:
			dict_temp['inter_name'] = dict_inter_name[pop_name]
			dict_temp['pop_name'] = pop_name
		except Exception as e:
	#		print(e)
			print("Unable to find Cloud facing interface from backend for '{}'' POP".format(pop_name))
			print("Please check the POP code. Input POP should have Juniper rtr installed")

	except KeyboardInterrupt as e:
		print("\nOops!! Exit by User.Bye!!\n")
		
			

#Calling function to prep Router config
prep_config(dict_temp,third_octet,cloud_type)













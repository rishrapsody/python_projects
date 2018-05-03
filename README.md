# python_projects
Self made codes for network automation

This section will cover python codes for network automation. 
I am currently working on Python with Napalm and Network related API's.
Still in learning phase

1. Description of 1st script

  ##Network Automation code to perform Network IOS router's peer devices Vendor(Phase1)##
1. First scans its own network(Network Automation docker) to find all active hosts running - Parallel processing with threading
2. SSH into each device using Napalm and get output of show arp - Parallel processing with threading
3. Grab mac addr and ip from each device and save it in a Dictionary
4. Use Dictionary to perform Vendor MAC addr lookup


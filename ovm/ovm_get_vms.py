#!/usr/bin/python3
'''
This script will get the list of OVS hosts and VMs Using OVM REST api.
It will also print the running state of the VMs.
To get output the from multiple OVM servers info, provide comma separated hosts list with -H switch (It will not works if you have different password on given OVM servers)
'''

import argparse, getpass, json, requests, sys
from collections import defaultdict
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class bcolors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    ENDC = '\033[0m'

# Get OVM Server's IP and credentials as script's argument
parser = argparse.ArgumentParser(description='Standard Arguments for talking to OVM Server')
parser.add_argument('-u', '--user', required=True,action='store', help='User name to use when connecting to host')
parser.add_argument('-H', '--host', required=True, action='store', help='OMV server\'s IP')
args = parser.parse_args()
args.password = getpass.getpass(prompt='Enter password for host %s and user %s: '%(args.host, args.user))

s=requests.Session()
s.verify=False
s.headers.update({'Accept': 'application/json', 'Content-Type': 'application/json'})
s.auth=(args.user,args.password)

ovm_ips = args.host.split(',')

for ovm_ip in ovm_ips:
    baseUri='https://'+ovm_ip+':7002/ovm/core/wsapi/rest'
    ## Function to get all the VMS info from OVM Server

    def get_vm_state(baseUri):
        vm=s.get(baseUri+'/Vm')
        return vm

    # Parsing the JSON response
    vm = get_vm_state(baseUri)
    vm_response = json.loads(vm.text)
    hosts_list = {}

    hosts_list = defaultdict(lambda: defaultdict(list))
    # Store Servers and Hosts info
    for vm in vm_response:
        if vm['serverId']:
            hosts_list[vm['serverId']['name']][vm['vmRunState']].append(vm['name'])
        else:
            hosts_list['Unassigned_vm'][vm['vmRunState']].append(vm['name'])

    # Sort VM lists
    for host in hosts_list:
        for state in hosts_list[host]:
            hosts_list[host][state].sort()

    #Print hosts and VMs state
    for host in hosts_list:
        ovs_server = bcolors.GREEN + ' OVS Server: ' + host + ' '  + bcolors.ENDC
        print(ovs_server.center( 100, '#'))
        for state in hosts_list[host]:
            print (bcolors.YELLOW + "State: " + state + bcolors.ENDC)
            for vm in hosts_list[host][state]:
                print (vm)

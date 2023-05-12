#!/usr/bin/python3
'''
This script will get the ESXI hosts and VMs list using Vcenter REST API.
It will also print the running state of VMs.
To get output from multiple vCenter's info, provide a comma-separated(without space) hosts list with -H switch (It will not work if you have a different password on given vCenter servers)
vCenter Server Requirement:  6.5+
'''

import argparse, getpass, json, requests, sys
from collections import defaultdict
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

__author__ = "MD. Noman"
__date__ = "02-10-2019"
__version__ = "0.1"

class bcolors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    ENDC = '\033[0m'

s=requests.Session()
s.verify=False

# Vcenter IP and credentials as scripts argument
parser = argparse.ArgumentParser(description='Standard arguments for talking to vCenter')
parser.add_argument('-u', '--user', required=True,action='store', help='User name to use when connecting to host')
parser.add_argument('-H', '--host', required=True, action='store', help='vSphere service to connect to')
args = parser.parse_args()
args.password = getpass.getpass(prompt='Enter password for host %s and user %s: '%(args.host, args.user))

vcips = args.host.split(',')


# Fget the vCenter server session
def get_vc_session(vcip,username,password):
    s.post('https://'+vcip+'/rest/com/vmware/cis/session',auth=(username,password))
    return s

# remove server session
def delete_vc_session(vcip):
    s.delete('https://'+vcip+'/rest/com/vmware/cis/session')

# get all the hosts from vCenter inventory
def get_hosts(vcip):
    hosts=s.get('https://'+vcip+'/rest/vcenter/host')
    return hosts

# get all the vms for given host from vCenter inventory
def get_vms(vcip,host):
    vms=s.get('https://'+vcip+'/rest/vcenter/vm/?filter.hosts='+host)
    return vms

for vcip in vcips:
    #Get vCenter server session
    vcsession = get_vc_session(vcip, args.user, args.password)

    # Check for any errors in HTTP response
    try:
        response = s.get('https://'+vcip+'/rest/vcenter/host')
        response.raise_for_status()
    except requests.RequestException as e:
        print(e)
        sys.exit(1)

    hosts = get_hosts(vcip)
    # parsing JSON response
    vm_response = json.loads(hosts.text)
    json_data_hosts = vm_response["value"]

    hosts_list = {}
    vms_list = {}

    # gather Hosts and VMs info
    for host in json_data_hosts:
        vms_list = defaultdict(list)
        vms = get_vms(vcip, host.get("host"))
        vm_response=json.loads(vms.text)
        json_data_vms=vm_response["value"]
        for vm in json_data_vms:
            vm_name = vm.get("name")
            power_state = vm.get("power_state")
            vms_list[power_state].append(vm_name)
            for state in vms_list:
                vms_list[state].sort()
                hosts_list[host.get("name")] = vms_list#

    # print hosts and VMs state
    for host in hosts_list:
        esxi_server = bcolors.GREEN +  'ESXI HOST: ' + host + ' '+ bcolors.ENDC
        print(esxi_server.center( 100, '#'))
        for state in hosts_list[host]:
            print (bcolors.YELLOW + "State: " + state + bcolors.ENDC)
            for vm in hosts_list[host][state]:
                print (vm)
    # Log out from current session
    delete_vc_session(vcip)

#!/usr/bin/python3

from pyVim.connect import SmartConnect
from pyVim.connect import Disconnect
from pyVmomi import vim
import ssl
from getpass import getpass
import argparse

parser = argparse.ArgumentParser(description = 'This script gets VM list from an ESXi host and keeps in a file named in {ESXiHostname}_vmlist.txt format')
parser.add_argument("-H","--hostname", action = 'store', required = True, help = 'ESXi hostname or IP')
parser.add_argument("-U","--username", action = 'store', required = True, help = 'ESXi username')

args = parser.parse_args()

hostname = args.hostname
username = args.username
password = getpass("Password: ")

security = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
security.verify_mode = ssl.CERT_NONE

try:
    connection = SmartConnect(host = hostname, user = username, pwd = password)
    print("Valid SSL certificate")
except:
    try:
        connection = SmartConnect(host = hostname, user = username, pwd = password, sslContext = security)
        print("\nInvalid SSL certificate. Ignoring...\n")
    except OSError as err:
        if err.errno == 113:
            raise SystemExit("ERROR: No route to host")
    except vim.fault.InvalidLogin:
        raise SystemExit("ERROR: Invalid username or password")

try:
    print(connection.CurrentTime(),"\n")
except:
    raise SystemExit("ERROR: Unable to connect. Please ensure, the remote host is an ESXi host")

datacenter = connection.content.rootFolder.childEntity[0]
vmList = datacenter.vmFolder.childEntity

outputFile=open(hostname+'_vmlist.txt','w')

for vm in vmList:
    info=vm.summary
    print(info.config.name,info.runtime.powerState,sep=',',file=outputFile)

print('Output has been saved to',hostname+'_vmlist.txt')

Disconnect(connection)

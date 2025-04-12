import os
import re
import time
import paramiko
from paramiko.channel import Channel
from dotenv import load_dotenv

load_dotenv('credentials.env')
SSH_USER = os.getenv('SSH_USER')
SSH_PASSWORD = os.getenv('SSH_PASSWORD')


def connect_ssh(_ip: str, _device_name: str= "NONAME") -> Channel:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"trying {_device_name}, {_ip}")
    try:
        client.connect(hostname=_ip,
                       username=SSH_USER,
                       password=SSH_PASSWORD,
                       look_for_keys=False,
                       allow_agent=False,
                       timeout=10)
    except Exception as e:
        print(f"{_device_name},{_ip}. Not connected. Reason {e}")
        client.close()
        time.sleep(0.5)
        return
    try:
        shell = client.invoke_shell()
    except Exception as e:
        print(f"{_device_name},{_ip}. Can't invoke shell. Reason {e}")
        client.close()
    print(f"{_device_name}, {_ip}. Connected.")
    return shell


def get_interfaces_and_ips(_device):
    shell = connect_ssh(_device[1],_device[0])
    if shell is None:
        return
    try:
        print("Getting raw data about interfaces and ips....")
        shell.send("terminal length 0\n")
        time.sleep(1)
        shell.send("show ip int br\n")
        time.sleep(5)
        output = shell.recv(102400).decode()
    except Exception as e:
        print(e)

    #split output to list of strings
    splitted_output = output.split(sep='\r\n')

    #drop all before Interfaces
    search_pattern = 'Interface\s*IP-Address\s*OK'
    for i in range(len(splitted_output)):
        if re.search(search_pattern,splitted_output[i]):
            for j in range(0, i+1):
                splitted_output.pop(0)
                j += 1
            break
    #drop last 2 strings with garbage
    splitted_output.pop()

    #drop interfaces with operstatus down and adminstatus down and not interesting interfaces
    items_to_delete = list()
    search_patterns = ['administratively down', 'unassigned', 'Loopback', 'Se0/', 'Et1/', 'BDI', 'Ethernet-Internal']
    for i in range(0, len(splitted_output)):
        for search_pattern in search_patterns:
            if re.search(search_pattern, splitted_output[i]):
                items_to_delete.append(splitted_output[i])
    for m in range(0, len(items_to_delete)):
        try:
            splitted_output.remove(items_to_delete[m])
        except:
            continue

    #make list of tuples with address, interface values
    interfaces_addresses_list = []
    for line in splitted_output:
        try:
            if_name = re.search("(GigabitEthernet\d+/\d+/\d+.\d+|GigabitEthernet\d+/\d+/\d+|Vlan\d+|GigabitEthernet\d+/\d+|Gi\d+/\d+/\d+.\d+|Tunnel\d|FastEthernet\d/\d|Port-channel\d|GigabitEthernet\d|Multilink\d+)", line).group(0)
            if_ip_address = re.search("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", line).group(0)
            if_name = if_name.replace("GigabitEthernet", "gi")
            if_name = if_name.replace("Vlan", "vl")
            if_name = if_name.replace(".", "-")
            if_name = if_name.replace("/", "-")
            interfaces_addresses_list.append((_device[0], if_name, if_ip_address))
        except Exception as e:
            print(f"{_device} \n {line}. Error reason {e}")
            break
    return interfaces_addresses_list
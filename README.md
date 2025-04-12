This script get network interfaces and ip addresses from devices and generates /etc/hosts file in root folder.

You can change search patterns for interface names in Cisco.py/Huawei.py/ECI.py/Juniper.py files. At first iteration script clean gathered data from device to work with only strigs with interfaces and ip addresses. At second, finds interface name and ip address.

Number of parallel threads can be adjusted by change the MAXTHREADS variable in main.py. Feel free to use above 500+ threads, script is working fine, it was tested for about 750 threads in parallel.

File with devices ip must be filled like hosts-example.env and named hosts.env and placed near main.py.
login/password must be set at credentials.env file and placed near main.py. See credentials-example.env.

Script is tested on 2k network devices, such as cisco ME-3600X, ISR-4451X, IE-3000, IE-2000, 3945, 2960X and 2960S; Huawei AR2504, 5720, 5700, 5735(YunShan OS too), 5732; Juniper EX 2200, 3300, 4200, M120, MX104
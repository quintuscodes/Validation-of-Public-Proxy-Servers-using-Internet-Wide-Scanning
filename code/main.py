import asyncio
import subprocess
import json
from proxy_manager import Proxy_Manager
from proxy_class import Proxy 
from functions import *
from Zmap_code import *
#from plots import *


async def main():
    # Configuration for ZMAP
    output_file = "output.csv"
    #target_range = "192.168.0.0/24"
    target_range = "10.20.30.0/24"
    ports = [80, 3128, 1080,8080] # + 443 HTTPS
    rate = 64
    probes = 2

    # Define port-to-protocol mapping
    http_ports = [80,443, 3128,8080]
    socks_ports = [1080]

    # Initialize Proxy_Manager
    proxy_managers_list = []
    http_manager = Proxy_Manager("HTTP")
    proxy_managers_list.append(http_manager)
    socks_manager = Proxy_Manager("SOCKS")
    proxy_managers_list.append(socks_manager)
    
    num_proto = len(proxy_managers_list)

    # Run ZMAP scan
    await run_zmap_scan(output_file, target_range, ports, rate, probes)


    # Fetch and write proxies to managers
    await fetch_proxys_write_to_class(proxy_managers_list,output_file, http_ports, socks_ports)

    
    
    await asyncio.sleep(10)
    #Evaluate List
    counter = 0
    "Recursive Re-Evaluate List: Dynamic Approach"
    
    global stop_counter
    stop_counter = 0
    print(proxy_managers_list)
    await rec_wait_and_evaluate_again(proxy_managers_list,counter,5,10,num_proto, stop_counter)

    
    for manager in proxy_managers_list:
        print(f"\n{manager.get_proto()} :  ")
        for epoch_data in manager.historical_data:
            print(f"Epoch: {epoch_data['epoch']}, Proxies: {len(epoch_data['proxies'])}")
    
# Entry point
if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import subprocess
import json
from proxy_manager import Proxy_Manager
from proxy_class import Proxy 
from functions import *
#from plots import *

async def run_zmap_scan(output_file, target_range, ports, rate, probes):
    """
    Run a ZMAP scan as a subprocess.
    """
    zmap_command = [
        "sudo", "zmap",
        "-p", ",".join(map(str, ports)),
        "-o", output_file,
        "-f", "saddr,sport,classification,success",
        "-r", str(rate),
        "--probes", str(probes),
        "--output-filter= success=1 && repeat = 0",
        
        target_range
    ]
    
    process = await asyncio.create_subprocess_exec(
        *zmap_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    print("ZMAP scan started. Streaming output in real-time:")

    # Stream stdout and stderr in real-time
    async def stream_output(stream, stream_name):
        while True:
            line = await stream.readline()
            if not line:
                break
            print(f"[{stream_name}] {line.decode().strip()}")

    await asyncio.gather(
        stream_output(process.stdout, "STDOUT"),
        stream_output(process.stderr, "STDERR")
    )

    await process.wait()
    #stdout, stderr = await process.communicate()

    if process.returncode == 0:
        print(f"ZMAP scan completed. Output written to {output_file}.")
    else:
        print(f"ZMAP scan failed. Error: {process.returncode}")

async def parse_zmap_output(output_file, http_ports, socks_ports):
    """
    Parse the ZMAP output and generate Proxy objects.
    """
    with open(output_file, "r") as file:
        data = file.readlines()

    headers = data[0].strip().split(",")
    entries = [line.strip().split(",") for line in data[1:]]

    proxies = []

    for entry in entries:
        entry_dict = dict(zip(headers, entry))

        if entry_dict.get("success") == "1":
            port = int(entry_dict.get("sport", 0))

            if port in http_ports:
                protocol = "HTTP"
            elif port in socks_ports:
                protocol = "SOCKS"
            else:
                continue

            proxy = {
                "ip": entry_dict.get("saddr"),
                "port": port,
                "protocol": protocol
            }
            proxies.append(proxy)

    return proxies
"""
async def fetch_proxys_write_to_class(manager: Proxy_Manager, output_file, http_ports, socks_ports):

    #Integrate ZMAP output into Proxy_Manager class.
    
    output = await parse_zmap_output(output_file, http_ports, socks_ports)

    for entry in output:
        ip = entry['ip']
        port = entry['port']
        protocol = entry['protocol']
        p = Proxy(protocol, ip, port,6)
        if p.protocol == manager.protocol:
            manager.add_to_list(p)
        


    print(f"Added {len(output)} proxies to {manager.protocol} manager.")
"""
async def fetch_proxys_write_to_class(proxy_managers_list:list, output_file, http_ports, socks_ports):
    """
    Integrate ZMAP output into Proxy_Manager class.
    """
    output = await parse_zmap_output(output_file, http_ports, socks_ports)

    for entry in output:
        ip = entry['ip']
        port = entry['port']
        protocol = entry['protocol']
        p = Proxy(protocol, ip, port,6)
        for item in proxy_managers_list:

            if item.get_proto() == p.protocol:
                item.add_to_list(p)
                print(f"Added {len(item.get_proxy_list())} proxies to {item.protocol} manager.")

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

import asyncio
import subprocess
import json
from proxy_manager import Proxy_Manager
from proxy_class import Proxy 

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
        "--output-filter= repeat = 0",
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

async def fetch_proxys_write_to_class(manager: Proxy_Manager, output_file, http_ports, socks_ports):
    """
    Integrate ZMAP output into Proxy_Manager class.
    """
    proxies = await parse_zmap_output(output_file, http_ports, socks_ports)

    for proxy in proxies:
        ip = proxy['ip']
        port = proxy['port']
        protocol = proxy['protocol']
        p = Proxy(protocol, ip, port,6)
        if p.protocol == manager.protocol:
            manager.add_to_list(p)
        


    print(f"Added {len(proxies)} proxies to {manager.protocol} manager.")

async def main():
    # Configuration for ZMAP
    output_file = "output.json"
    target_range = "192.168.0.0/24"
    ports = [80, 3128, 1080]
    rate = 64
    probes = 2

    # Define port-to-protocol mapping
    http_ports = [80, 3128]
    socks_ports = [1080]

    # Run ZMAP scan
    await run_zmap_scan(output_file, target_range, ports, rate, probes)

    # Initialize Proxy_Manager
    http_manager = Proxy_Manager("HTTP")
    socks_manager = Proxy_Manager("SOCKS")

    # Fetch and write proxies to managers
    await fetch_proxys_write_to_class(http_manager, output_file, http_ports, socks_ports)
    await fetch_proxys_write_to_class(socks_manager, output_file, http_ports, socks_ports)

    # Print results
    http_manager.print_proxy_list("slave")
    socks_manager.print_proxy_list("slave")
    
    #Evaluate List
    counter = 0
    await http_manager.evaluate_proxy_list(counter, 10,2)
    await http_manager.sort_proxy_lists(2)
    # Print results
    http_manager.print_proxy_list("slave")
    socks_manager.print_proxy_list("slave")
    http_manager.print_proxy_list("master")
    socks_manager.print_proxy_list("master")
# Entry point
if __name__ == "__main__":
    asyncio.run(main())

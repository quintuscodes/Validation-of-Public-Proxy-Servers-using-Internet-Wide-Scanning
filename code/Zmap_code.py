from proxy_manager import Proxy_Manager
from proxy_class import Proxy 
import asyncio

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

from proxy_class import Proxy
import asyncio
from proxy_manager import Proxy_Manager

"Proxy Positiv Test - HTTP"

proxies = {
        "HTTP" : ["202.61.206.250", 8888, "Australia"],
        "SOCKS4": ["212.83.143.191", 12898, "France"],
        "SOCKS5" : ["212.83.143.191",12898, "France"],
        "CONNECT25": ["160.86.242.23",8080,"Japan"],
        "http_false_80": [ "XXX.XX.XXX.XXX", 80, "ufer_hama"],
        "socks_false_1080" : [ "XXX.XX.XXX.XXX", 1080,"ufer_hama"],
        "HTTP_false" : ["202.61.206.250", 80,"Australia"]

}
proxy_manager_list = []
proxy_list = []
def construct_PMs(proxies,proxy_manager_list):
    for key in proxies:
        object = Proxy_Manager(f"{key}")
        ip = proxies[key][0]
        port = proxies[key][1]
        country = proxies[key][2]
        type = key
        p = Proxy(type,ip,port,country,0)
        object.add_to_list(p)
        proxy_manager_list.append(object)

def print_proxy_managers(list,arg):
    for proxy_manager_item in list:
        proxy_manager_item.print_proxy_list(arg)


def write_proxy_to_class(proxies,proxy_list):
    

    
    for key in proxies:

      
            
      ip = proxies[key][0]
      port = proxies[key][1]
      country = proxies[key][2]
      type = key
      p = Proxy(type,ip,port,country,0)
      proxy_list.append(p)

"""
def print_proxy_list(arg):
    
    Method to print the actual proxy_list with enhanced ASCII art representation designed by ChatGPT
    
    border_top = "╔" + "═" * 150 + "╗"
    border_bottom = "╚" + "═" * 150 + "╝"
    separator = "╟" + "─" * 150 + "╢"
    title_bar = "║{:^150}║"

    def format_proxy(proxy, index):
        fields = [
            f"Protocol: {proxy.protocol}",
            f"IP: {proxy.ip}",
            f"Port: {proxy.port}",
            f"Country: {proxy.country}",
            f"Avg Score: {proxy.avg_score:.2f}",
            f"Score: {proxy.score:.2f}",
            f"Log Score: {proxy.log_score}",
            f"Handshakes: {proxy.handshakes}",
            f"Log Handshake: {proxy.log_handshake}",
            f"Avg SYN-ACK Time: {proxy.avg_syn_ack_time:.2f} s",
            f"Avg Transmission Time: {proxy.avg_transmission_time:.2f} s",
            f"Avg Throughput: {proxy.avg_throughput:.2f} KB/s",
            f"Log Request: {proxy.log_request}",
            f"Request-Rate: {proxy.request_rate} % ",
            f"Handshake-Rate: {proxy.handshake_rate} % "
        ]
        proxy_info = "\n".join([f"║ {field:<148} ║" for field in fields])
        return f"╠{'═'*150}╣\n║ Proxy {index+1:<143}║\n{proxy_info}\n"

    
    proxy_list_to_print = proxy_list if arg == "master" else proxy_list
    list_type = " Proxy List" if arg == "master" else "Proxy List"

    #Output
    output = [border_top, title_bar.format(f" Proxy - Manager"), separator, title_bar.format(f"**** {list_type} ****")]

    for i, proxy in enumerate(proxy_list_to_print):
        output.append(format_proxy(proxy, i))

    output.append(border_bottom)

    # Print the output
    print("\n".join(output))

"""
#write_proxy_to_class(proxies,proxy_list)
    
#print_proxy_list(proxy_list)

construct_PMs(proxies,proxy_manager_list)
print_proxy_managers(proxy_manager_list,"lol")
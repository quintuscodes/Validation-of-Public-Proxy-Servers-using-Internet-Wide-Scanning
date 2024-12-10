from proxy_class import Proxy


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

proxy_list = []

def write_proxy_to_class(proxies,proxy_list):
    

    
    for key in proxies:

      
            
      ip = proxies[key][0]
      port = proxies[key][1]
      country = proxies[key][2]
      type = key
      p = Proxy(type,ip,port,country,0)
      proxy_list.append(p)

write_proxy_to_class(proxies,proxy_list)

for proxy in proxy_list:
   print(proxy.get_object())
# Validation-of-Public-Proxy-Servers-using-Internet-Wide-Scanning
The Repository is an Investigation of public proxy servers. Proxy Servers should be identified using an Internet-Wide-Scanning Technique. Objects should be evaluated/validated in order to make a statement how proxy servers of the public adress space are available and reliable. 
This is a test line of code to be pushed to origin.

# Class Diagram
Illustrates the Proxy Manager and Proxy classes with Getters & Setters. <br>
<br>
<br>

```mermaid 
%%{init: {'theme':'neutral'}}%%
classDiagram

  direction LR
  
  class Proxy_Manager {
    - protocol: str
    - master_proxy_list: list
    - proxy_list: list
    - historical_data: list
    + __init__(_protocol) Proxy_Manager
    + add_to_list(proxy) void
    + add_epoch_data(epoch_number)void
    + print_proxy_list(arg) void
    + evaluate_proxy_list(counter, evaluation_rounds) void
    + sort_proxy_lists(proxy_number) void
    + reset_proxys() void
    + log_scores() void
    + get_proxy(index) Proxy
    + get_master_list() list 
    + get_proxy_list() list
    + get_proto() str
    + get_hist_data() list
    
  }
  
  class Proxy {
    - protocol: str
    - ip: str
    - port: int
    - avg_score: int
    - avg_syn_ack_time: float
    - avg_throughput: float
    - avg_transmission_time: float
    - score: int
    - handshakes: int
    - log_handshake: list
    - log_request: list
    - log_score: list
    - log_syn_ack_time: list
    - log_throughput: list
    - log_transmission_time: list
    + __init__(_proto, _ip, _port, _country, _handshakes) Proxy
    + evaluate() self
    + evaluate_handshakes() self
    + evaluate_throughput() self
    + evaluate_request() self
    + calc_score(evaluation_rounds) self
    + reset_attributes() self

    + get_ip() str
    + get_last_log_handshake_item() int
    + get_log_handshake() list
    + get_log_syn_ack_time() list
    + get_log_throughput() list
    + get_log_transmission_time() list
    + get_object() Proxy
    + get_port() int
    + get_score() float
    + set_avg_score() float
    + set_log_handshake(n) list
    + set_log_request(res) list
    + set_log_score() list
    + set_log_syn_ack_time(syn_ack) list
    + set_log_throughput(throughput) list 
    + set_log_transmission_time(transm_time) list
    + set_score(_score) float
  }
  
  Proxy_Manager "1" --> "1..*" Proxy : contains
```

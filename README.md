# Validation-of-Public-Proxy-Servers-using-Internet-Wide-Scanning
The Repository's purpose is an investigation of public proxy servers. Proxy Servers are identified using the open-source internet-wide-scanning tool Zmap. <br> Objects should be evaluated in order to make a statement how proxy servers of the public adress space are available and reliable. <br>

# Class Diagram
Illustrates the Proxy Manager and Proxy class with Getters & Setters. <br>
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

# Sequence Diagram - ZMap Scan & Validation Data Structure
The sequence diagram shows the program control flow. <br>
The defined network address space is scanned(tcp-port scan) in order to detect running and open public proxy services. <br>
In addition the output is used to parse the data and run validation methods in order to get a ranked list of more and less reliable proxy objects.
```mermaid
sequenceDiagram
    autonumber
    actor main as "main.py"
    
    participant zmap as "ZMAP"
    
    participant http as     "HTTP   :: Proxy_Manager"
    participant socks as    "SOCKS  :: Proxy_Manager"
    participant proxy as    "Proxy  :: Proxy"
    participant functions as Functions

    main->>+main: asyncio.run(main())

    Note right of main: ZMAP IP-Range + Port Declaration

    main->>+http: new Proxy_Manager("HTTP")
    http-->>main: http_manager
    main->>main: proxy_managers_list.append(http_manager)
    main->>+socks: new Proxy_Manager("SOCKS)
    socks-->>main: socks_manager
    main->>main: proxy_managers_list.append(socks_manager)

    
    main->>+zmap: await run_zmap_scan(output_file,target_range,ports,rate,probes)

    Note left of main: Step I. - Zmap Scan
    zmap->>zmap: await asyncio.subprocess(*zmap_command)

    zmap-->>main: output.csv
    Note left of main: Step II. - Fetch Proxies
    main->>zmap: await fetch_proxys_write_to_class(PM_List,output_file,http_ports,socks_ports)
    
    zmap->>zmap: parse_zmap_output(output_file,http_ports,socks_ports)

    loop output.csv
        zmap->>+proxy: new proxy(protocol,ip,port)

        alt proxy.port is in http_ports
            
            proxy-->>http: http_manager.add_to_list(proxy)
        else proxy.port is in socks_ports
            proxy-->>socks: socks_manager.add_to_list(proxy)
        end
    end

    deactivate zmap

    Note left of main: Step III. & IV. - Validate and Scoring Mechanism

    main->>+functions: await dynamic_evaluate_call(proxy_managers_list)
    
    loop  Evaluate 10 epochs
        
        functions->>socks: log_scores()
        functions->>http:log_scores()
        loop
        Note over functions: Wait 20s between evaluation epochs
        end
        functions->>functions: reset_proxy_objects(PM_List)
        functions->>http: reset_proxys()
        Note over http,proxy: Reset evaluated fields of proxy objects before new evaluation epoch
        http->>proxy: reset_attributes()
      
        functions->>socks: reset_proxys()
        
        socks->>proxy: reset_attributes()
        functions->>functions: await generate_evaluate_tasks()
        functions->>functions: await asyncio.gather(*re_evaluate_tasks)
        Note right of socks: Start validation
        par evaluate http
        functions-)http: http.evaluate_proxy_list()
        loop iterate for 10 evaluation_rounds per evaluation epoch
        
          par evaluate proxys concurrently with asyncio
            http-)proxy: proxy.evaluate()
            par evaluate proxy parameters concurrently
            Note over socks: asyncio ThreadPoolExecutor 
              proxy-)proxy: evaluate_handshakes()
              proxy-)proxy: evaluate_throughput()
              proxy-)proxy: evaluate_request()
            end
            proxy->>proxy: proxy.calc_score()
            proxy-->>http: return
          end
        end
      and evaluate socks
        functions-)socks: socks.evaluate_proxy_list()
        loop iterate for 10 evaluation_rounds per evaluation epoch
        
          par evaluate proxys concurrently with asyncio
            socks-)proxy: proxy.evaluate()
            par evaluate proxy parameters concurrently
            Note over socks: asyncio ThreadPoolExecutor 
              proxy-)proxy: evaluate_handshakes()
              proxy-)proxy: evaluate_throughput()
              proxy-)proxy: evaluate_request()
            end
            proxy->>proxy: proxy.calc_score()
            proxy-->>socks: return
          end
        end
      end
      functions->>functions: sort_proxy_managers(PM_List)
      functions->>functions: print_proxy_managers(PM_List,"master")
    end

    deactivate functions
    deactivate http
    deactivate socks
    deactivate proxy
    deactivate main
  
```

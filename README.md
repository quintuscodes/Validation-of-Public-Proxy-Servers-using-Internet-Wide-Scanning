# Validation-of-Public-Proxy-Servers-using-Internet-Wide-Scanning
The Repository's purpose is an Investigation of public proxy servers. Proxy Servers are identified using the open-source internet-wide-scanning Tool Zmap. <br> Objects should be evaluated in order to make a statement how proxy servers of the public adress space are available and reliable. <br>

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

# Sequence Diagram
The Sequence Diagram illustrating the program control flow of the proxy validation python script.
<br>
<br>
<br>

```mermaid 

sequenceDiagram
    autonumber
    actor main as "CLI - main"
    
    participant socks5 as "SOCKS5   :Proxy_Manager"
    participant http as "HTTP   :Proxy_Manager"
    participant broker as "Broker   :proxybroker"
    participant proxy as Proxy
    participant functions as Functions

    
    main->>main: run(proxy_number: int, evaluation_rounds: int, protocols: set)
    main->>+main: asyncio.get_event_loop()
    loop
      
      main->>main: loop.run_until_complete(main(proxy_number, evaluation_rounds, protocols))
      
      
      main->>+http: new   Proxy_Manager("HTTP")
      http-->> main: http
      main->>main: fetch_tasks.append(http.fetch_proxy_write_to_class())
      main->>main: evaluate_tasks.append(http.evaluate_proxy_list())
      

      main->>+socks5: new   Proxy_Manager("SOCKS5")
      socks5-->>main: socks5

      main->>main: fetch_tasks.append(socks5.fetch_proxy_write_to_class())
      main->>main: evaluate_tasks.append(socks5.evaluate_proxy_list())
      
      
      main->>main: await asyncio.gather(*fetch_tasks)
      par fetch http
          
        main-)http: fetch_proxys_write_to_class()
        http-)+broker: new   Broker()
        broker-)broker: find(protocol,lvl = 'HIGH',limit=proxy_num)
        broker--)http: return proxies
        http-)http: write_proxy_to_class(proxies)
        http-)+proxy: new   proxy(type,ip,port,country,evaluation_rounds)
        proxy--)http: return proxy
        proxy->>http: add_to_list(<proxy>)
        deactivate broker
      and fetch socks5
        main-)socks5: fetch_proxys_write_to_class()
        socks5-)+broker: new   Broker()
        broker-)broker: find(protocol,lvl = 'HIGH',limit=proxy_num)
        broker--)socks5: return proxies
        socks5-)socks5: write_proxy_to_class(proxies)
        socks5-)proxy: new   proxy(type,ip,port,country,evaluation_rounds)
        proxy--)socks5: return proxy
        proxy->>socks5: add_to_list(<proxy>)
        deactivate broker
      end

      main->>main: await asyncio.gather(*evaluate_tasks)
      par evaluate http
          
        main-)http: http.evaluate_proxy_list()
        loop evaluation_rounds
          par evaluate proxys concurrently with asyncio
            http-)proxy: proxy.evaluate()
            par
              proxy-)proxy: evaluate_handshakes()
              proxy-)proxy: evaluate_throughput()
              proxy-)proxy: evaluate_request()
            end
            proxy->>proxy: proxy.calc_score()
            proxy-->>http: return
            http->>http: reward_best_proxys()
          end
        end
        
      and evaluate socks5
        main-)socks5: socks5.evaluate_proxy_list()
        loop evaluation_rounds
          par evaluate proxys concurrently with asyncio
            socks5-)proxy: proxy.evaluate()
            par
              proxy-)proxy: evaluate_handshakes()
              proxy-)proxy: evaluate_throughput()
              proxy-)proxy: evaluate_request()
            end
            proxy->>proxy: proxy.calc_score()
            proxy-->>socks5: return
            socks5->>socks5: reward_best_proxys()
          end
        end
      end
      

      main->>main: await sort_proxy_managers()
      loop
        
        Note right of main: Remove Proxys with score <100
        main->>http:sort_proxy_lists()
        main->>socks5: sort_proxy_lists()
      end 
      
      main->>functions:await rec_wait_and_evaluate_again()
      functions->>http: log_scores()
      functions->>socks5: log_scores()
      functions->>main: await print_proxy_managers()
      loop
        Note over functions: Wait 20s
      end
      functions->>functions: await Checker()
      loop CHECKER ACTIVE
        alt CHECK APPROVED - CONTINUE
          
        else CHECK REJECT - REFILL
          functions-)functions: await asyncio.gather(*refresh_tasks)
          par Refresh HTTP Proxy List
            functions-)http: http.refresh_proxy_list()
          and Refresh SOCKS5 Proxy List
            functions-)socks5: socks5.refresh_proxy_list()
          end
        end
      end
      functions->>functions: reset_proxy_objects()
      
      functions->>http: reset_proxys()
      Note over http,proxy: Reset evaluated Fields of existing Proxy Objects before new Evaluation Round
      http->>proxy: reset_attributes()
      
      functions->>socks5: reset_proxys()
      Note over socks5,proxy: Reset evaluated Fields of existing Proxy Objects before new Evaluation Round
      socks5->>proxy: reset_attributes()

      functions-)functions: await asyncio.gather(*re_evaluate_tasks)
      
      par evaluate http
        functions-)http: http.evaluate_proxy_list()
      and evaluate socks5
        functions-)socks5: socks5.evaluate_proxy_list()
      end
      functions->>functions: await sort_proxy_managers()
      functions->>functions: await print_proxy_managers("master")
      functions->>functions: await rec_wait_and_evaluate_again()

      deactivate proxy
      deactivate http
      deactivate socks5
      deactivate main
    end
    
```

# Sequence Diagram ZMAP

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

    Note left of main: 

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

    Note left of main: Step III. & IV.

    main->>+functions: await dynamic_evaluate_call(proxy_managers_list)
    
    loop  stop_counter < epoch_number
        Note right of functions: Evaluate n = epoch_number epochs
        functions->>socks: log_scores()
        functions->>http:log_scores()
        loop
        Note over functions: Wait t=20s between evaluation epochs
        end
        functions->>functions: reset_proxy_objects(PM_List)
        functions->>http: reset_proxys()
        Note over http,proxy: Reset evaluated Fields of existing Proxy Objects before new Evaluation Round
        http->>proxy: reset_attributes()
      
        functions->>socks: reset_proxys()
        Note over socks,functions: Reset evaluated Fields of existing Proxy Objects before new Evaluation Round
        socks->>proxy: reset_attributes()
        functions->>functions: await generate_evaluate_tasks()
        functions->>functions: await asyncio.gather(*re_evaluate_tasks)
        par evaluate http
        functions-)http: http.evaluate_proxy_list()
        loop iterate for 10 evaluation_rounds
        
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
            http->>http: reward_best_proxys()
          end
        end
      and evaluate socks
        functions-)socks: socks.evaluate_proxy_list()
        Note right of functions: Equivalent to http
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

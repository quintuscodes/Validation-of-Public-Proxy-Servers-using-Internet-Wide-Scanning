import asyncio
from proxy_class import Proxy




class Proxy_Manager:

  """
  A Class for Managing Protocol Proxy List and Evaluation
  """


  "Constructor"
  def __init__(self,_protocol):
    self.protocol = _protocol
    self.master_proxy_list = []
    self.proxy_list = []
    self.historical_data = []




  
  
  def get_proxy(self, index) -> Proxy:
     proxy = self.proxy_list[index]
     
     return proxy
  
  def get_master_list(self):
     return self.master_proxy_list
  
  def get_proxy_list(self):
     return self.proxy_list
  
  def get_proto(self):
     return self.protocol

  def get_hist_data(self):
     return self.historical_data
  
  def add_epoch_data(self, epoch_number):
        """
        Store Epoch data for plotting 
        """
        epoch_data = {
            'epoch': epoch_number,
            'proxies': [
                {
                    'ip': proxy.get_ip(),
                    'port':proxy.get_port(),
                    'avg_syn_ack_time' : proxy.get_avg_syn_ack_time(),
                    'avg_transmission_time': proxy.get_avg_transmission_time(),
                    'avg_throughput': proxy.get_avg_throughput(),
                    'handshake_rate': proxy.get_handshake_rate(),
                    'request_rate': proxy.get_request_rate()
                }
                for proxy in self.master_proxy_list
            ]
        }
        self.historical_data.append(epoch_data)
  
  "Method to add a Proxy item to the list "
  def add_to_list(self,Proxy):
    self.proxy_list.append(Proxy)
    
    attrs = vars(Proxy)
    print(f"\nAdded to List:\n" + ', \n'.join("%s: %s" % item for item in attrs.items()) + "\n")
  
  async def print_proxy_list(self, arg): 
    """
    Method to print the actual proxy_list with enhanced ASCII art representation designed by ChatGPT
    """
    border_top = "╔" + "═" * 150 + "╗"
    border_bottom = "╚" + "═" * 150 + "╝"
    separator = "╟" + "─" * 150 + "╢"
    title_bar = "║{:^150}║"

    def format_proxy(proxy, index):
        fields = [
            f"Protocol: {proxy.protocol}",
            f"IP: {proxy.ip}",
            f"Port: {proxy.port}",
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

    
    proxy_list_to_print = self.master_proxy_list if arg == "master" else self.proxy_list
    list_type = "MASTER Proxy List" if arg == "master" else "Proxy List"

    #Output
    output = [border_top, title_bar.format(f"{self.protocol} Proxy - Manager"), separator, title_bar.format(f"**** {list_type} ****")]

    for i, proxy in enumerate(proxy_list_to_print):
        output.append(format_proxy(proxy, i))

    output.append(border_bottom)

    # Print the output
    print("\n".join(output))

  async def evaluate_proxy_list(self,counter, evaluation_rounds,proxy_number):
    
    """
    A Method to initialize the evaluation of the Proxies in Proxy-List
    
    """
    
    
    
    while counter < evaluation_rounds: 
      counter += 1 
      
    
      tasks = []
      
      
      
      for i in range(len(self.proxy_list)):
        proxy = self.get_proxy(i)
        task = proxy.evaluate()             #Evaluate Thread Pool Executor -> Evaluation Methods {handshake,transmission_time,throughput,request}
        tasks.append(task)
        
        

      await asyncio.gather(*tasks)
    
    for i in range(len(self.proxy_list)):
        proxy = self.get_proxy(i)
        proxy.calc_score(evaluation_rounds) #loop through proxy_list and calculate score per proxy
    
    
    "Reward the Best Proxys in evaluation parameters - sort after score - then give 15,10,5 Points credit score"
    """
    During ZMAP approach test scenario this is unneccesary hence we dont have more than 1,2 proxys per proxy manager.
    In an Internet-Wide-Scan with 1:m proxys this needs to be added again.
    """
    """
    first = 15
    second = 10
    third = 5

    for i in range(3):
      if i == 0:
        self.proxy_list.sort(key=lambda Proxy: Proxy.avg_syn_ack_time, reverse=False) 

      elif i == 1:
        self.proxy_list.sort(key=lambda Proxy: Proxy.avg_transmission_time, reverse=False)

      elif i == 2:
         self.proxy_list.sort(key=lambda Proxy: Proxy.avg_throughput, reverse=True)

      
      
      if len(self.proxy_list) >= 1:
        self.proxy_list[0].score += first
        if i == 0:
          print(f"{first}  Points Credit to IP: {self.proxy_list[0].ip} in avg_syn_ack_time PROT: {self.protocol}  ")
        if i == 1:
          print(f"{first}  Points Credit to IP: {self.proxy_list[0].ip} in avg_transmission_time PROT: {self.protocol}  ")
        if i == 2:
          print(f"{first}  Points Credit to IP: {self.proxy_list[0].ip} in avg_throughput PROT: {self.protocol}  ")
        
      
      if len(self.proxy_list) >= 2:
        self.proxy_list[1].score += second
        if i == 0:
          print(f"{second} Points Credit to IP: {self.proxy_list[1].ip} in avg_syn_ack_time PROT: {self.protocol}  ")
        if i == 1:
          print(f"{second} Points Credit to IP: {self.proxy_list[1].ip} in avg_transmission_time PROT: {self.protocol} ")
        if i == 2:
          print(f"{second} Points Credit to IP: {self.proxy_list[1].ip} in avg_throughput PROT: {self.protocol} ")
        
        
      
      if len(self.proxy_list) >= 3:
        self.proxy_list[2].score += third
        if i == 0:
          print(f"{third} Points Credit to IP: {self.proxy_list[2].ip} in avg_syn_ack_time PROT: {self.protocol} ")
        if i == 1:
          print(f"{third} Points Credit to IP: {self.proxy_list[2].ip} in avg_transmission_time PROT: {self.protocol} ")
        if i == 2:
          print(f"{third} Points Credit to IP: {self.proxy_list[2].ip} in avg_throughput PROT: {self.protocol} ")
    """
    for i in range(len(self.proxy_list)):
        proxy = self.get_proxy(i)
        
        
    
    self.proxy_list.sort(key=lambda Proxy: Proxy.score, reverse=True)
    


  async def sort_proxy_lists(self,proxy_number):
    "A Method to sort the List and remove proxys with a < 50 score threshold"
    
    self.proxy_list.sort(key=lambda Proxy: Proxy.score, reverse=True)
    
    if len(self.master_proxy_list) < proxy_number:
      
      for proxy in self.proxy_list:
        
        #proxy.set_rates()
        if proxy.score < 50: 
          self.proxy_list.remove(proxy)
          print("\n Removed Proxys with score <= 50 \n")
        if proxy.score >= 80 and len(self.master_proxy_list) < proxy_number:
          
          self.master_proxy_list.append(proxy)
        
        
    
    self.master_proxy_list.sort(key=lambda Proxy: Proxy.score, reverse=True)
    self.proxy_list.clear()
  
  def reset_proxys(self):
     for proxy_object in self.master_proxy_list:
        proxy_object.reset_attributes()
        self.proxy_list.append(proxy_object)
        self.master_proxy_list.remove(proxy_object)

  def log_scores(self):
     for proxy_object in self.master_proxy_list:
        proxy_object.set_log_score()# Store score before reset
        proxy_object.set_avg_score() #Average Score for up to date reliability attribute criteria

        if len(proxy_object.log_score) > 9:
           if proxy_object.get_avg_score() <= 80:
              self.master_proxy_list.remove(proxy_object)

import matplotlib.pyplot as plt
from proxy_manager import Proxy_Manager
#import seaborn as sns
#import pandas as pd
import numpy as np
import os 
import shutil
import csv

"Script for plotting the Project Proxy Manager Data."

def export_proxy_data(proxy_manager1:Proxy_Manager,proxy_manager2:Proxy_Manager):
    historical_data1 = proxy_manager1.get_hist_data()
    historical_data2 = proxy_manager2.get_hist_data()

    combined_historical_data = historical_data1 + historical_data2
    
    
    filename="proxy_data.csv"

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Epoch", "IP", "Port", "Avg SYN-ACK Time", "Avg Transmission Time", "Avg Throughput", "Handshake Rate", "Request Rate"])

        for epoch_data in combined_historical_data:
            epoch = epoch_data['epoch']
            for proxy in epoch_data['proxies']:
                writer.writerow([epoch, proxy['ip'], proxy['port'], proxy['avg_syn_ack_time'], proxy['avg_transmission_time'], proxy['avg_throughput'], proxy['handshake_rate'], proxy['request_rate']])

def plot_everything():
    "Plotting,args: pm_list, pm_instanz for param plots"
    #plot_avg_score_distribution(proxy_managers_list)
    plot_top_proxies_by_protocol("avg_score.csv",2)
    plot_avg_syn_ack_time("proxy_data.csv")
    plot_avg_throughput("proxy_data.csv")
    plot_avg_transmission_time("proxy_data.csv")
    plot_HR_and_RR("proxy_data.csv")
    
    move_plots(run_number="Default")

def format_label(ip, port):
    """Formatiert die Legende mit IP, Port und Proxy-Typ."""
    if port == 80:
        return f"{ip}:{port} (HTTP-Standard-Gateway)"
    elif port == 3128:
        return f"{ip}:{port} (HTTP-Proxy)"
    elif port == 1080:
        return f"{ip}:{port} (SOCKS-Proxy)"
    else:
        return f"{ip}:{port}"

def plot_avg_score_distribution(proxy_managers):
    data = []
    for manager in proxy_managers:
        protocol = manager.get_proto()
        for proxy in manager.get_master_list():
            data.append({'protocol': protocol, 'avg_score': proxy.avg_score})

    #Color
    pastel_colors = ['#AEC6CF', '#FFB7B2', '#B39EB5', '#FFDAC1']

    #Information
    info = 'Evaluation Rounds per Iteration = 10, Evaluation Epochs = 5'
    # Convert to a DataFrame for easier plotting (requires pandas)
    
    df = pd.DataFrame(data)
    
    # Boxplot
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='protocol', y='avg_score', data=df,hue='protocol',palette=pastel_colors,legend=False)
    plt.title('Distribution of AVG_Scores by Protocol.')
    #plt.text(0.95,0.01, info,verticalalignment='bottom',horizontalalignment='right',
    #         transform=plt.gca().transAxes,color='gray',fontsize=12)
    plt.savefig('boxplot_avg_scores.png') # Save
    #plt.show()
    plt.close()
    #Clear Cache
    plt.clf()

    # Violinplot (alternative)
    plt.figure(figsize=(10, 6))
    sns.violinplot(x='protocol', y='avg_score', data=df,hue='protocol', palette=pastel_colors,legend=False)
    plt.title('Distribution of AVG_Scores by Protocol.')
    
    plt.savefig('violinplot_avg_scores.png') # Save
    plt.close()
    
    plt.clf()

def plot_top_proxies_by_protocol(csv_filename, top_n=2):
    # CSV-Datei einlesen
    df = pd.read_csv(csv_filename)

    # Sortiere nach avg_score, absteigend
    df_sorted = df.sort_values(by="avg_score", ascending=False)

    # HTTP-Proxies jetzt inkl. Port 80
    df_http_gateway = df_sorted[df_sorted["Port"] == 80].head(top_n)
    df_http_proxy = df_sorted[df_sorted["Port"] == 3128].head(top_n)
    df_socks = df_sorted[df_sorted["Port"] == 1080].head(top_n)

    # Kombiniere alle relevanten Datensätze
    df_top = pd.concat([df_http_gateway, df_http_proxy, df_socks])

    # Spalte für die Legende hinzufügen
    df_top["ip_port"] = df_top.apply(lambda row: format_label(row["IP"], row["Port"]), axis=1)

    plt.figure(figsize=(12, 6))

    # Plotte mit hue="ip_port", um IP+Port als eindeutigen Schlüssel für Farben zu verwenden
    sns.barplot(x='Port', y='avg_score', hue='ip_port', data=df_top, palette="tab10")

    plt.title(f'Proxies by Average Score')

    # Erstelle Legende mit formatierten Labels
    handles, labels = plt.gca().get_legend_handles_labels()
    unique_labels = dict(zip(labels, handles))

    # Sortiere die Protokolle in der Legende korrekt
    sorted_protocols = ['HTTP-Standard-Gateway', 'HTTP-Proxy', 'SOCKS-Proxy']

    sorted_labels = []
    for protocol in sorted_protocols:
        sorted_labels.extend([label for label in unique_labels if protocol in label])

    sorted_handles = [unique_labels[label] for label in sorted_labels]

    plt.legend(sorted_handles, sorted_labels, title='Listed by IP:Port', bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.tight_layout()
    plt.savefig('Proxies_by_avg_score.png')
    plt.close()
    plt.clf()



def filter_final_proxies(proxy_manager):
    
    
    final_proxies = set(proxy.get_ip() for proxy in proxy_manager.get_master_list())
    print(f"Final Proxies in Master List: {final_proxies}")

    
    filtered_data = []
    for epoch_data in proxy_manager.get_hist_data():  
        proxies = [proxy for proxy in epoch_data['proxies'] if proxy['ip'] in final_proxies]
        print(f"Epoch: {epoch_data['epoch']}, Filtered Proxies: {len(proxies)}, IPs: {[proxy['ip'] for proxy in proxies]}")
        filtered_data.append({'epoch': epoch_data['epoch'], 'proxies': proxies})

    return filtered_data

def filter_final_proxies_from_csv(csv_filename):
    
    df = pd.read_csv(csv_filename)

    
    #final_proxies = set(df["IP"].unique()) #Filter für deduplikation von IP-Adressen
    

    
    filtered_data = []
    epochs = df["Epoch"].unique()

    for epoch in epochs:
        epoch_data = df[df["Epoch"] == epoch]
        proxies = [
            {
                "ip": row["IP"],
                "port": row["Port"],
                "avg_syn_ack_time": row["Avg SYN-ACK Time"],
                "avg_transmission_time": row["Avg Transmission Time"],
                "avg_throughput": row["Avg Throughput"],
                "handshake_rate": row["Handshake Rate"],
                "request_rate": row["Request Rate"]
            }
            for _, row in epoch_data.iterrows() #if row["IP"] in final_proxies ->Dedup IP Filter
        ]
        filtered_data.append({"epoch": epoch, "proxies": proxies})

    return filtered_data


def plot_avg_throughput(csv_filename):
    filtered_data = filter_final_proxies_from_csv(csv_filename)
    proto = "HTTP and SOCKS"
    
    # Erstelle eine Menge mit (IP, Port), damit jede Kombination einzigartig bleibt
    unique_proxies = set()
    for epoch_data in filtered_data:
        for proxy in epoch_data['proxies']:
            unique_proxies.add((proxy['ip'], proxy['port']))

    # Farbschema für jede (IP, Port) Kombination
    color_map = plt.cm.get_cmap('tab20', len(unique_proxies))
    ip_colors = {(ip, port): color_map(i) for i, (ip, port) in enumerate(unique_proxies)}

    # Plotte die Daten
    plt.figure(figsize=(10, 6))

    for epoch_data in filtered_data:
        epoch = epoch_data['epoch']
        for proxy in epoch_data['proxies']:
            ip = proxy['ip']
            port = proxy['port']
            
            jittered_epoch = epoch + np.random.uniform(-0.2, 0.2)

            plt.scatter(jittered_epoch, proxy['avg_throughput'], color=ip_colors[(ip, port)])

    plt.xlabel('Epoch')
    plt.ylabel('Average Throughput in [KB/s]')
    plt.title(f'Average Throughput per Epoch of the {proto} - Protokoll')

    plt.xticks(np.arange(1, 11, 1))

    # Legende mit IP, Port und Typ
    handles = [
        plt.Line2D([0], [0], marker='o', color=ip_colors[(ip, port)], 
                   label=format_label(ip, port), linestyle='') 
        for ip, port in unique_proxies
    ]
    plt.legend(handles=handles, title='Proxies', bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.tight_layout()
    plt.savefig('Plot_Avg_Throughput.png')
    plt.close()
    plt.clf()

def plot_avg_syn_ack_time(csv_filename):
    filtered_data = filter_final_proxies_from_csv(csv_filename)
    proto = "HTTP and SOCKS"

    # Erstelle eine Menge mit (IP, Port), um jede Kombination eindeutig zu speichern
    unique_proxies = set()
    for epoch_data in filtered_data:
        for proxy in epoch_data['proxies']:
            unique_proxies.add((proxy['ip'], proxy['port']))

    # Farbschema für jede (IP, Port) Kombination
    color_map = plt.cm.get_cmap('tab20', len(unique_proxies))
    ip_colors = {(ip, port): color_map(i) for i, (ip, port) in enumerate(unique_proxies)}

    # Plotte die Daten
    plt.figure(figsize=(10, 6))

    for epoch_data in filtered_data:
        epoch = epoch_data['epoch']
        for proxy in epoch_data['proxies']:
            ip = proxy['ip']
            port = proxy['port']
            
            jittered_epoch = epoch + np.random.uniform(-0.1, 0.1)

            plt.scatter(jittered_epoch, proxy['avg_syn_ack_time'], color=ip_colors[(ip, port)])

    plt.xlabel('Epoch')
    plt.ylabel('Average SYN-ACK Time in [s]')
    plt.title(f'Average SYN-ACK Time per Epoch of the {proto} - Protokoll')

    plt.xticks(np.arange(1, 11, 1))  # Setzt die Ticks auf die Werte 1 bis 10
    plt.ylim(0, 1)

    # Legende mit IP, Port und Typ
    handles = [
        plt.Line2D([0], [0], marker='o', color=ip_colors[(ip, port)], 
                   label=format_label(ip, port), linestyle='') 
        for ip, port in unique_proxies
    ]
    plt.legend(handles=handles, title='Proxies', bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.tight_layout()
    plt.savefig('Plot_Avg_SYN_ACK_Time.png')
    plt.close()
    plt.clf()

def plot_avg_transmission_time(csv_filename):
    filtered_data = filter_final_proxies_from_csv(csv_filename)
    proto = "HTTP and SOCKS"

    # Erstelle eine Menge mit (IP, Port), um jede Kombination eindeutig zu speichern
    unique_proxies = set()
    for epoch_data in filtered_data:
        for proxy in epoch_data['proxies']:
            unique_proxies.add((proxy['ip'], proxy['port']))

    # Farbschema für jede (IP, Port) Kombination
    color_map = plt.cm.get_cmap('tab20', len(unique_proxies))
    ip_colors = {(ip, port): color_map(i) for i, (ip, port) in enumerate(unique_proxies)}

    # Plotte die Daten
    plt.figure(figsize=(10, 6))

    for epoch_data in filtered_data:
        epoch = epoch_data['epoch']
        for proxy in epoch_data['proxies']:
            ip = proxy['ip']
            port = proxy['port']
            
            jittered_epoch = epoch + np.random.uniform(-0.2, 0.2)

            plt.scatter(jittered_epoch, proxy['avg_transmission_time'], color=ip_colors[(ip, port)])

    plt.xlabel('Epoch')
    plt.ylabel('Average Transmission Time in [s]')
    plt.title(f'Average Transmission Time per Epoch of the {proto} - Protokoll')
    plt.xticks(np.arange(1, 11, 1))

    # Legende mit IP, Port und Typ
    handles = [
        plt.Line2D([0], [0], marker='o', color=ip_colors[(ip, port)], 
                   label=format_label(ip, port), linestyle='') 
        for ip, port in unique_proxies
    ]
    plt.legend(handles=handles, title='Proxies', bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.tight_layout()
    plt.savefig('Plot_Avg_Transmission_Time.png')
    plt.close()
    plt.clf()

def plot_HR_and_RR(csv_filename):
    filtered_data = filter_final_proxies_from_csv(csv_filename)
    proto = "HTTP and SOCKS"
    
    
    unique_proxies = set()
    for epoch_data in filtered_data:
        for proxy in epoch_data['proxies']:
            unique_proxies.add((proxy['ip'], proxy['port']))

    
    color_map = plt.cm.get_cmap('tab20', len(unique_proxies))
    ip_colors = {(ip, port): color_map(i) for i, (ip, port) in enumerate(unique_proxies)}

    
    plt.figure(figsize=(10, 6))

    for epoch_data in filtered_data:
        epoch = epoch_data['epoch']
        for proxy in epoch_data['proxies']:
            ip = proxy['ip']
            port = proxy['port']
            
            jittered_epoch = epoch + np.random.uniform(-0.2, 0.2)

            
            plt.scatter(jittered_epoch, proxy['handshake_rate'], color=ip_colors[(ip, port)], marker='o')

            
            plt.scatter(jittered_epoch, proxy['request_rate'], color=ip_colors[(ip, port)], marker='x')

    plt.xlabel('Epoch')
    plt.ylabel('Rate Values in [%]')
    plt.title(f'Handshake Rate (HR) and Request Rate (RR) per Epoch of the {proto} - Protokoll')
    plt.xticks(np.arange(1, 11, 1))

    
    handles = []
    for ip, port in unique_proxies:
        hr_handle = plt.Line2D([0], [0], marker='o', color=ip_colors[(ip, port)], 
                               label=f'{format_label(ip, port)} HR', linestyle='')
        rr_handle = plt.Line2D([0], [0], marker='x', color=ip_colors[(ip, port)], 
                               label=f'{format_label(ip, port)} RR', linestyle='')
        handles.extend([hr_handle, rr_handle])

    plt.legend(handles=handles, title='Proxies', bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.tight_layout()
    plt.savefig('Plot_Handshake_and_Request_Rate.png')
    plt.close()
    plt.clf()
def move_plots(run_number):
    
    folder_name = f"Lauf_{run_number}"
    
    
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

   
    plot_files = [
        'Proxies_by_avg_score.png',
        'Plot_Avg_Throughput.png',
        'Plot_Avg_Transmission_Time.png',
        'Plot_Avg_SYN_ACK_Time.png',
        'Plot_Handshake_and_Request_Rate.png',
        'avg_score.csv',
        'proxy_data.csv',
        'output.csv'
    ]
    #Move
    
    for plot in plot_files:
        if os.path.exists(plot):  
            shutil.move(plot, os.path.join(folder_name, plot))
        else:
            print(f"Plot {plot} wurde nicht gefunden.")
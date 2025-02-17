import asyncio

"Functions to manage the main"

async def print_proxy_managers(list,arg):
    for proxy_manager_item in list:
        await proxy_manager_item.print_proxy_list(arg)
        

async def sort_proxy_managers(list,proxy_number):
    for proxy_manager_item in list:
        await proxy_manager_item.sort_proxy_lists(proxy_number)

def reset_proxy_objects(list):
    for proxy_manager_item in list:
        proxy_manager_item.reset_proxys() #resets the proxy attributes, logs the score, copys master -> proxy_list, clears master list

def log_scores(list):
    for proxy_manager_item in list:
        proxy_manager_item.log_scores() #Store Scores before Reset



async def dynamic_evaluate_call(proxy_managers_list, counter, evaluation_rounds,proxy_number,num_proto,stop_counter):
    """Dynamic Evaluate - Epoch Amount can be adapted
    Re-Evaluate every 20s, remove not reliable Proxys with avg_score < 100
    
    """
    epoch_number = 10
    while stop_counter < epoch_number: 
        stop_counter += 1
        
        log_scores(proxy_managers_list) #Log Score here before reset AND remove avg_score <= 100
        await print_proxy_managers(proxy_managers_list,"master")
        print("\n\n      ------- Initiated Termination -------\n\n     ^                                         ^\n     |   Here is the final Master Proxy List   |\n")

        print("Wait 20s until Master List re-evaluate. Press ctrl + z to break and show the final List.\n")
        print(f"Epoch Number: {stop_counter}\n")
        for _ in range(20):  # 20 Seconds / 2 Seconds = 10
            
            await asyncio.sleep(1)
                
            print('.', end='',flush=True)
        
        
        print('\nEvaluate Master List again!\n')

        

        reset_proxy_objects(proxy_managers_list) # reset proxy Objects and init Master/Proxy List for new evaluation Update

        re_evaluate_tasks = await generate_evaluate_tasks(proxy_managers_list, counter, evaluation_rounds,proxy_number)
        
        await asyncio.gather(*re_evaluate_tasks)
        await sort_proxy_managers(proxy_managers_list,proxy_number)
        for manager in proxy_managers_list:
                manager.add_epoch_data(epoch_number=stop_counter)
        
        

    await print_proxy_managers(proxy_managers_list,"master")
    
async def generate_evaluate_tasks(proxy_managers_list, counter, evaluation_rounds,proxy_number):
    re_evaluate_tasks = []
    for manager in proxy_managers_list:
        re_evaluate_tasks.append(manager.evaluate_proxy_list(counter, evaluation_rounds,proxy_number))
        
    return re_evaluate_tasks


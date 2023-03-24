
class Config:
    # interarrival time for customers
    interarrival_time = 5
    
    # mean service times for each station (in minutes)
    kitchen_service_time = 3
    counter_service_time = 1
    
    # number of servers at each station
    kitchen_servers = 2
    counter_servers = 1
    
    # maximum queue size for each station
    kitchen_queue_size = 5
    counter_queue_size = 3
    
    # simulation run metrics
    warm_up_time = 60
    sim_duration = 480
    num_runs = 50
    
    # placeholders to track wait times and queue lengths
    kitchen_wait_times = []
    kitchen_queue_lengths = []
    counter_wait_times = []
    counter_queue_lengths = []

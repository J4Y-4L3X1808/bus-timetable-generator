from lxml import etree
from datetime import datetime, timedelta
import os
from tabulate import tabulate
#import tkinter as tk

bus_route_specific = None

def record_lines():
    routes = []
    what_file = {}

    for file in os.listdir():
        if file.endswith(".xml"):
            tree = etree.parse(file)
            root = tree.getroot()

            for journey in root.iter("{*}VehicleJourney"):                                                                                     
                line_ref = journey.find("{*}LineRef").text.split(":")
                line = line_ref[-1]

                if not line in routes:
                    routes.append(line)

                    what_file[line] = file

    return routes, what_file

def record_stops_on_route():
    print("TBC")


#finds the timetable of the route and prints it
def find_timetable(root, what_data):
    for journey in root.iter("{*}VehicleJourney"):                                                          #for each 'journey' in the file...
        column = []
        stop_number = 1
        departure_string = journey.find("{*}DepartureTime").text                                            #get the departure time
        departure = datetime.strptime(departure_string, "%H:%M:%S")
        stop_departure = departure
        current_time = datetime.strptime(str(datetime.now())[11:19], "%H:%M:%S")
        

        if what_data == "Next" and departure < current_time:                                                #checks if the current journey has already occurs and skips ahead to the next journey if so
            continue

        #finds the line reference and checks if it matches what the user inputted
        line_ref = journey.find("{*}LineRef").text.split(":")   
        if bus_route_specific != line_ref[-1]:
            continue

        for interval in journey.iter("{*}VehicleJourneyTimingLink"):                                        #for each stop in the journey
            wait_time = timedelta(minutes = 0)
            time_to_stop = timedelta(minutes = int(interval.find("{*}RunTime").text[2:-1]))                 #find the time it takes to get to each stop

            for wait_time in interval.iter("WaitTime"):                                                     #check if there's a wait time
                wait_time = timedelta(minutes = int(interval.find("{*}WaitTime").text[2:-1]))

            link_ref = interval.find("{*}JourneyPatternTimingLinkRef").text                                 #find the journey timing link ref
            
            for jptlr in root.iter("{*}JourneyPatternTimingLink"):                                          #find the stop point ref corresponding to the jounrey timing link ref
                if jptlr.get("id") == link_ref:
                    stop_point_ref = jptlr.find("{*}From/{*}StopPointRef").text
                    next_stop = jptlr.find("{*}To/{*}StopPointRef").text

                    for stop in root.iter("{*}AnnotatedStopPointRef"):                                      #find the stop name corresponding to the stop point ref
                        stop_point = stop.find("{*}StopPointRef").text
                        if stop_point == stop_point_ref:
                            stop_name = stop.find("{*}CommonName").text

            if stop_number == 1:
                row = [stop_name, departure.time()]
                stop_number += 1  

            else:
                row = [stop_name, stop_departure.time()]

            stop_departure += time_to_stop                                                                  #add the travel time and wait time to the actual time
            stop_departure += wait_time

            column.append(row)

        final_stop = next_stop
        for stop in root.iter("{*}AnnotatedStopPointRef"):                                      
            stop_point = stop.find("{*}StopPointRef").text
            if stop_point == final_stop:
                stop_name = stop.find("{*}CommonName").text
        
        column.append([stop_name, stop_departure.time()])
        table = tabulate(column, headers = ["Stop", "Time"], tablefmt='orgtbl')



        print(table)
        print(" ")
        print("--------------------------")
        print(" ")

        


routes, what_file = record_lines()

what_data = input("Would you like the next buses or all buses? ")

#asks for route until a valid route is given
while not bus_route_specific in routes:
    bus_route_specific = input("Which bus route do you want the timetable of?").upper()

    if not bus_route_specific in routes:
        print("Not a Valid Route, Try Again")

tree = etree.parse(what_file[bus_route_specific])
root = tree.getroot()

find_timetable(root, what_data)





"""
Want to eventually do:
user inputs time and date
returns the services after that time on the correct date

User inputs a stop
returns routes through that stop then prompts the user to input time and date of when
"""






















































#Future Testing / Plans

#goes above while loop
"""
#sets window up
root = tk.Tk()
root.geometry("750x250")
root.configure(background = 'lightblue')

var = tk.StringVar()

#puts heading at the top
tk.Label(root, text = "Bus Information", background='lightblue').grid(row = 0, column = 0)

#displays the 2 options for what_data
tk.Label(root, text = "Would you like the next buses or all buses?", background='lightblue').grid(row = 1, column = 0)
tk.Radiobutton(root, text = "All", background='lightblue', variable = var, value = 1).grid(row = 1, column = 1)
tk.Radiobutton(root, text = "Next", background='lightblue', variable = var, value = 2).grid(row = 1, column = 2)


if var == 1:
    what_data = "All"
elif var == 2:
    what_data = "Next"
"""

#goes inside while loop
""""
tk.Label(root, text="Which Bus Route?", background='lightblue').grid(row = 2, column = 0)
entry = tk.Entry(root)
entry.grid(row = 2, column = 1)
button = tk.Button(root, text= "Submit", command = get_content)
button.grid(row = 2, column = 2)
"""

#in functions list
"""
def get_content():
    print(entry.get())
    print(var.get())
"""

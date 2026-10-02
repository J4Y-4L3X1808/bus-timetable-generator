from lxml import etree
from datetime import datetime, timedelta
import os
from tabulate import tabulate
stop_or_route = None
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


def find_routes_at_stop():
    line_refs = []
    
    chosen_stop = input("What stop? ")

    for file in os.listdir():
        if file.endswith(".xml"):
            tree = etree.parse(file)
            root = tree.getroot()

            for stop in root.iter("{*}AnnotatedStopPointRef"):
                stop_name = stop.find("{*}CommonName").text
                if stop_name == chosen_stop:
                    stop_point_ref = stop.find("{*}StopPointRef").text

                    for jptlr in root.iter("{*}JourneyPatternTimingLink"):
                        if jptlr.find("{*}From/{*}StopPointRef").text == stop_point_ref:
                            jptlr_id = jptlr.get("id")

                            for journey in root.iter("{*}VehicleJourney"):
                                for vehicle_journey_tl in journey.iter("{*}VehicleJourneyTimingLink"):
                                    if vehicle_journey_tl.find("{*}JourneyPatternTimingLinkRef").text == jptlr_id:

                                        for interval in journey.iter("{*}VehicleJourneyTimingLink"):
                                            for jptlr in root.iter("{*}JourneyPatternTimingLink"):
                                                if jptlr.get("id") == jptlr_id:
                                                    line_ref = journey.find("{*}LineRef").text.split(":")
                                                    if not line_ref[-1] in line_refs:
                                                        line_refs.append(line_ref[-1])
    return line_refs


#finds the timetable of the route and prints it
def find_timetable(root, what_data):
    for journey in root.iter("{*}VehicleJourney"):                                                          #for each 'journey' in the file...
        column = []
        stop_number = 1
        departure_string = journey.find("{*}DepartureTime").text                                            #get the departure time
        departure = datetime.strptime(departure_string, "%H:%M:%S")
        stop_departure = departure
        current_time = datetime.strptime(str(datetime.now())[11:19], "%H:%M:%S")
        

        if what_data == "NEXT":
            if departure < current_time:                                                                    #checks if the current journey has already occurs and skips ahead to the next journey if so
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

what_data = input("Would you like the next buses or all buses? ").upper()

while not stop_or_route in ["Stop", "Route"]:
    stop_or_route = input("Would you like to get the timetable for a stop or a route? ")


if stop_or_route == "Stop":
    bus_routes_specific = find_routes_at_stop()
    #print(bus_routes_specific)

    for bus_route_specific in bus_routes_specific:
        tree = etree.parse(what_file[bus_route_specific])
        root = tree.getroot()
        find_timetable(root, what_data)


#asks for route until a valid route is given
if stop_or_route == "Route":
    while not bus_route_specific in routes:
        bus_route_specific = input("Which bus route do you want the timetable of?").upper()
    chosen_stop = "Start"

    if not bus_route_specific in routes:
        print("Not a Valid Route, Try Again")

    tree = etree.parse(what_file[bus_route_specific])
    root = tree.getroot()
    find_timetable(root, what_data)

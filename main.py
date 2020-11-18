import ugfx, gc, wifi, badge, system, time, display, machine
from time import sleep, localtime
import urequests as requests

try:

    departureTimeOld= [None] * 4
    departureRealtimeOld= [None] * 4
    departureTime = [None] * 4
    departureRealtime = [None] * 4

    departureDir= [None] * 4
    departureLine= [None] * 4

    refreshCounter = 0
    updateDisplay = True
    
    while True:
        ugfx.init()
        display.orientation(270)
        try:
            wifi.init()
            while not wifi.sta_if.isconnected():
                sleep(0.1)
        except:
            wifi.connect()
            if not wifi.wait():
                time.sleep(2)
                system.home()


        #############################################################################################################################################################################################
        url = "http://travelplanner.mobiliteit.lu/restproxy/departureBoard?accessId=cdt&id=A=1@O=Lintgen,%20Kräizung@X=6,125115@Y=49,720344@U=82@L=160702003@B=1@p=1594365298&format=json"
        trainURL = "http://travelplanner.mobiliteit.lu/restproxy/departureBoard?accessId=cdt&id=A=1@O=Lintgen,%20gare&format=json"

        while True:
            r = requests.get(url)
            print("HTTP request status Code:",r.status_code)
            #print(r.status_code)
            
            if r.status_code == 200:
                break
            else:
                # Hope it won't 500 a little later
                print("Bad response")
                time.sleep(5)

        #print("Data")
        #print(r.text)

        jsonData = r.json()
        r.close()
        gc.collect()

        print("JSON loaded")
        #print(jsonData)

        #print("length of response:", len(jsonData))
        #length = len(jsonData)
        #print(length)

        #############################################################################################################################################################################################
        
        #####################################FILL IN DATA###############################################
        if len(jsonData) >= 4: #checks that there is returned data other than the 3 entry in the JSON footer
            numOfDepartures = len(jsonData['Departure'])
            print("Number of Departures: ",numOfDepartures)
            if numOfDepartures >= 4:
                numOfDepartures = 4 #cap the number of departure to be printed to 4 as that is the maximum you can fit on screen
            
            for x in range(0, numOfDepartures):
                print("|||||||||||||||||||||| ",x," ||||||||||||||||||||||")
                print(len(jsonData['Departure'][x])," returned cat. if more than 13, it is a late bus") ###
                
                if len(jsonData['Departure'][x]) >= 14:
                    print("Storing departure time")
                    departureTime[x] = jsonData['Departure'][x]['time'] #scheduled times ##problem here
                    departureRealtime[x] = jsonData['Departure'][x]['rtTime'] #real time accounts for delays
                    
                    departureTime[x] = departureTime[x][:-3]
                    departureRealtime[x] = departureRealtime[x][:-3]
                    
                    print("Showing real time as this bus is late:",departureRealtime[x], "instead of:", departureTime[x])
                    
                    if departureTime[x] == departureRealtime[x]:
                        departureRealtime[x] = None # The bus is not late afterall
                        print("The bus is not late afterall")
                else:
                    departureRealtime[x] = None # The bus is not late
                    departureTime[x] = jsonData['Departure'][x]['time'] #scheduled times
                    
                    departureTime[x] = departureTime[x][:-3]
                    print("Showing scheduled time as this bus is on time:",departureTime[x])

                name = jsonData['Departure'][x]['name']
                name = name[:2]
                if name == "RB": #Checks if this is a replacement bus for an RB train
                    departureLine[x] = "RB"
                else:
                    departureLine[x] = jsonData['Departure'][x]['Product']['line']

                departureDir[x] = jsonData['Departure'][x]['direction']
                #print ('"direction":', departureDir)
                #print ('"line":', departureLine)
                
                departureDir[x] = departureDir[x][:12] #max number of char. that can display
                
                print ('"direction":', departureDir[x])
                print ('"line":', departureLine[x])
                print("////////////////////// ",x," //////////////////////")
            
            ##################################### Update display? ###############################################
            print("Checking if new data available compared to what is on the display now")
            updateDisplay = False
            for x in range(0, numOfDepartures):
                #check if new data is different currently displayed data
                if (departureTime[x] != departureTimeOld[x]) or (departureRealtime[x] != departureRealtimeOld[x]):

                    departureTimeOld[x] = departureTime[x]
                    departureRealtimeOld[x] = departureRealtime[x]
                    updateDisplay = True
            ##################################### Update display! ###############################################
            
            if updateDisplay == True:     
                print("~~Updating display~~")    
                
                lut = ugfx.LUT_FASTER
                
                refreshCounter = refreshCounter + 1
                if refreshCounter >= 10: #full deep refresh after 10 normal prints
                    refreshCounter = 0
                    print("Full screen clear")
                    ugfx.clear(ugfx.WHITE)
                    lut = ugfx.LUT_FULL
                else:
                    lut = ugfx.LUT_FASTER
                
                ugfx.string_box(0, -8, 128, 30, "BUS TIME", "Roboto_Black22", ugfx.BLACK, ugfx.justifyCenter) #printing title
                ugfx.area(0, 33+(0)*65, 128, 55, ugfx.BLACK)
                ugfx.flush(lut)

                for x in range(0, numOfDepartures):

                    ugfx.fill_rounded_box (86, 38+x*65, 37, 20, -2, ugfx.WHITE) #printing white box for the line
                    ugfx.string_box(86, 36+x*65, 37, 20, departureLine[x], "Roboto_Regular18", ugfx.BLACK, ugfx.justifyCenter) #printing line in white box
                    #ugfx.string(86+2, 37+x*65, departureLine[x], "Roboto_Regular18", ugfx.BLACK)

                    if departureRealtime[x] == None: #if realtime (if bus is late) is empty print scheduled time
                        ugfx.string(4, 35+x*65, departureTime[x], "Roboto_Black22", ugfx.WHITE)
                    else: #if realtime (if bus is late) is has data print late time
                        ugfx.string(4, 35+x*65, departureRealtime[x], "Roboto_Black22", ugfx.WHITE)
                        #ugfx.fill_circle(x, y, r, colour)
                        ugfx.fill_circle(76, 47+x*65, 5, ugfx.WHITE) #add dot to show the bus is late
                    
                    ugfx.string(4, 35+28+x*65, departureDir[x], "Roboto_Regular18", ugfx.WHITE) # print direction
                    

                    if x+1 < numOfDepartures:
                        ugfx.area(0, 33+(x+1)*65, 128, 55, ugfx.BLACK)
                    else:
                        ugfx.area(0, 33+(x+1)*65, 128, 55, ugfx.WHITE)

                    ugfx.flush(ugfx.LUT_FASTER)
            else:
                print("No change in data, no screen update needed")
        #####################################No data from API###############################################
        else: #no data from API
            print("Number of JSON return: ",0)
            refreshCounter = refreshCounter + 1

            numOfDepartures=0
            ugfx.clear(ugfx.WHITE)
            ugfx.string_box(0, -8, 128, 30, "BUS TIME", "Roboto_Black22", ugfx.BLACK, ugfx.justifyCenter)
            ugfx.flush()

        #############################################################################################################################################################################################


        print("Number of screen prints:",refreshCounter,"will hard refresh at 10")

        badge.eink_busy_wait()

        print("Sleep time~")
        print("################################################################################################################################################################")
        time.sleep(60)
        #system.sleep(60000)
        #deepsleep.start_sleeping(6000)
except:
    print("################################################################################################################################################################")
    print("################################################################################################################################################################")
    print("Something bad happened (blame lack of RAM), exception, we need a reboot")
    print("################################################################################################################################################################")
    print("################################################################################################################################################################")
    #system.reboot()
    machine.reset()

# ################################################################################
# #make app run on boot
# import machine
# machine.nvs_setstr("system", "default_app", "luxPublicTransport")

# ################################################################################
# #install app from store after pushing to Hatchery
# #Hatchery link: https://badge.team/projects/luxpublictransport/

# import wifi, woezel,machine
# wifi.connect()
# wifi.wait()
# woezel.install("luxPublicTransport")
# machine.reset()

# import machine
# machine.reset()
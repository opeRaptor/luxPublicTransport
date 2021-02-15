import gc, wifi, badge, time, display, machine
from time import sleep
import urequests as requests

try:

    departureTimeOld= [None] * 4
    departureRealtimeOld= [None] * 4
    departureTime = [None] * 4
    departureRealtime = [None] * 4

    departureDir= [None] * 4
    departureLine= [None] * 4

    refreshCounter = 10
    updateDisplay = True
###############################################
    BADGE_EINK_LUT_CUSTOM  = -1
    BADGE_EINK_LUT_FULL    =  4
    BADGE_EINK_LUT_NORMAL  =  8
    BADGE_EINK_LUT_FASTER  =  16
    BADGE_EINK_LUT_FASTEST =  32
###############################################

    while True:
        #ugfx.init()
        display.orientation(270)
        
        try:
            wifi.init()
            #wifi.connect()
            while not wifi.sta_if.isconnected():
                sleep(0.1)
        except:
            wifi.connect()
            print("Connecting to WiFi")
            if not wifi.wait():
                time.sleep(2)
                print("Connection Error, Rebooting")
                machine.reset()


        #############################################################################################################################################################################################
        url = "http://travelplanner.mobiliteit.lu/restproxy/departureBoard?accessId=cdt&id=A=1@O=Lintgen,%20Kräizung@X=6,125115@Y=49,720344@U=82@L=160702003@B=1@p=1594365298&format=json"
        trainURL = "http://travelplanner.mobiliteit.lu/restproxy/departureBoard?accessId=cdt&id=A=1@O=Lintgen,%20gare&format=json"
        trustmeURL = "http://192.168.179.1:8186/trustme.lua?accept="
        #r = requests.get("http://192.168.179.1:8186/trustme.lua?accept=")
       ################################ Guest Wifi Portal ######################################### 
        while True:
            trust = requests.get(trustmeURL)
            print("Trust me HTTP request status Code:",trust.status_code)
            #print(r.status_code)
            
            if trust.status_code == 200:
                break
            else:
                # Hope it won't 500 a little later
                print("Bad response")
                time.sleep(5)

        #print("Trustme:",r.text)
        trust.close()
        gc.collect()
        #########################################################################
       
        while True:
            api = requests.get(url)
            print("API HTTP request status Code:",api.status_code)
            #print(r.status_code)
            
            if api.status_code == 200:
                break
            else:
                # Hope it won't 500 a little later
                print("Bad response")
                time.sleep(5)

        #print("Data")
        #print(r.text)

        jsonData = api.json()
        api.close()
        gc.collect()

        print("JSON loaded")
        #print(jsonData)

        #print("length of response:", len(jsonData))
        #length = len(jsonData)
        #print(length)

        #############################################################################################################################################################################################
        
        tempurl= 'http://wttr.in/lintgen?format="%t"'
        while True:
            tempAPI = requests.get(tempurl)
            print("Temperature HTTP request status Code:",tempAPI.status_code)
            #print(r.status_code)
            
            if tempAPI.status_code == 200:
                break
            else:
                # Hope it won't 500 a little later
                print("Bad response")
                time.sleep(5)

        print("Temp Data:",tempAPI.text)

        temp = tempAPI.text[1:]
        
        tempAPI.close()
        gc.collect()

        #temp = "-8dcc"
        if temp[0] == "+":
            temp = temp[1:]
        temp = temp[:-3]

        #print(temp)
        
        #############################################################################################################################################################################################
        
        #####################################FILL IN DATA###############################################
        if len(jsonData) >= 4: #checks that there is returned data other than the 3 entry in the JSON footer
            numOfDepartures = len(jsonData['Departure'])
            print("Number of Departures: ",numOfDepartures)
            if numOfDepartures >= 4:
                numOfDepartures = 4 #cap the number of departure to be printed to 4 as that is the maximum you can fit on screen
            
            for x in range(0, numOfDepartures):
                print("|||||||||||||||||||||| ",x," ||||||||||||||||||||||")
                print(len(jsonData['Departure'][x])," returned cat. if more than 13, it is a late bus and ",departureTime[x], "not equal to",departureRealtime[x]) ###
                
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
                
                #departureDir[x] = departureDir[x][:12] #max number of char. that can display
                while display.getTextWidth(departureDir[x],"Roboto_Black22") >= (128+ 22):
                    departureDir[x] = departureDir[x][:-1]
                    #print("Len of dir.: ",display.getTextWidth(departureDir[x],"Roboto_Black22"))
                    #print("Direction:",departureDir[x])
                
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
                
                lut = BADGE_EINK_LUT_FASTER
                
                refreshCounter = refreshCounter + 1
                if refreshCounter >= 10: #full deep refresh after 10 normal prints
                    refreshCounter = 0
                    print("Full screen clear")
                    #display.clear(0xFFFFFF)
                    display.drawFill(0xFFFFFF)
                    lut = BADGE_EINK_LUT_FULL
                else:
                    lut = BADGE_EINK_LUT_FASTER
                
                #ugfx.string_box(0, -8, 128, 30, "BUS TIME", "Roboto_Black22", ugfx.BLACK, ugfx.justifyCenter) #printing title
                display.drawPng(0,0,"/lib/luxPublicTransport/busBoardV2.png")
                
                display.drawText(106-int(display.getTextWidth(temp,"Roboto_Regular18")/2), 10, temp, 0xFFFFFF, "Roboto_Regular18")

                display.drawCircle(120, 12, 2,0,360,True,0xFFFFFF)
                display.drawCircle(120, 12, 1,0,360,True,0x000000)

                #ugfx.area(0, 45+(0)*65, 128, 55, ugfx.BLACK)
                #display.drawRect(0, 45+(0)*65, 128, 55,True,  0x000000)
                display.drawPng(0, 45+(0)*65,"/lib/luxPublicTransport/busTablets.png")
                display.flush(lut)

                for x in range(0, numOfDepartures):

                    #ugfx.fill_rounded_box (86, 50+x*65, 37, 20, -2, ugfx.WHITE) #printing white box for the line
                    #display.drawRect(86, 50+x*65, 37, 20,True,  0xFFFFFF)
                    #ugfx.string_box(86, 48+x*65, 37, 20, departureLine[x], "Roboto_Regular18", ugfx.BLACK, ugfx.justifyCenter) #printing line in white box
                    display.drawText(86+2, 50+(x*65)+15-int(display.getTextWidth(departureLine[x],"Roboto_Regular18")/2), departureLine[x], 0x000000, "Roboto_Regular18")
                    #ugfx.string(86+2, 37+x*65, departureLine[x], "Roboto_Regular18", ugfx.BLACK)

                    if departureRealtime[x] == None: #if realtime (if bus is late) is empty print scheduled time
                        #ugfx.string(4, 47+x*65, departureTime[x], "Roboto_Black22", ugfx.WHITE)
                        display.drawText(4, 47+x*65, departureTime[x], 0xFFFFFF, "Roboto_Black22")
                    else: #if realtime (if bus is late) is has data print late time
                        #ugfx.string(4, 47+x*65, departureRealtime[x], "Roboto_Black22", ugfx.WHITE)
                        display.drawText(4, 47+x*65, departureRealtime[x], 0xFFFFFF, "Roboto_Black22")
                        #ugfx.fill_circle(x, y, r, colour)
                        #ugfx.fill_circle(76, 57+x*65, 5, ugfx.WHITE) #add dot to show the bus is late
                        display.drawCircle(76, 59+x*65, 3,0,360,True,0xffffff)
                    
                    #ugfx.string(4, 45+28+x*65, departureDir[x], "Roboto_Regular18", ugfx.WHITE) # print direction
                    display.drawText(4, 45+30+x*65, departureDir[x], 0xFFFFFF, "Roboto_Regular18")
                    

                    if x+1 < numOfDepartures:
                        #ugfx.area(0, 45+(x+1)*65, 128, 55, ugfx.BLACK)
                        #display.drawRect(0, 45+(x+1)*65, 128, 55,True,  0x000000)
                        display.drawPng(0, 45+(x+1)*65,"/lib/luxPublicTransport/busTablets.png")
                    else:
                        #ugfx.area(0, 45+(x+1)*65, 128, 55, ugfx.WHITE)
                        display.drawRect(0, 45+(x+1)*65, 128, 55,True,  0xFFFFFF)

                    display.flush(BADGE_EINK_LUT_FASTER)
            else:
                print("No change in data, no screen update needed")
        #####################################No data from API###############################################
        else: #no data from API
            print("Number of JSON return: ",0)
            refreshCounter = refreshCounter + 1

            numOfDepartures=0
            #ugfx.clear(ugfx.WHITE)
            #display.clear(0xFFFFFF)
            display.drawFill(0xFFFFFF)
            #ugfx.string_box(0, -8, 128, 30, "BUS TIME", "Roboto_Black22", ugfx.BLACK, ugfx.justifyCenter)
            display.drawPng(0,0,"/lib/luxPublicTransport/busBoardV2.png")
            
            display.drawText(106-int(display.getTextWidth(temp,"Roboto_Regular18")/2), 10, temp, 0xFFFFFF, "Roboto_Regular18")
            display.drawCircle(120, 12, 2,0,360,True,0xFFFFFF)
            display.drawCircle(120, 12, 1,0,360,True,0x000000)
            display.flush()

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


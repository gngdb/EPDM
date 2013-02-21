def dload(fname):
    #open DUMP_FILE
    f = open(fname)

    data = []

    #add the data to data, line by line
    for line in f:
        data.append(line)

    f.close()

    import string

    #split the data up by the | character
    data = map(lambda x: string.split(x, "|"), data[:])
    #turn all the strings into floats
    data = map(lambda x: map(lambda y: float(y), x), data[:])

    return data

def powercalc(line):
    #assuming balanced circuit, find power consumption
    Ra = line[0]
    Rb = line[1]
    Rc = line[2]
    Rd = line[3]
    Ve = line[4]
    Rf = line[5]
    Ry = 2.0
    #Using thevenins theorem, Vy is the point next to Rb
    Vthy = (Ve*(Rd+Rf))/(Rd+Rc+Rf)
    Rthy = Ry + (Rf*(Rd+Rc))/(Rf+Rd+Rc)
    Ithy = Vthy/(Rthy+Rb)
    Vy = (Rb*Vthy)/(Rthy+Rb)
    Pb = Vy*Ithy
    #Vz is the point next to Rc
    Vthz = (Ve*(Ry+Rb))/(Rf+Ry+Rb)
    Rthz = (Rf*(Ry+Rb))/(Rf+Ry+Rb) + Rd
    Ithz = Ve/(Rthz + Rc)
    Vz = (Vthz*Rc)/(Rthz+Rc)
    Pc = Ithz*Vz
    #Vx is the point next to Rf
    Vx = (Ve*(Ry+Rb)*(Rd+Rc))/((Ry+Rb)*(Rd+Rc)+Rf*(Ry+Rb+Rd+Rc))
    Pd = (Vx**2)/Rd
    Pf = ((Ve-Vz)**2)/Rf
    Rtot = Rf + ((Ry+Rb)*(Rd+Rc))/(Ry+Rb+Rd+Rc)
    power = (Ve**2)/Rtot
    return [power,Pb, Pc, Pd, Pf]

def iterator():
    #monte carlo iterator to run the test many times with random values
    import random
    import math
    
    data = dload("DUMP_FILE") 
    #infer what Rc should be on each line
    data2= []
    for line in data:
        Rc = (line[2]*line[1])/2
        data2.append(line[0:2]+[Rc]+line[2:])

    #modulate with random variable
    #query before doing this, so test can also work without this
    #good old infinite loop
    while 1:
        #user query
        uq = raw_input("Run Monte Carlo(mc) or nominal(n):\n")
        if uq == "mc":
            #query for resistor tolerance
            tol = float(raw_input("Resistor Tolerance(in %):"))/100
            psv = float(raw_input("Power supply standard deviation(in %):"))/100
            #run Monte Carlo
            datalist = []
            for i in xrange(1000):
                print "iteration %s/1000"%(i+1)
                #modulate all resistor values and power supply as Gaussian random variables
                mcdata = []
                for line in data2:
                    #new line
                    nl=[]
                    for R in line[:4]:
                        nl.append(random.gauss(R, tol*R/5.9))
                    nl.append(random.gauss(line[4],line[4]*psv))
                    nl.append(random.gauss(line[5], tol*line[5]/5.9))
                    mcdata.append(nl)
                datalist.append(begin(mcdata))
            print "Monte Carlo complete"
            print "Processing..."
            #use the output data to calculate variations in output variables
            mcout = []
            #the data is a list of list of lists at this point
            for line in zip(*datalist):
                #so unpack it into lists and zip each row into a tuple of lists
                #then unpack the tuple into lists and then zip these lists into tuples
                #so now each tuple in the data is each output of the Monte Carlo
                linz = zip(*line)
                avgs = []
                #calculate average of each tuple and add it to a list
                for x in linz:
                    avgs.append(sum(x)/len(x))
                #do the same with standard deviations
                sigmas = []
                for x, avg in zip(linz, avgs):
                    s = map(lambda y: (y-avg)**2, x)
                    sigmas.append(math.sqrt(sum(s)/len(s))) 
                #estimate yield from both dys
                ylds = []
                #make a list of the averages and sigmas in tuples, then throw away all but the dys
                for x in zip(avgs, sigmas)[:2]:
                    ylds.append(x[0]/x[1])
                #smallest yield is the worst yield
                yld = min(ylds)
                #estimate worst case power consumption
                pwc = avgs[2]+6*sigmas[2]
                #esimate worst case accuracy
                dywcs = []
                for x in zip(avgs, sigmas)[:2]:
                    dywcs.append(x[0]+6*x[1])
                dywc = max(dywcs)
                #estimate worst case power consumption for each resistor
                Rwcs = []
                for x in zip(avgs,sigmas)[2:]:
                    Rwcs.append(x[0]+6*x[1])
                #append results to list
                mcout.append([dywc,pwc,yld]+Rwcs)
            
            #write results to output file
            f = open("LOAD_FILE", "w")
            for x in mcout:
                y = range(len(x))
                y.reverse()
                for z in zip(x,y):
                    if z[1]==0:
                        f.write("%f\n"%z[0])
                    else:
                        f.write("%f|"%z[0])
                    #f.write("%f|%f|%f\n"%(x[0],x[1],x[2]))           
            f.close()
            print "Processing complete"
            break
        elif uq == "n":
            #run nominal
            odata = begin(data2)
            #probably just change this bit to a simple for loop
            #odata = map(lambda x: [max(x[:2]),x[2:]],odata[:])
            odata2 = []
            for line in odata[:]:
                l2 = [max(line[:2])]
                l2.extend(line[2:])
                odata2.append(l2)
            #write results to output file
            f = open("LOAD_FILE", "w")
            for x in odata2:
                y = range(len(x))
                y.reverse()
                for z in zip(x,y):
                    if z[1]==0:
                        f.write("%f\n"%z[0])
                    else:
                        f.write("%f|"%z[0])
            f.close()
            break
        elif uq == "\n":
            break
    return None

def begin(data):
    #this code is terrible
    import os 
    import pdb

    data2= []
    for line in data:
        data2.append(line + [0.0002]) 

    #add unbalanced current

    f = open("DUMP_FILE_PATCH", "w")

    for line in data2:
        for x in line[:]:
            if x == line[-1]:
                f.write("%f"%x)
            else:
                f.write("%f|"%x)
        f.write("\n")
            #f.write("%f|%f|%f|%f|%f|%f|%f\n"%(line[0], line[1], line[2], line[3], line[4], line[5], line[6]))
    
    f.close()

    #execute c code on command line
    os.system("./bridge")

    #read in results
    hy = dload("LOAD_FILE")
    dy1 = map(lambda x: 2.0-x[0], hy)

    data2= []
    for line in data:
        Rc = (line[2]*line[1])/2
        data2.append(line + [-0.0002]) 

    f = open("DUMP_FILE_PATCH", "w")

    for line in data2:
        for x in line[:]:
            if x == line[-1]:
                f.write("%f"%x)
            else:
                f.write("%f|"%x)
        f.write("\n")
            #f.write("%f|%f|%f|%f|%f|%f|%f\n"%(line[0], line[1], line[2], line[3], line[4], line[5], line[6]))
    
    f.close()   

    #execute c code on command line
    os.system("./bridge")

    #read in results
    ly = dload("LOAD_FILE")

    dy2 = map(lambda x: x[0]-2.0, ly)

    #dy = map(lambda x: (x[1][0]-x[0][0])/2, zip(hy,ly))

    #dy=[]
    #for x in zip(dy1,dy2):
    #    dy.append(max(x))
    #    if x[0] < 0:
    #        print "Warning, circuit no longer detects 2 Ohm resistors"
    #    else if x[1] < 0:
    #        print "Warning, circuit no longer detects 2 Ohm resistors"


    plist = []
    #calculate power consumption   
    for line in data2:
        plist.append(powercalc(line))

    odata = zip(dy1, dy2, *zip(*plist))

    #f = open("LOAD_FILE", "w")

    #for x in odata:
    #    f.write("%f|%f\n"%(x[0],x[1]))
    
    #f.close()

    return odata 

if __name__ == "__main__":
    iterator()


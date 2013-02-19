def dload(fname):
    f = open(fname)

    data = []

    for line in f:
        data.append(line)

    f.close()

    import string

    data = map(lambda x: string.split(x, "|"), data[:])
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
    Rtot = Rf + ((2+Rb)*(Rd+Rc))/(2+Rb+Rd+Rc)
    power = (Ve**2)/Rtot
    return power

def iterator():
    #monte carlo iterator to run the test many times with random values
    import random
    import math
    
    data = dload("DUMP_FILE") 
    
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
            #run Monte Carlo
            datalist = []
            for i in xrange(1000):
                print "iteration %s/1000"%(i+1)
                #modulate all resistor values as Gaussian random variables
                mcdata = []
                for line in data2:
                    #new line
                    nl=[]
                    for R in line[:4]:
                        nl.append(random.gauss(R, tol*R/5.9))
                    nl.append(line[4])
                    nl.append(random.gauss(line[5], tol*line[5]/5.9))
                    mcdata.append(nl)
                datalist.append(begin(mcdata))
            #use the output data to calculate variations in output variables
            mcout = []
            for line in zip(*datalist):
                #unpack the line and zip for all the data
                linz = zip(*line)
                avgs = []
                #calculate averages
                for x in linz:
                    avgs.append(sum(x)/len(x))
                sigmas = []
                for x, avg in zip(linz, avgs):
                    s = map(lambda y: (y-avg)**2, x)
                    sigmas.append(math.sqrt(sum(s)/len(s))) 
                #estimate yield from both dys
                ylds = []
                for x in zip(avgs, sigmas)[:2]:
                    ylds.append(x[0]/x[1])
                yld = min(ylds)
                #estimate worst case power consumption
                pwc = avgs[2]+6*sigmas[2]
                #esimate worst case accuracy
                dywcs = []
                for x in zip(avgs, sigmas)[:2]:
                    dywcs.append(x[0]+6*x[1])
                dywc = max(dywcs)
                #append results to list
                mcout.append([dywc,pwc,yld])
            
            #write results to output file
            f = open("LOAD_FILE", "w")
            for x in mcout:
                f.write("%f|%f|%f\n"%(x[0],x[1],x[2]))           
            f.close()
            print "Monte Carlo complete"
            break
        elif uq == "n":
            #run nominal
            odata = begin(data2)
            odata = map(lambda x: [[max(x[:2])]+[x[2]]],odata[:])
            #write results to output file
            f = open("LOAD_FILE", "w")
            for x in odata:
                f.write("%f|%f\n"%(x[0][0],x[0][1]))
            f.close()
            break
        elif uq == "\n":
            break

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

    odata = zip(dy1, dy2, plist)

    #f = open("LOAD_FILE", "w")

    #for x in odata:
    #    f.write("%f|%f\n"%(x[0],x[1]))
    
    #f.close()

    return odata 

if __name__ == "__main__":
    iterator()


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
    
    data = dload("DUMP_FILE") 

    data2= []
    for line in data:
        Rc = (line[2]*line[1])/2
        data2.append(line[0:2]+[Rc]+line[2:]

    #modulate with random variable
    #query before doing this, so test can also work without this

def begin(data):
    #this code is terrible
    import os 

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


    #print hy

    data2= []
    for line in data:
        Rc = (line[2]*line[1])/2
        data2.append(line[0:2]+[Rc]+line[2:] + [-0.0002]) 

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

    #print ly

    dy = map(lambda x: (x[1][0]-x[0][0])/2, zip(hy,ly))

    #print dy

    plist = []
    #calculate power consumption   
    for line in data:
        plist.append(powercalc(line))

    odata = zip(dy, plist)

    f = open("LOAD_FILE", "w")

    for x in odata:
        f.write("%f|%f\n"%(x[0],x[1]))
    
    f.close()

    return None

if __name__ == "__main__":
    begin()


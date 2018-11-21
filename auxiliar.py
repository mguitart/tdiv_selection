'''
Script to read a csv with a list of discharges (with certain charachteristics), and plot it's divertor temperature, to decide which ones to get
'''

import csv
import dd
import matplotlib.pylab as plt
import numpy as np
from utils import rebin
from utils import Utils
import sys
sys.path.append('/afs/ipp/u/mcavedon/repository/python/')
from ddPlus import XVS

def rebin (lst_x, lst_y):
    r_x = []
    r_y = []
    W = 10  # desired bin width
    for i in range(0, len(lst_x), W):
        r_x.append(lst_x[i])
        avg=0
        n=0
        for j in range (0, W-1):
            if i+j< len(lst_y):
                n+=1
                avg += lst_y[i+j]
        r_y.append(avg/(W-1))
    return [r_x, r_y]

#read the shotfiles of the csv and save them in a list
def openJournal(path):
    shotfiles = []
    with open('journal.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                #print 'shotfile : ' + row[0]
                shotfiles.append(row[0])
                line_count += 1
        print 'Processed ' +str(line_count) +' lines.'
    return shotfiles


class TDiv:

    def __init__(self, shot):
        self.
        self.Tdiv = None
        self.shotfile = shot
        self.avg_Tdiv = None
        self.err_y = None
        self.valid = True
        self.createTdiv(shot)

    def createTdiv(self, i):
        dds = dd.shotfile('DDS', int(i))
        self.Tdiv = dds('Tdiv')
        dds.close()
        #make all same dimentions
        if self.Tdiv.data.size == 4501: #most of them
            self.Tdiv.data = np.delete(Tdiv.data, -1)
            self.Tdiv.time = np.delete(Tdiv.time, -1)
        elif self.Tdiv.data.size == 4500:
            pass
        else:
            self.valid = False
            return

        indexTime = np.arange(Tdiv.time.shape[0])[(Tdiv.time > t_ini) & (Tdiv.time < t_end )]

        aux_time = []
        aux_data = []
        for t in indexTime:

            aux_data.append(Tdiv.data[t])
            aux_time.append(Tdiv.time[t])

        self.shotfile = i
        self.avg_Tdiv = np.mean(aux_data)
        self.err_y = np.std(aux_data)



    def spectra(self, shot, t_ini, t_end, ax):

        evs = XVS.XVS('EVS',shot,smear_correction=False) #calling the class
        evs.select_time(t_ini , t_end)
        los = 'DOT-04'
        jlos = np.where(evs.losnam == los)[0][0]
        ax.plot(evs.wavel[jlos],evs.intensity.data.mean(axis=0)[jlos],label='high')

        #evs.contour_plot(losname=los,log=True)


    def Tdiv_rebin(self, Tdiv):
        binned_Tdiv = np.zeros_like(self.Tdiv.data)
        binned_Tdiv.resize(450)
        time = np.zeros_like(self.Tdiv.time)
        time.resize(450)

        rb = rebin(self.Tdiv.time[:], self.Tdiv.data[:])
        time = rb[0]
        for t in range(0, len(rb[0])):
            binned_Tdiv[t]= rb[1][t]
        self.binned_Tdiv = binned_Tdiv
        return binned_Tdiv, time


###############################%main#######################################
def main():

    shotfiles = openJournal('journal.csv', shotfiles)


    #plot the Tdiv of these shotfiles
    #change it as wished
    t_ini = 3
    t_end = 4

    valid_shotfiles = []
    avg_Tdiv = []
    err_y = []
    for i in shotfiles:
        shot = Tdiv(i)
        if shot.valid:
            valid_shotfiles.append(shot)
            avg_Tdiv.append(shot.avg_Tdiv) #mean
            err_y.append(shot.err_y)     #standard deviation

    #plt.errorbar(aux_shotfiles, avg_Tdiv , yerr= err_y, color = 'r', ecolor='k', fmt =  'o')
    #plt.grid()
    #plt.show()

    #create hystogram
    bins= [-5,0,5,10,15,20,25,30,40,50,60,70,150]
    hist = np.histogram(avg_Tdiv, bins=bins)
    #plt.hist(avg_Tdiv, bins=bins)
    #splt.show(block= True)
    shotfiles_dict = {}
    for i in range(len(valid_shotfiles)):
        shotfiles_dict[str(avg_Tdiv[i])] = valid_shotfiles[i]
    sort = np.sort(avg_Tdiv)
    bi = 0
    dbins = {}
    for b in bins:
       dbins[str(b)] = []

    for avg in sort:
       for i in range(bi, len(bins)):
           if bins[i] < avg:
               bi = i
           else:
               break
       dbins[str(bins[bi])].append([avg, shotfiles_dict[str(avg)]])


    #f, (ax1,ax2, ax3, ax4) = plt.subplots(4, 1, figsize = (15,10)) #sharex = 'col', sharey = 'row'
    for key in dbins:
        for shot in dbins[key]:
            f, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize = (15,10))
            shotfile =  j[1]
            spectra(int(shotfile.shot), 0, 8, ax1)        #plot spectra
            spectra(int(shotfile.shot), t_ini, t_end, ax2)#plot averaged spectra for specified time window

            Tdiv = shotfile.Tdiv

            uvs = dd.shotfile('UVS', shotfile.shot)
            D_tot = uvs('D_tot')
            N_tot = uvs('N_tot')
            uvs.close()

            #rebin IDL
            Tdiv_binned, time = shotfile.Tdiv_rebin()
            ax3.plot(Tdiv.time, Tdiv.data, 'b')
            ax3.plot(time,Tdiv_binned, 'r')
            ax4.plot(D_tot.time, D_tot.data, 'k', label= 'Dtot')
            ax4.plot(N_tot.time, N_tot.data, 'r', label= 'Ntot')
            ax4.legend()
            plt.show()

if __name__ == '__main__':
    main()

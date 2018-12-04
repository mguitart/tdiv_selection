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


def plotting(ax1, ax2, ax3, t_ini, t_end):

    ax1.set_title('Spectra')
    ax1.set_ylabel('N')
    ax1.set_xlabel('wavelength [nm]')
    ax1.grid()
    ax1.set_ylim([0.0, 6e19])
    ax1.set_xlim([396 , 411])
    ax1.legend()

    ax2.set_ylabel('Tdiv')
    ax2.set_xlabel('time [s]')
    ax2.set_ylim([-20, 150])
    ax2.set_xlim([0 , 8])
    ax2.axvline(t_ini,  lw=2, alpha=0.5)
    ax2.axvline(t_end,  lw=2, alpha=0.5)
    x = [t_ini, t_ini, t_end, t_end]
    y = [200, -50, -50, 200]
    ax2.fill(x,y, facecolor = 'grey', alpha = 0.5)
    ax2.grid()
    ax2.legend()

    ax3.set_ylabel('Gas Flux [1/s]')
    ax3.set_xlabel('time [s]')
    #ax3.set_ylim([-20, 150])
    ax3.set_xlim([0 , 8])
    ax3.grid()
    ax3.legend()


class TDiv:

    def __init__(self, shot, t_ini, t_end):
        self.Tdiv = None
        self.shotfile = shot
        self.avg_Tdiv = None
        self.err_y = None
        self.valid = True
        self.data = None
        self.jlos = None
        self.los = None
        self.createTdiv(shot, t_ini, t_end)

    def createTdiv(self, i, t_ini, t_end):
        dds = dd.shotfile('DDS', int(i))
        self.Tdiv = dds('Tdiv')
        dds.close()

        uvs = dd.shotfile('UVS', int(i))
        self.D_tot = uvs('D_tot')
        self.N_tot = uvs('N_tot')
        uvs.close()

        #make all same dimentions
        if self.Tdiv.data.size == 4501: #most of them
            self.Tdiv.data = np.delete(self.Tdiv.data, -1)
            self.Tdiv.time = np.delete(self.Tdiv.time, -1)
        elif self.Tdiv.data.size == 4500:
            pass
        else:
            #print('Invalid')
            self.valid = False
            return

        indexTime = np.arange(self.Tdiv.time.shape[0])[(self.Tdiv.time > t_ini) & (self.Tdiv.time < t_end )]

        aux_time = []
        aux_data = []
        for t in indexTime:

            aux_data.append(self.Tdiv.data[t])
            aux_time.append(self.Tdiv.time[t])

        self.shotfile = i
        self.avg_Tdiv = np.mean(aux_data)
        self.err_y = np.std(aux_data)



    def spectra(self, shot, t_ini, t_end, ax, col, style, line,  lab):
        #comment either fvs or evs
        '''
        fvs = XVS.XVS('FVS',shot,smear_correction=False) #calling the class
        fvs.select_time(t_ini , t_end)
        los = 'DOT-03' #change it as one wishes
        jlos = np.where(fvs.losnam == los)[0][0]
        ax.plot(fvs.wavel[jlos],fvs.intensity.data.mean(axis=0)[jlos],color = col, marker = style,linestyle = line,  label= lab)
        self.data = fvs

        '''
        evs = XVS.XVS('EVS',shot,smear_correction=False) #calling the class
        evs.select_time(t_ini , t_end)
        los = 'DOT-04' #change it as one wishes
        jlos = np.where(evs.losnam == los)[0][0]
        ax.plot(evs.wavel[jlos],evs.intensity.data.mean(axis=0)[jlos],color = col, marker = style,linestyle = line,  label= lab)
        self.data = evs
        

        self.jlos = jlos
        self.los = los

    def Tdiv_rebin(self):
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


################################## main ########################################
def main():

    shotfiles = openJournal('journal.csv') #lists the shotfiles


    #gets the Tdiv of these shotfiles
    #change it as wished
    t_ini = 2.
    t_end = 3.
    x_position = float((t_end + t_ini)/2)

    valid_shotfiles = []
    avg_Tdiv = []
    err_y = []
    for i in shotfiles:
        shot = TDiv(i, t_ini, t_end)
        if shot.valid:
            print shot.valid
            print shot.avg_Tdiv
            valid_shotfiles.append(shot)
            avg_Tdiv.append(shot.avg_Tdiv)#mean
            
            err_y.append(shot.err_y)     #standard deviation
            
    ordenat_Tdiv = np.sort(avg_Tdiv)
    #print ordenat_Tdiv
    #plt.errorbar(, avg_Tdiv , yerr= err_y, color = 'r', ecolor='k', fmt =  'o')
    #plt.grid()
    #plt.show()


    #create hystogram
    bins= [-5,0,5,10,15,20,25,30,40,50,60,70,150]
    hist = np.histogram(avg_Tdiv, bins=bins)
    #print hist
    plt.hist(avg_Tdiv, bins=bins)
    plt.show(block= True)
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


    for key in dbins: #each bin
        plt.plot([1, 2, 3], [2, 2, 2])
        plt.title('bin: '+ key, size = 18)
        plt.show()
        for shot in dbins[key]: # each shotfile 
            f, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize = (15,15))
            f.suptitle('bin = '+ str(key)+'. Shotfile ' + str(shot[1].shotfile), size = 30)
            print shot[1].shotfile
            shotfile =  shot[1]
            try:
                shotfile.spectra(int(shotfile.shotfile),     0,     8, ax1, 'r', '' , '-', 'averaged_spectra')        #plot spectra
                shotfile.spectra(int(shotfile.shotfile), t_ini, t_end, ax1, 'b', '' , '-', 'window_averaged_spectra')#plot averaged spectra for specified time window
            
            except:
                print 'error: '  + str(shot[1].shotfile)
                continue
            print shotfile.avg_Tdiv
            Tdiv = shotfile.Tdiv
            D_tot = shotfile.D_tot
            N_tot = shotfile.N_tot

            #rebin IDL
            Tdiv_binned, time = shotfile.Tdiv_rebin()

            ax2.plot(Tdiv.time, Tdiv.data, 'b', label = 'Tdiv')
            ax2.plot(time,Tdiv_binned, 'r', label = 'binned_Tdiv')
            ax2.errorbar(x_position, shotfile.avg_Tdiv, yerr= shotfile.err_y, color = 'g', ecolor='k',elinewidth = 2,  fmt =  'o', label = 'average_Tdiv' , markersize = 8)

            ax3.plot(D_tot.time, D_tot.data, 'k', label= 'Dtot')
            ax3.plot(N_tot.time, N_tot.data, 'r', label= 'Ntot')

            plotting(ax1, ax2, ax3, t_ini, t_end)
            plt.show()


if __name__ == '__main__':
    main()

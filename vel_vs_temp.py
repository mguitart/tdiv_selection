'''
Program to calculate the velocity for specific shotfiles

'''

import numpy as np
import matplotlib.pylab as plt
from matplotlib import cm
import sys
sys.path.append('/afs/ipp/u/mcavedon/repository/python/')
from ddPlus import XVS
import dd
from auxiliar import rebin, plotting
from auxiliar import TDiv
from utils import Utils
from Gaussian import lmfit_gauss_single
from lmfit import  Parameters, minimize, fit_report
import math
from colors import Colors


#################################functions##########################################

lmbd_bck_0 = 404.6
lmbd_bck_1 = 405.5

def lmfit_fit_single(lmbd, binned_data, i, lmbd_0, lmbd_end, t):

    x = lmbd[i,:][( lmbd[i,:] > lmbd_0) & ( lmbd[i,:] < lmbd_end)]

    y = binned_data[t,i,:][( lmbd[i,:] > lmbd_0) & ( lmbd[i,:] < lmbd_end)]
    
    bck = np.mean(binned_data[t,i,:][( lmbd[i,:] > lmbd_bck_0) & ( lmbd[i,:] < lmbd_bck_1)])

    pars = Parameters()    
    pars.add('a_0' , value = 2e18  ,  min = 0 )
    pars.add('b_0' , value = 0.01  ,  min = -0.1 ,  max = 0.10)
    pars.add('c_0' , value = 0.05  ,  min = 0.01 ,  max = 0.1)

    pars.add('bck' , value = bck)
    pars['bck'].vary = False
    
    out = minimize(lmfit_gauss_single, pars, method = 'leastsq',  args=(x,), kws={ 'data': y})

    #print fit_report(out)
    return out
    
#####################################main#####################################################

def main():
    

   # shotfiles_dict = {'34684':[7, 8], '34267':[5, 6], '34266':[7, 8], '34467':[5, 6], '34684':[4, 5], '34273':[3,4], '34281':[2.5, 3.5], '34467':[5, 6], '34278':[5, 6], '34443':[4, 5], '34280':[5, 6], '34281':[2.5, 3.5], '34278':[5, 6],, '34443':[4, 5], '34536':[2.5, 3.5], '34445':[2.8, 3.8], '34535':[1.8, 2.6], '34386':[3, 4], '34165':[4, 5], '34532':[6, 7], '34178':[5, 6], '34267':[5, 6], '34264':[2.5, 3.5] ,'34358':[2.5, 3.5], '34279':[4, 5], '34177':[3, 4], '34385':[3.5, 4.5], '34382':[2.5, 3.5], '34382':[2.5, 3.5], '34642':[4, 5] , '34277':[2.5, 3.5], '34275':[2.8, 3.5], '34265':[4.5, 5.5], '34359':[2.5, 3.5] , '34164':[2, 3], '34179':[4, 4.8], '34441':[2.7, 3.5], '34639':[3.3, 3.7], '34189':[5.6, 6.58], '34492':[4, 5], '34536':[2.5, 3.5], '34654':[2.14, 3.14], '34647':[2.2, 2.95],  '34379':[2.5, 3.0],'34381':[4, 5],

    shotfiles_dict = { '34865':[3, 4], '34980':[5.5, 6.5],'34981':[2.8, 3.8], '34829':[5, 5.85], '34979':[5, 5.8], '34971':[4.3, 4.9], '35151':[4, 5], '35152':[5, 6], '35155':[4, 5], '35156':[4, 5], '35157':[3, 4], '35158':[3, 4], '35165':[4.5, 5.5], '35167':[3.5 , 4.5], '35169':[3, 4], '35173':[4.3, 5], '35174':[4, 5], '35175':[4, 5], '35176':[3, 4], '35177':[2.5, 3.5],'35191':[4, 5], '34822':[2.2, 3.2], '34823':[3, 4],  '34829':[5.1, 5.85], '34861':[2.2 , 8.1], '34973':[4 , 4.8], '35155':[3 , 4], '35158':[3 , 4], '35168':[4 , 5], '35217':[2.5 , 3.5] , '35218':[6.2 , 7.2], '35219':[2.5 , 3.5], '35220':[2 , 3], '35221':[2 , 3], '35222':[4 , 5], '35223':[2 , 3], '35224':[5.5 , 6.5], '35225':[4.9 , 5.8], '35226':[4.1 , 5], '35227':[4 , 5]}
# '35185':[4.3,5] , '35189':[2,3], '35190':[3,4] , '35192':[4,5] , '35193':[3.5,4.5] , '35194':[3.5,4.5], '35195':[3,4] , '35196':[4.5,5.5], shotfiles without nitrogen puffed in


    lambda_0 =  399.4997
    c = 299792458 #m/s
    k =1

    '''choose spectormeter and LOS'''
    #spec = 'EVS'
    spec = 'FVS'
    #los = 'DOT-03'
    los = 'DOT-03'


    for shot in shotfiles_dict:
        
        #if True:
        try:
            t_ini = shotfiles_dict[shot][0]
            t_end = shotfiles_dict[shot][1]
            x_position = float((float(t_ini) + float(t_end))/2)
            
            shotfile = TDiv(int(shot), t_ini, t_end, spec, los) #creates the object and creates avg_Tdiv & err_y
            shotfiles_dict[shot].append(shotfile.avg_Tdiv)
            shotfiles_dict[shot].append(shotfile.err_y)

            if False:#int(shot) >= 35179: #False: #int(shot) in  [35162, 35163, 35167]: #True for plotting
           
                f, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize = (15,15))
                
                uncert = abs((shotfile.err_y) /  (shotfile.avg_Tdiv)*100)
                uncert = str(round(uncert,1))              #save only two decimals from uncert
                str_Tdiv = str(round(shotfile.avg_Tdiv,1)) #save only two decimals from Tdiv
                f.suptitle('Shotfile ' + shot + '\n' + ' Avg_Tdiv = '+ str_Tdiv  + " w/ uncertainty: " + str(uncert) + '%', size = 30)
            
                
                '''spectra for plotting, spectra2 for not plotting'''
                
                shotfile.spectra(int(shotfile.shotfile),     0,     8, ax1, 'r', '' ,'-', 'averaged_spectra')        
                shotfile.spectra(int(shotfile.shotfile), t_ini, t_end, ax1, 'b', 'o','' , 'window_averaged_spectra')

            #if True, uncomment
            shotfile.spectra2(int(shotfile.shotfile),     0,     8)   
            shotfile.spectra2(int(shotfile.shotfile), t_ini, t_end)

            averaged_data = np.zeros(shape = (1, shotfile.data.nch, 512))
            averaged_data[0,:,:] =  shotfile.data.intensity.data.mean(axis=0)

            try:
                popt_lmfit = lmfit_fit_single(shotfile.data.wavel, averaged_data, shotfile.jlos, 398.5, 399.75, 0) 
            except:
                popt_lmfit = lmfit_fit_single(shotfile.data.wavel, averaged_data, shotfile.jlos, 399.2, 399.75, 0)


            shift = popt_lmfit.params['b_0'].value
            vel = shift*c/(lambda_0*1000)
            shotfiles_dict[shot].append(vel)
            shotfiles_dict[shot].append(popt_lmfit.params['b_0'].stderr*c/(lambda_0*1000))
            shotfiles_dict[shot].append(popt_lmfit.params['a_0'].value)


            if False:#True:#int(shot) >= 35179: # False: #int(shot) in [35162, 35163, 35167]: #shot == '34536': #True for plotting
            
                xx = np.linspace(398.5 , 399.75,  1000)
                ax1.plot(xx,lmfit_gauss_single(popt_lmfit.params, xx), color= 'g' , ls= '-', label = 'fitting of N1 peak')
                
                Tdiv_binned, time = shotfile.Tdiv_rebin()
                ax2.plot(shotfile.Tdiv.time, shotfile.Tdiv.data, 'b', label = 'Tdiv')
                ax2.plot(time,Tdiv_binned, 'r', label = 'binned_Tdiv')
                ax2.errorbar(x_position, shotfile.avg_Tdiv, yerr= shotfile.err_y, color = 'g', ecolor='k',elinewidth = 2,  fmt =  'o', label = 'average_Tdiv' , markersize = 8)
            
                ax3.plot(shotfile.D_tot.time, shotfile.D_tot.data, 'k', label= 'Dtot')
                ax3.plot(shotfile.N_tot.time, shotfile.N_tot.data, 'r', label= 'Ntot')

                plotting(ax1, ax2, ax3, t_ini, t_end)
                
            k +=1
            
        except:

            print 'error at shot: '+ str(shot )
            continue

    #plt.show()


    green = Colors(cm.Greens, 'Discharges [34800, 34880]')
    blue  = Colors(cm.Blues,  'Discharges [34920, 35100]')
    red   = Colors(cm.Reds,   'Discharges [35120, 35190]')
    grey  = Colors(cm.Greys,  'Discharges [35191, 35230]')

    for key in shotfiles_dict:
        try:
            if (shotfile.spec is 'FVS' and int(key) >=  34718) or shotfile.spec is 'EVS':

                if int(key) in range(34800, 34880):
                    print 'color verd'

                    green.vel.append(shotfiles_dict[key][4])
                    green.x_err.append(shotfiles_dict[key][3])
                    green.y_err.append(shotfiles_dict[key][5])
                    green.colors.append(shotfiles_dict[key][6])
                    green.labels.append(str(key))
                    green.T_div.append(shotfiles_dict[key][2])
                    print 'color verd'

                elif int(key) in range(34920, 35100):
                    print 'color blau'
                    

                    blue.vel.append(shotfiles_dict[key][4])
                    blue.x_err.append(shotfiles_dict[key][3])
                    blue.y_err.append(shotfiles_dict[key][5])
                    blue.colors.append(shotfiles_dict[key][6])
                    blue.labels.append(str(key))
                    blue.T_div.append(shotfiles_dict[key][2])
                    print 'color blau'

                elif int(key) in range(35120, 35190):
                    print 'color vermell'
                    
                    
                    red.vel.append(shotfiles_dict[key][4])
                    red.x_err.append(shotfiles_dict[key][3])
                    red.y_err.append(shotfiles_dict[key][5])
                    red.colors.append(shotfiles_dict[key][6])
                    red.labels.append(str(key))
                    red.T_div.append(shotfiles_dict[key][2])
                    print 'color vermell'

                elif int(key) in range(35191, 35230):
                    print 'color gris'
                   
   
                    grey.vel.append(shotfiles_dict[key][4])
                    grey.x_err.append(shotfiles_dict[key][3])
                    grey.y_err.append(shotfiles_dict[key][5])
                    grey.colors.append(shotfiles_dict[key][6])
                    grey.labels.append(str(key))
                    grey.T_div.append(shotfiles_dict[key][2])
                    print 'color gris'
                   
            else:
                print 'error'
                continue
        except:
            continue
    print green.T_div
    green.plot2(green.T_div, green.vel, green.x_err,green.y_err, green.colors, green.labels, shotfile.spec, shotfile.los)
    blue.plot2(blue.T_div, blue.vel, blue.x_err, blue.y_err, blue.colors, blue.labels, shotfile.spec, shotfile.los)
    red.plot2(red.T_div, red.vel, red.x_err,red.y_err, red.colors, red.labels, shotfile.spec, shotfile.los)
    grey.plot2(grey.T_div, grey.vel, grey.x_err, grey.y_err, grey.colors, grey.labels, shotfile.spec, shotfile.los)
    
    plt.show()

'''
    T_div = []
    vel = []
    x_err = []
    y_err = []
    colors = []
    labels = []
    
    for key in shotfiles_dict:
        try:
            if (shotfile.spec is 'FVS' and int(key) >=  34718) or shotfile.spec is 'EVS':
                
                vel.append(shotfiles_dict[key][4])
                x_err.append(shotfiles_dict[key][3])
                y_err.append(shotfiles_dict[key][5])
                colors.append(shotfiles_dict[key][6])
                labels.append(str(key))
                T_div.append(shotfiles_dict[key][2])

            else:
                continue
        except:
            continue

    
    col = Colors()
    col.plot(T_div, vel, x_err, y_err, colors, labels, shotfile.spec, shotfile.los)
    
'''

if __name__ == '__main__':
    main()

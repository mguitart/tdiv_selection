'''
Program to calculate the velocity for specific shotfiles

'''

import numpy as np
import matplotlib.pylab as plt
import matplotlib
import sys
sys.path.append('/afs/ipp/u/mcavedon/repository/python/')
from ddPlus import XVS
import dd
from auxiliar import rebin, plotting
from auxiliar import TDiv
from utils import Utils
from Gaussian import lmfit_gauss_single
from lmfit import  Parameters, minimize, fit_report


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
    
def floatRgb(mag, cmin, cmax):
    """ Return a tuple of floats between 0 and 1 for R, G, and B. """
    # Normalize to 0-1
    try: x = float(mag-cmin)/(cmax-cmin)
    except ZeroDivisionError: x = 0.5 # cmax == cmin
    blue  = min((max((4*(0.75-x), 0.)), 1.))
    red   = min((max((4*(x-0.25), 0.)), 1.))
    green = min((max((4*math.fabs(x-0.5)-1., 0.)), 1.))
    return red, green, blue

#####################################main#####################################################

def main():
    

    shotfiles_dict = {'34684':[7,8] , '34267':[5,6] , '34266':[7,8] , '34467':[5,6] , '34684':[4,5] , '34273':[3,4] , '34281':[2.5, 3.5] , '34467':[5,6] , '34278':[5,6] , '34865':[3,4] , '34443':[4,5] , '34280':[5,6] , '34281':[2.5, 3.5] , '34278':[5,6] , '34865':[3,4] , '34443':[4,5] , '34536':[2.5, 3.5] , '34445':[2.8, 3.8] , '34535':[1.8, 2.6] , '34386':[3,4], '34165':[4,5] ,  '34532':[6,7] , '34178':[5,6] , '34267':[5,6] , '34264':[2.5, 3.5] ,'34358':[2.5 , 3.5] , '34279':[4,5]  ,  '34980':[5.5, 6.5] , '34177':[3,4]  , '34385':[3.5, 4.5] , '34382':[2.5, 3.5] , '34382':[2.5, 3.5] , '34642':[4,5] , '34829':[5, 5.85] , '34277':[2.5 , 3.5], '34275':[2.8 , 3.5] , '34265': [4.5 , 5.5] , '34980':[5.5 , 6.5] , '34359':[2.5 , 3.5] , '34164':[2,3] , '34179':[4 , 4.8], '34441':[2.7 , 3.5], '34981':[2.8, 3.8], '34639':[3.3 , 3.7] , '34189':[5.6 , 6.58] , '34492':[4,5], '34536':[2.5, 3.5], '34654':[2.14, 3.14], '34647':[2.2, 2.95], '34381':[4,5], '34979':[5, 5.8], '34379':[2.5, 3.0] }

    lambda_0 =  399.4997
    c = 299792458 #m/s
    k =1

    for shot in shotfiles_dict:

        try:
            t_ini = shotfiles_dict[shot][0]
            t_end = shotfiles_dict[shot][1]
            x_position = float((float(t_ini) + float(t_end))/2)
            
            shotfile = TDiv(int(shot), t_ini, t_end) #creates the object and creates avg_Tdiv & err_y
            shotfiles_dict[shot].append(shotfile.avg_Tdiv)
            shotfiles_dict[shot].append(shotfile.err_y)
            '''
            #checking the goodness of the fit
            f, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize = (15,15))
            
            uncert = abs((shotfile.err_y) /  (shotfile.avg_Tdiv)*100)
            uncert = str(round(uncert,1))              #save only two decimals from uncert
            str_Tdiv = str(round(shotfile.avg_Tdiv,1)) #save only two decimals from Tdiv
            f.suptitle('Shotfile ' + shot + '\n' + ' Avg_Tdiv = '+ str_Tdiv  + " w/ uncertainty: " + str(uncert) + '%', size = 30)
            '''
            #spectra 2 for no plotting
    
            #shotfile.spectra(int(shotfile.shotfile),     0,     8, ax1, 'r', '' ,'-', 'averaged_spectra')         
            shotfile.spectra2(int(shotfile.shotfile),     0,     8)   
            #shotfile.spectra(int(shotfile.shotfile), t_ini, t_end, ax1, 'b', 'o','' , 'window_averaged_spectra')  
            shotfile.spectra2(int(shotfile.shotfile), t_ini, t_end)
            print shotfile.data.wlen

            averaged_data = np.zeros(shape = (1, shotfile.data.nch, 512))
            averaged_data[0,:,:] =  shotfile.data.intensity.data.mean(axis=0)
            popt_lmfit = lmfit_fit_single(shotfile.data.wavel, averaged_data, shotfile.jlos, 398.5, 399.75, 0) 

            shift = popt_lmfit.params['b_0'].value
            vel = shift*c/(lambda_0*1000)
            shotfiles_dict[shot].append(vel)
            shotfiles_dict[shot].append(popt_lmfit.params['b_0'].stderr*c/(lambda_0*1000))
            shotfiles_dict[shot].append(popt_lmfit.params['a_0'].value)


            '''
            #for plotting, uncomment 
            xx = np.linspace(398.5 , 399.75,  1000)
            ax1.plot(xx,lmfit_gauss_single(popt_lmfit.params, xx), color= 'g' , ls= '-', label = 'fitting of N1 peak')
  
            Tdiv_binned, time = shotfile.Tdiv_rebin()
            ax2.plot(shotfile.Tdiv.time, shotfile.Tdiv.data, 'b', label = 'Tdiv')
            ax2.plot(time,Tdiv_binned, 'r', label = 'binned_Tdiv')
            ax2.errorbar(x_position, shotfile.avg_Tdiv, yerr= shotfile.err_y, color = 'g', ecolor='k',elinewidth = 2,  fmt =  'o', label = 'average_Tdiv' , markersize = 8)
            
            ax3.plot(shotfile.D_tot.time, shotfile.D_tot.data, 'k', label= 'Dtot')
            ax3.plot(shotfile.N_tot.time, shotfile.N_tot.data, 'r', label= 'Ntot')

            plotting(ax1, ax2, ax3, t_ini, t_end) #calls functions with all detaisl for plotting
            
            k +=1
            '''
        except:
            print 'error at shot: '+ str(shot )
            #print shotfile.data.wlen
            continue

    #plt.show()

    cmin = min()
    cmax
    #colors = plt.cm.jet(np.linspace(0,1,k))
    #j = 0
    fig, ax = plt.subplots(figsize=(10,10))
    for key in shotfiles_dict:
        try:
        
            T_div = shotfiles_dict[key][2]
            vel = shotfiles_dict[key][4]
            x_err = shotfiles_dict[key][3]
            y_err = shotfiles_dict[key][5]
            col = shotfiles_dict[key][6]
            #cmap = matplotlib.cm.get_cmap('viridis')
            #normalize = matplotlib.colors.Normalize(vmin=min(z), vmax=max(z))
            #colors = [cmap(normalize(value)) for value in col]
            cmap = matplotlib.cm.get_cmap('viridis')
            normalize = matplotlib.colors.Normalize(vmin=min(col), vmax=max(col))
            colors = [cmap(normalize(value)) for value in col]


            ax.errorbar(T_div,  vel, xerr=x_err , yerr= y_err,    color = col , norm = normalize,  cmap= cmap, fmt='o')
           #j += 1

        except:
            continue
    #plt.legend()
    #plt.title(str(shotfile.))
    cax, _ = matplotlib.colorbar.make_axes(ax)
    cbar = matplotlib.colorbar.ColorbarBase(cax, cmap=cmap, norm=normalize)
    #cbar = plt.colorbar()
    #cbar.set_label('Nitrogen intensity')
 
    plt.axvline(x=0.0, color='k', linestyle='-')
    plt.axhline(y=0.0, color='k', linestyle='-')
    plt.xlabel('Divertor Temperature [eV]')
    plt.ylabel('Velocity [km/s]')
    plt.show()

if __name__ == '__main__':
    main()

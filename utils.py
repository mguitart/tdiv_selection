import numpy as np
import matplotlib.pylab as plt
from netCDF4 import Dataset
import dd


#function
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


#class
class Utils:

  def __init__(self):
    self.rootgrp = None
    self.calibrated_data = None
    self.binned_data = None
    self.spec = ""
    self.channels = []
    self.time = None
    self.idl_data = None
    self.idl_binned_data = None
    self.idl_time = None
    self.avg = None
    self.text = "" 

  def get_data(self, shotfile, spectrometer):
      self.spec = spectrometer
      self.text = spectrometer+"\n"
      rootgrp = Dataset("/afs/ipp-garching.mpg.de/home/m/mguitart/Master_Thesis/pub/"+ str(shotfile)+ "_"+str(spectrometer),"r")
      dt = np.diff(rootgrp.variables['time'][:]).mean()
      dwdp = np.gradient(rootgrp.variables['lambda'])[1]
      calibrated_data = np.zeros_like(rootgrp.variables['spectra'][:])
      for jt in xrange(rootgrp.variables['spectra'][:].shape[1]):
          calibrated_data[:,jt,:] = rootgrp.variables['spectra'][:,jt,:]/\
              rootgrp.variables['sens'][:]/dt/dwdp
      calibrated_data = np.ma.filled(calibrated_data)
      self.rootgrp = rootgrp
      self.calibrated_data = calibrated_data
      return calibrated_data


  def idl_get_data(self, spectr, shotfile, ed):

      sf = dd.shotfile(spectr, shotfile, experiment = 'SPRD', edition= ed)
      IDL_N1 = sf('SN_13995') 
      self.idl_data = IDL_N1
      
      #bin the IDL fitting data


  #in the future I can make the bin size as a variable
  def rebin(self, calibrated_data):
    	
      binned_data = np.zeros_like(calibrated_data)
      binned_data.resize((25,250,512))
      time = np.zeros_like(self.rootgrp.variables['time'][:])
      time.resize(250)

      for i in range(0,len(self.rootgrp.variables['lambda'][:,3])): #all channels
          for j in range(0, len(self.rootgrp.variables['lambda'][i,:])): #all pixels
              rb = rebin(self.rootgrp.variables['time'][:], calibrated_data[i,:,j])
              time = rb[0]
              for t in range(0, len(rb[0])):
                  binned_data[i,t,j]= rb[1][t]
      self.binned_data = binned_data
      self.time = time
      return binned_data


  def idl_rebin(self):
      binned_data = np.zeros_like(self.idl_data.data)
      binned_data.resize((50,24))
      time = np.zeros_like(self.idl_data.time)
      time.resize(50)

      for i in range(0,len(self.idl_data.data[3,:])): #all channels (0 --> 24)
          rb = rebin(self.idl_data.time[:], self.idl_data.data[:,i])
          time = rb[0]
          for t in range(0, len(rb[0])):
              binned_data[t,i]= rb[1][t]

      self.idl_binned_data = binned_data
      self.idl_time = time


  def average(self, shotfile, t_ini, t_end):

      aux_time = self.rootgrp.variables['time'][:]
 
      indexTime =  np.arange(self.calibrated_data[0,:,:].shape[0])\
        [(np.array(aux_time) > t_ini) & (np.array(aux_time) < t_end )]

      a = len(indexTime)
      n_ch = len(self.rootgrp.variables['lambda'][:,3])

      aux_matrix = np.zeros(shape = (n_ch, a, 512))
      avg        = np.zeros(shape = (n_ch, 1, 512))

      for i in range(0, len(self.rootgrp.variables['lambda'][:,3])): #all channels

          for j in range(0, len(self.rootgrp.variables['lambda'][3, :])): #all pixels
              k = 0
              for t in indexTime: #desired time window
                  aux_matrix[i, k, j]+= self.calibrated_data[i, t, j]
                  k +=1
              
      avg[:, 0, :]=aux_matrix[:, :, :].mean(axis=1)

      self.avg = avg


  def plot_rawData(self):
      for i in self.channels:
          plt.plot(self.rootgrp.variables['lambda'][i,:],\
                       self.binned_data[i,:,:].mean(axis=0), label ='channel_'+str(i)+': '+str(self.rootgrp.variables['losnam'][i]))
      plt.legend()
      plt.show()
    


  def setChannels(self, channels):
    self.channels = channels

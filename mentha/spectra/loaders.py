# I write the loader 
#what loader should know and do 
# it should go to the file pull out the data to do the spectrum 
#and it should present the spectrum what we call the function 
import numpy as np
from mentha.spectra.spectrum import Spectrum

def load_spectrum(path, cell_id):
    # load the data from the file 
    data= np.loadtxt(path)

    return Spectrum(
       frequency_hz= data[:,0],
        z_real_ohm= data[:,1], 
        z_imag_ohm= data[:,2],
        cell_id= cell_id
    )

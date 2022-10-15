#!/usr/bin/env python
# coding: utf-8

# # Compressor Simulation
# ---

# To select a suitable compressor for a vapor compression machine, compressor manufacturers offer selection software. This selection software presents to the user one or more compressor models based on the user's input, such as the kind of refrigerant, the required cooling or heating capacity at design conditions, the evaporation and condensation temperature aimed at under design conditions, the target degree of superheat at the evaporator exit and along the suction line, the target degree of subcooling at the condenser exit. The selection program also presents through tables and diagrams the compressor performance under a variety of working conditions, which are mainly characterized by evaporation and condensation temperature, whereby the degree of superheat and subcooling remain fixed. In addition to tables and diagrams most selection programs these days also offer extensive sets of coefficients that can be used in polynomial equations that mathematically describe the compressor performance characteristics, such as mass flow rate, cooling capacity, compressor power, etc. in function of evaporation and condensing temperature, and, in the case of variable speed compressors, also in function of compressor speed. With these polynomials it is possible to simulate the performance of a given compressor under varying working conditions.

# The polynomial coefficients can be exported from the selection program to a spreadsheet or comma-separated-values (csv) file. For each performance parameter a different set of coefficients is valid. Two classes have been written to model a real compressor based on the equations offered by compressor manufacturers. One class applies to compressors with fixed speed, while the other class applies to compressors with a variable speed drive. The variables in the equations of a fixed speed compressor are evaporation and condensation temperature only. The equations of a variable speed compressor also count compressor speed as a third variable. A fixed speed compressor is modeled using the class `FixedSpeedCompressor` and a variable speed compressor is modeled by the class `VariableSpeedCompressor`. Both classes reside in the package `hvac.vapor_compression`.

# In[1]:


from deps import load_packages
load_packages()

import warnings
warnings.filterwarnings('ignore', category=UserWarning)

from hvac.fluids import fluid_logger
import logging
fluid_logger.setLevel(logging.ERROR)

# %matplotlib widget


# In[2]:


from pathlib import Path
import pandas as pd

from hvac import Quantity
from hvac.fluids import Fluid, fluid_logger
from hvac.vapor_compression import FixedSpeedCompressor, VariableSpeedCompressor
from hvac.charts.log_ph_diagram import StandardVaporCompressionCycle, LogPhDiagram


# In[3]:


Q_ = Quantity


# In order to use these two classes, the coefficients of all performance parameters must be collected in a file that these classes can recognize. Therefore, the coefficients must be ordered in a table-like structure stored on disk with the csv file extension (\*.csv). Examples of such files can be found in the folder *compressor_data* under the project's main folder. The code block below will open a csv-file with the coefficients of one of the available compressor models and it will print the table on screen:

# In[4]:


data_folder = Path("../compressor_data")
file = data_folder / "DSF175-4.csv"
table = pd.read_csv(file)

with pd.option_context('display.max_columns', None, 'display.width', 300):
    print(table)


# The coefficients of four performance parameters are given in the file:
# - the cooling capacity, denoted by `Qc_dot`
# - the mechanical compressor power, denoted by `Wc_dot`
# - the drawn compressor current, denoted by `I`
# - the mass flow rate of refrigerant, denoted by `m_dot`
# 
# A fifth parameter is alo possible, wich is the discharge temperature at the compressor outlet, denoted by `T_dis`.
# 
# It is very important that these exact notations will be used, otherwise the program won't understand and give you trouble.
# 
# The polynomials describing each of the performance parameters in the example count 10 coefficients (C0...C9), which is the case for a fixed speed compressor. In case of a variable speed compressor the number of coefficients may be 20 (C0...C19) or 30 (C0...C29).

# ## Example of a Fixed Speed Compressor

# A fixed speed compressor is modelled by an instance of class `FixedSpeedCompressor`. To instantiate this class, we need to specify the path of the csv-file, the degree of superheat and the degree of subcooling for which the polynomial coefficients are valid, and also the type of refrigerant:

# In[5]:


fixed_speed_compressor = FixedSpeedCompressor(
    coeff_file=data_folder / "ZR144KCE-TFD.csv",
    dT_sh=Q_(10, 'K'),  # degree of superheat
    dT_sc=Q_(0, 'K'),  # degree of subcooling
    refrigerant_type=Fluid('R22')
)


# > **Note**<br>
# > It might be necessary that before instantiation the default units inside the `FixedSpeedCompressor` class have to be adapted to the units that were used by the compressor manufacturer to express the magnitude of the performance quantities, as the units also have an impact on the values of the coefficients.<br> 
# > The dictionary `units` of class `FixedSpeedCompressor` has the following keys: 
# > - `'Qc_dot'` for cooling capacity - default unit `'kW'`
# > - `'Wc_dot'` for compressor power - default unit `'kW'`
# > - `'m_dot'` for mass flow rate - default unit `'g/s'`
# > - `'speed'` for compressor speed - default unit `'1/min'`.
# >
# > To change the units in the `FixedSpeedCompressor` class, you would write for example for mass flow rate:
# > ```
# > FixedSpeedCompressor.units['m_dot'] = 'kg / hr'
# > ```

# After instantiation of the class, we need to set the working conditions of the compressor. Working conditions are determined by evaporation and condensation temperature:

# In[6]:


fixed_speed_compressor.Te = Q_(5.0, 'degC')   # evaporator temperature
fixed_speed_compressor.Tc = Q_(50, 'degC')    # condenser temperature


# Now we can retrieve the performance parameters of the compressor under the given working conditions:
# - cooling capacity `Qc_dot`
# - mass flow rate `m_dot`
# - compressor power `Wc_dot`
# - isentropic efficiency `eta_is`
# - heating capacity (or heat rejection rate) `Qh_dot`
# - coefficient of performance `COP`

# In[7]:


print(
    f"Qc_dot = {fixed_speed_compressor.Qc_dot.to('kW'):~P.2f}\n"
    f"Wc_dot = {fixed_speed_compressor.Wc_dot.to('kW'):~P.2f}\n"
    f"eta_is = {fixed_speed_compressor.eta_is.to('pct'):~P.2f}\n"
    f"m_dot = {fixed_speed_compressor.m_dot.to('g/s'):~P.2f}\n"
    f"Qh_dot = {fixed_speed_compressor.Qh_dot.to('kW'):~P.2f}\n"
    f"COP = {fixed_speed_compressor.COP.to('frac'):~P.2f}"
)


# Also the refrigerant states at the evaporator and condenser in- and outlet can be retrieved from the compressor model based on a standard vapor compression cycle (i.e. an idealized cycle whereby any pressure loss in the evaporator, the condenser, the liquid line, the suction line, or the discharge line is ignored).

# In[8]:


with pd.option_context('display.max_columns', None, 'display.width', 300):
    print(fixed_speed_compressor.get_refrigerant_cycle())


# You can alter the units of the state properties in the table. For this you need to call `get_refrigeration_cycle` with a dictionary which must have following keys along with the corresponding desired unit: `'T'` for temperature, `'P'` for pressure, `'rho'` for mass density, `'h'` for enthalpy, and `'s'` for entropy. Note that it is not possible to change the unit of only one or a few state properties; you need to pass a complete dictionary with all the keys.

# **Log\(P\)-h Diagram**

# We can now draw the log\(P\)-h diagram of the vapor compression cycle at the working conditions we specified earlier (see also the chapter on log\(P\)-h diagrams).

# In[9]:


vc_cycle = StandardVaporCompressionCycle(
    Refrigerant=fixed_speed_compressor.refrigerant_type,
    evaporationTemperature=fixed_speed_compressor.Te,
    condensationTemperature=fixed_speed_compressor.Tc,
    evaporatorSuperheat=fixed_speed_compressor.dT_sh,
    subCooling=fixed_speed_compressor.dT_sc,
    suctionLineSuperheat=None,
    isentropicEfficiency=fixed_speed_compressor.eta_is
)

log_ph_diagram = LogPhDiagram(fixed_speed_compressor.refrigerant_type, size=(8, 6), dpi=96)
log_ph_diagram.setCycle(vc_cycle)
log_ph_diagram.show()


# ## Example of a Variable Speed Compressor

# The procedure for a variable speed compressor is more or less identical to the one for the fixed speed compressor. Let's demonstrate with an example: We have a compressor working with refrigerant R454B. This refrigerant -a mixture of 68.9 w-% R32 and 31.1 w-% R1234yf- is not available in CoolProp, but we can define the mixture as explained in the chapter on refrigerants. The polynomial coefficients from the compressor manufacturer expect that speed will be expressed in units of revs per second (1/s) and refrigerant mass flow rate in units of kilogram per hour (kg/hr). The coefficients were taken from the selection software at a superheat degree of 10 K and a subcooling degree of 5 K.

# In[10]:


VariableSpeedCompressor.units['speed'] = '1 / s'
VariableSpeedCompressor.units['m_dot'] = 'kg / hr'


# In[11]:


variable_speed_compressor = VariableSpeedCompressor(
    coeff_file=data_folder / "VZH088CGM.csv",
    dT_sh=Q_(10, 'K'),
    dT_sc=Q_(5, 'K'),
    refrigerant_type=Fluid('R32&R1234yf', mass_fractions=[Q_(0.689, 'frac'), Q_(0.311, 'frac')])
)


# The compressor's documentation states that the frequency range of the variable speed drive is from 25 Hz to 100 Hz, which corresponds with a speed range of 1500 to 6000 revs/min. The compressor was selected with an evaporation temperature of -7 °C and a condensation temperature of 35 °C. The required heating capacity at these design conditions are met at a compressor speed of 5618 revs/min. Let's get the performance data at these conditions:

# In[12]:


variable_speed_compressor.Te = Q_(-7, 'degC')
variable_speed_compressor.Tc = Q_(35, 'degC')
variable_speed_compressor.speed = Q_(5618, '1/min')


# In[13]:


print(
    f"Qc_dot = {variable_speed_compressor.Qc_dot.to('kW'):~P.2f}\n"
    f"Wc_dot = {variable_speed_compressor.Wc_dot.to('kW'):~P.2f}\n"
    f"eta_is = {variable_speed_compressor.eta_is.to('pct'):~P.2f}\n"
    f"m_dot = {variable_speed_compressor.m_dot.to('g/s'):~P.2f}\n"
    f"Qh_dot = {variable_speed_compressor.Qh_dot.to('kW'):~P.2f}\n"
    f"COP = {variable_speed_compressor.COP.to('frac'):~P.2f}"
)


# As with the `FixedSpeedCompressor` class, the magnitude of the state properties at the 4 corner points of the cycle can be requested:

# In[14]:


with pd.option_context('display.max_columns', None, 'display.width', 300):
    print(variable_speed_compressor.get_refrigerant_cycle())


# > **Note**<br>
# > Although the evaporation temperature was set -7 °C, it can be noticed that according to CoolProp's calculations the refrigerant temperature at the evaporator inlet is around -8 °C. The evaporation pressure is determined by the internal program code of class `VariableSpeedCompressor` at the given evaporation temperature (-7 °C) and for saturated vapor ($x$ = 100 %). The enthalpy of the refrigerant at the evaporator inlet (a mixture of saturated liquid and vapor) equals the enthalpy of the subcooled liquid refrigerant at the condenser outlet, since the pressure reduction at the expansion valve is considered to be an isenthalpic process. Based on the evaporation pressure and the enthalpy, the refrigerant temperature at the evaporator inlet is then calculated by CoolProp to be around -8 °C, instead of -7 °C.

# **Log\(P\)-h Diagram**

# For refrigerant mixtures drawing a log\(P\)-h diagram throws an exception from inside CoolProp's internal code (version 6.4.1). At the time of writing this notebook, no solution was found to overcome this error.

# **Minimum and Maximum Cooling Capacity at given Evaporation and Condensation Temperature**

# In[15]:


variable_speed_compressor.speed = Q_(1500, '1 / min')
print(f"cooling capacity at minimum speed: {variable_speed_compressor.Qc_dot.to('kW'):~P.2f}")


# In[16]:


variable_speed_compressor.speed = Q_(6000, '1 / min')
print(f"cooling capacity at minimum speed: {variable_speed_compressor.Qc_dot.to('kW'):~P.2f}")


# **Find the Compressor Speed to Realize a given Cooling Capacity at given Evaporation and Condensation Temperature**

# In[17]:


Qc_dot = Q_(10.0, 'kW')
rpm = variable_speed_compressor.get_compressor_speed(Qc_dot)
print(f"cooling capacity {Qc_dot:~P.2f} @ {rpm.to('1 / min'):~P.1f}")


# In[ ]:





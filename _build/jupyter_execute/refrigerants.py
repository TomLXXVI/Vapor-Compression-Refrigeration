#!/usr/bin/env python
# coding: utf-8

# # Using Refrigerants
# ---

# The `Fluid` class, contained inside the package `hvac.fluids`, provides a thin wrapper around the third-party library **[CoolProp](http://www.coolprop.org/)**, which gives you access to thermodynamic properties of many fluids. The list of available fluids can be found in CoolProp's documentation. The `Fluid` class has also been developed to allow direct use of physical quantities. The use of physical quantities is based on another third-party package **[Pint](https://pint.readthedocs.io/en/stable/)**. To use physical quantities in a notebook or script we need to import the `Quantity` class from the main package `hvac`.

# In[1]:


from deps import load_packages

load_packages()

from hvac.fluids import fluid_logger
import logging
fluid_logger.setLevel(logging.ERROR)


# In[2]:


from hvac import Quantity
from hvac.fluids import Fluid


# As a shortcut we also define an alias for `Quantity`:

# In[3]:


Q_ = Quantity


# In this notebook it will be demonstrated how to use the `Fluid` class to define a specific refrigerant, how to set the state of this refrigerant, and how to get the quantity of other state properties after the state of the refrigerant has been determined.

# As an example, the refrigerant R134A will be defined. To do that, we need to create an instance of the `Fluid` class with the name of the refrigerant as known by CoolProp inside a string:

# In[4]:


R134A = Fluid('R134A')


# That is what is minimal required in order to define a specific fluid. 
# 
# CoolProp has a number of backends that can be used to determine the thermodynamic properties of a fluid. The default backend is `HEOS`. You can check CoolProp's documentation about the other backends, but mostly `HEOS` will suffice.
# 
# Not all existing fluids are available in CoolProp. However, it is possible to create a mixture of fluids that are known by CoolProp. To specify a mixture the name of its constituents are written side by side separated by an ampersand (&). In addition to the names of the constituents, the mass fraction of each of the constituents needs to be passed to the `Fluid` constructor. This is done with a `list` in which the order of the mass fractions must correspond with the order of the constituent names in the specification of the mixture. An example of a mixture will follow later on in this notebook.
# 
# Enthalpy and entropy are relative properties. Their magnitude is measured relative to a certain reference state. A number of reference states have been defined in international standards. CoolProp knows about the following standards: `NBP` (Normal Boiling Point), `ASHRAE` (the ASHRAE standard reference), or `IIR` (the standard reference of the International Institute of Refrigeration). The default value for the reference state is set to `DEF`, which means that CoolProp will use the default reference state for the fluid.

# Now that we have defined our refrigerant R134A, we can specify its state by giving two of its state properties. The following state properties are defined within the `Fluid` class:
# 
# | **property** | **keyword** |
# | ------------ | ----------- |
# | temperature | `T` |
# | pressure | `P` |
# | mass density | `rho` |
# | specific enthalpy | `h` |
# | specific entropy | `s` |
# | specific heat at constant pressure | `cp` |
# | specific heat at constant volume | `cv` |
# | vapor quality | `x` |
# | thermal conductivity | `k` |
# | dynamic viscosity | `mu` |

# Let's consider refrigerant R134A at a temperature of 0°C while it is a saturated liquid, meaning that the vapor quality is zero. To set this state, we write:

# In[5]:


R134A_sl = R134A(T=Q_(0, 'degC'), x=Q_(0, 'frac'))


# The vapor quality `x` is expressed as a fraction. We could equally well express it as a percentage ('pct').

# Now that the state of the refrigerant has been specified, we can for example get the mass density and specific enthalpy at this state by writing:

# In[6]:


print(
    f"mass density = {R134A_sl.rho}\n"
    f"enthalpy = {R134A_sl.h}"
)


# We can easily convert between units. Frequently enthalpy will be expressed in units of kJ/kg rather than J/kg. We can also format how quantities will be displayed. To demonstrate, let us express enthalpy in units of kJ/kg and rounded to 3 digits behind the decimal point:

# In[7]:


print(f"enthalpy: {R134A_sl.h.to('kJ/kg'):~P.3f}")


# The format specifier `~P` comes from Pint. It indicates that units have to be displayed in their prettyfied, abbreviated notation. The format specifier `.3f`, which is standard Python, denotes that the value has to be displayed as a ordinary decimal number rounded to 3 decimal digits.

# ## Mixture of Refrigerants

# As already mentioned above, not all fluids are known by CoolProp. One example is refrigerant R454B. It is a blend of 68.9 w-% R32 and 31.1 w-% R1234yf. Both of these constituents are known by CoolProp. Then to define refrigerant R454B we need to write:

# In[8]:


R454B = Fluid('R32&R1234yf', mass_fractions=[Q_(68.9, 'pct'), Q_(31.1, 'pct')])


# When specifying the state of a refrigerant mixture, there is however a restriction on the kind of state properties that can be set. Only the following three combinations can be used with CoolProp:
# - pressure `P` and quality `x`
# - temperature `T` and quality `x`
# - pressure `P` and temperature `T`

# Therefore, a small workaround has been implemented inside class `Fluid` that allows to get the refrigerant's state for other, however not all possible combinations. One of the state properties must be pressure, temperature, or quality. The second state property can be any valid state property. Furthermore, we must also guess a value for a third state property, which must be pressure, temperature, or quality again, but of course, cannot be the same 
# as for the first property. Through iteration the value of the third state property will be searched for, such that the value given to the second state property is fulfilled. An example will clarify how it works: Assume that at the condenser outlet the pressure of the subcooled liquid refrigerant equals 25.71 bar and its temperature is 35 °C. The evaporation temperature is given as -10 °C. We are asked to find the refrigerant's vapor quality at the inlet of the evaporator.

# In[9]:


condenser_out = R454B(P=Q_(25.71, 'bar'), T=Q_(35.0, 'degC'))

# evaporator_in = R454B(T=Q_(-10, 'degC'), h=condenser_out.h) --> this would raise an exception

evaporator_in = R454B(T=Q_(-10, 'degC'), h=condenser_out.h, x=Q_(0, 'frac'))

print(evaporator_in.x.to('pct'))


# In[ ]:





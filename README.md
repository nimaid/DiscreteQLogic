# DiscreteQLogic
My resources and projects relating to digital circuits made out of discrete transistors.

## Efficient Discrete NMOS Logic Gate Designs
I have yet to find a well-compiled source that lists the most efficient NMOS implementations using discrete MOSFETS and resistors. This is likely because, well, it's a very slow and outdated technology that draws more power than CMOS.

However, for DIY projects where one wishes to do the bare minimum of soldering, layout, and purchasing, NMOS provides very good functionality at about half the transistor count of CMOS (at the expense of adding some resistors). Therefore, I have decided to use NMOS for my DIY projects, and as such, I have been collecting the most efficient gate designs, which use fewest transistors and resistors possible.

*(I have been making a library of these parts for both Digital and LTspice, in order to simulate them before building them. You can find these libraries in their respective subfolders of this repository.)*

For this list, I will use some shorthand notation to refer to the total transistor and resistor counts for each part. This shorthand will follow the format `xQyR`, where `x` is the total transistor count and `y` is the total resistor count. So, for example, a XOR gate which was labeled `6Q3R` would require 6 transistors and 3 resistors to build.

Unless otherwise stated, all transistors are N-type.

Resistor values should be chosen based on acceptable power dissipation and speed requirements. If the resistors are large (on the order of 10kΩ+), then power dissipation will be very low (the resistor lets less current through to ground), but the response time of the gate will be slower (it takes longer to charge up the stray capacitance in the wires). Conversely, smaller values will yield higher power usage, but faster response times.

### NOT (1Q1R)
The simplest gate to construct is a NOT gate (also known as an inverter). This is simply a pullup resistor with a transistor configured to short the output to ground when voltage is applied to it's gate. Make sure you understand how this gate works, because this fundamental principal is the foundation which allows the systematic construction of every other NMOS gate.

<img src="https://github.com/nimaid/DiscreteQLogic/raw/main/Images/Circuits/nm_not.PNG" width="400px" />

### NAND (2Q1R)
The next step up in complexity is the NAND gate. This is essentially just a NOT gate with an extra transistor in series to ground. This has the effect of only shorting the output to ground if *both* transistors are conducting. This results in the behavior of a NAND gate.

<img src="https://github.com/nimaid/DiscreteQLogic/raw/main/Images/Circuits/nm_nand.PNG" width="400px" />

### NOR (2Q1R)
The NOR gate is almost exactly the same as the NAND gate, except the second transistor is connected in parallel as opposed to series. This has the effect of shorting the output to ground if *either* transistors are conducting. This results in the behavior of a NOR gate.

<img src="https://github.com/nimaid/DiscreteQLogic/raw/main/Images/Circuits/nm_nor.PNG" width="400px" />

### n-way NAND and NOR (nQ1R)
It is possible to efficiently make NAND and NOR gates that have more than 2 inputs without chaining together the above units. While this method uses the same number of transistors as chaining the 2-way gates, but it does use significantly fewer resistors. We do this be applying the same logic that took us from a NOT gate to 2-way NAND and NOR gates, but instead of putting only 2 transistors in either series or parallel, we put n tranistors, where n is the number of inputs we want.

Here is an example of 8-way NAND and NOR gates, respectively.

<img src="https://github.com/nimaid/DiscreteQLogic/raw/main/Images/Circuits/nm_nand8.PNG" height="400px" />
<img src="https://github.com/nimaid/DiscreteQLogic/raw/main/Images/Circuits/nm_nor8.PNG" width="400px" />

### AND and OR
The best way to made AND and OR gates happens to be the most straightforward. All we have to do is add a NOT gate after the NAND and NOR gates, as shown.

<img src="https://github.com/nimaid/DiscreteQLogic/raw/main/Images/Circuits/nm_and.PNG" width="400px" />
<img src="https://github.com/nimaid/DiscreteQLogic/raw/main/Images/Circuits/nm_or.PNG" width="400px" />

### WIP
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

### n-way NAND and NOR (\{n\}Q1R)
It is possible to efficiently make NAND and NOR gates that have more than 2 inputs without chaining together the above units. While this method uses the same number of transistors as chaining the 2-way gates, but it does use significantly fewer resistors. We do this be applying the same logic that took us from a NOT gate to 2-way NAND and NOR gates, but instead of putting only 2 transistors in either series or parallel, we put `n` transistors, where `n` is the number of inputs we want.

Here is an example of 8-way NAND and NOR gates, respectively.

<img src="https://github.com/nimaid/DiscreteQLogic/raw/main/Images/Circuits/nm_nand8.PNG" height="400px" />
<img src="https://github.com/nimaid/DiscreteQLogic/raw/main/Images/Circuits/nm_nor8.PNG" width="400px" />

### AND and OR (3Q2R)
The best way to make AND and OR gates happens to be the most straightforward. All we have to do is add a NOT gate after the NAND and NOR gates, as shown.

<img src="https://github.com/nimaid/DiscreteQLogic/raw/main/Images/Circuits/nm_and.PNG" width="400px" />
<img src="https://github.com/nimaid/DiscreteQLogic/raw/main/Images/Circuits/nm_or.PNG" width="400px" />

### AOI[aXbX...] (\{a+b+...\}Q1R)
The AOI (And-Or-Invert) gate is a bit unusual at first glance, and it is not as well known as the other gates. However, it is essential for building efficient NMOS circuits. This gate acts on "sets" of inputs, and processes them as follows:
- It first runs each "set" of inputs through an `n`-way AND gate, where `n` is the number of inputs in that set.
- The results from all of the AND gates are run through an `m`-way OR gate, where `m` is the number of sets.
- Finally, the output of the OR gate is run through a NOT gate (also called an inverter).

AOI gates are defined by a series of numbers, which specify exactly how many sets of inputs there are, and how many inputs are in each set. Each set can have a different number of inputs, and you can have an many sets as you like. This is in the format `aXbXcX...`, where `a`, `b`, `c`, etc. specify how many inputs each set has, in order. So a `2X3X1` AOI gate would have 3 sets with 2 inputs going to the first AND gate, 3 inputs going to the second AND gate, and the third set has only 1 input that goes directly to the OR gate stage (because AND only makes sense with 2 or more inputs).

Here is an example of an AOI2X2 gate using conventional combinational logic.

<img src="https://github.com/nimaid/DiscreteQLogic/raw/main/Images/Circuits/aoi2x2_function.PNG" width="400px" />

So why do we care about this odd gate as a single unit? Why can't we just use combinations of AND and NOR gates whenever we need to do these types of operations? The answer is that all of these logical operations can be easily implemented in a single NMOS logic block that uses far fewer transistors and resistors to achieve the same behavior.

Here is that same AIO2x2 gate in NMOS logic, using 4Q1R.

<img src="https://github.com/nimaid/DiscreteQLogic/raw/main/Images/Circuits/nm_aoi2x2.PNG" width="400px" />

The way this works is actually very clever. First, observe that this is still arranged with a pullup resistor and transistors that, with some combinations of inputs, shorts to ground. This is the same idea as the NOT gate, and this is where the "inversion" comes from.

Second, observe that there are 2 parallel paths to ground, just like the NOR gate. The only difference is that instead of each path has 2 transistors in series, which is exactly the same method used to construct the NAND gate. Indeed, when either set of series transistors is conducting, the output will be shorted to ground, providing the AND functionality for each set.

Finally, observe that because the sets of series transistors are in parallel with each other, the compound effect of ORing the results of the 2 AND operations is realized.

Here is an example of a 2X1 AOI gate.

<img src="https://github.com/nimaid/DiscreteQLogic/raw/main/Images/Circuits/nm_aoi2x1.PNG" width="400px" />

And just to make sure it makes sense, here is a 2X2X2X2 AOI gate.

<img src="https://github.com/nimaid/DiscreteQLogic/raw/main/Images/Circuits/nm_aoi2x2x2x2.PNG" width="400px" />

As you can see, you can customize the number of sets and their respective input count to fit your specific needs in the same way you can customize the number of inputs to a NAND or NOR gate.

The final transistor count of each AOI gate will be exactly equal to the total number of inputs, and each AOI gate will only ever use a single resistor.

### WIP
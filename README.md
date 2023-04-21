# DiscreteQLogic
My resources and projects relating to digital circuits made out of discrete transistors.

## Efficient Discrete NMOS Logic Gate Designs
I have yet to find a well-compiled source that lists the most efficient NMOS implementations using discrete MOSFETS and resistors. This is likely because, well, it's a very slow and outdated technology that draws more power than CMOS.

However, for DIY projects where one wishes to do the bare minimum of soldering, layout, and purchasing, NMOS provides very good functionality at about half the transistor count of CMOS (at the expense of adding some resistors). Therefore, I have decided to use NMOS for my DIY projects, and as such, I have been collecting the most efficient gate designs, which use fewest transistors and resistors possible.

*(I have been making a library of these parts for both Digital and LTspice, in order to simulate them before building them. You can find these libraries in their respective subfolders of this repository.)*

For this list, I will use some shorthand notation to refer to the total transistor and resistor counts for each part. This shorthand will follow the format `xQyR`, where `x` is the total transistor count and `y` is the total resistor count. So, for example, an XOR gate which was labeled `6Q3R` would require 6 transistors and 3 resistors to build.

Sometimes, you may see the part count listed in the format `(!aQbR/xQyR)`. This means the simplest (lowest part count) version of the part has it's input(s) or output(s) inverted (the `!` means `NOT` or inversion). *This inverted version uses `a` transistors and `b` resistors.* In order to use the part in it's non-inverted state, one or more NOT gates is needed, which increases the total component count per part. *This non-inverted version uses `x` transistors and `y` resistors.* If you are using many of these parts with a shared signal on their inputs (like a clock), it is more economical to invert that signal *once* before it then goes into each of the inverted variants of the part. In addition, sometimes you get inverted outputs for free (like with latches and flip-flops), so you actually don't even need NOT gates a lot of the time! This can save a *TON* of components when building things like multi-bit registers or enablers, where the savings add up with more bits.

Unless otherwise stated, all transistors are N-type.

Resistor values should be chosen based on acceptable power dissipation and speed requirements. If the resistors are large (on the order of 10kΩ+), then power dissipation will be very low (the resistor lets less current through to ground), but the response time of the gate will be much slower. This is due to an inherent weakness in NMOS where it takes longer to charge up the combined gate capacitance of the MOSFETs and the stray capacitance in the wires though a larger resistor. Conversely, smaller values will yield higher power usage, but faster response times.

### NOT (1Q1R)
<details>
<summary>Details</summary>

The simplest gate to construct is a NOT gate (also known as an inverter). This is simply a pullup resistor with a transistor configured to short the output to ground when voltage is applied to it's gate. Make sure you understand how this gate works, because this fundamental principal is the foundation which allows the systematic construction of every other NMOS gate.

<img src="https://github.com/nimaid/DiscreteQLogic/raw/main/Images/Circuits/nm_not.PNG" width="400px" />

</details>

### NAND (2Q1R)
<details>
<summary>Details</summary>

The next step up in complexity is the NAND gate. This is essentially just a NOT gate with an extra transistor in series to ground. This has the effect of only shorting the output to ground if *both* transistors are conducting. This results in the behavior of a NAND gate.

<img src="https://github.com/nimaid/DiscreteQLogic/raw/main/Images/Circuits/nm_nand.PNG" width="400px" />

</details>

### NOR (2Q1R)
<details>
<summary>Details</summary>

The NOR gate is almost exactly the same as the NAND gate, except the second transistor is connected in parallel as opposed to series. This has the effect of shorting the output to ground if *either* transistors are conducting. This results in the behavior of a NOR gate.

<img src="https://github.com/nimaid/DiscreteQLogic/raw/main/Images/Circuits/nm_nor.PNG" width="400px" />

</details>

### n-way NAND and NOR (\{n\}Q1R)
<details>
<summary>Details</summary>

It is possible to efficiently make NAND and NOR gates that have more than 2 inputs without chaining together the above units. This method uses fewer transistors and resistors than simply chaining the 2-way gates together. We do this be applying the same logic that took us from a 1-way NOT gate to 2-way NAND and NOR gates, but instead of putting only 2 transistors in either series or parallel, we put `n` transistors, where `n` is the number of inputs we want.

Here is an 8-way NAND gate.

<img src="https://github.com/nimaid/DiscreteQLogic/raw/main/Images/Circuits/nm_nand8.PNG" height="400px" />

Here is an 8-way NOR gate.

<img src="https://github.com/nimaid/DiscreteQLogic/raw/main/Images/Circuits/nm_nor8.PNG" width="400px" />

</details>

### AND and OR (3Q2R)
<details>
<summary>Details</summary>

The best way to make AND and OR gates happens to be the most straightforward. All we have to do is add a NOT gate after the NAND and NOR gates, as shown.

AND:

<img src="https://github.com/nimaid/DiscreteQLogic/raw/main/Images/Circuits/nm_and.PNG" width="400px" />

OR:

<img src="https://github.com/nimaid/DiscreteQLogic/raw/main/Images/Circuits/nm_or.PNG" width="400px" />

</details>

### AOI[a-b-...] (\{a + b + ...\}Q1R)
<details>
<summary>Details</summary>

The AOI (And-Or-Invert) gate is a bit unusual at first glance, and it is not as well known as the other gates. However, it is essential for building efficient NMOS circuits. This gate acts on "sets" of inputs, and processes them as follows:
- It first runs each "set" of inputs through an `n`-way AND gate, where `n` is the number of inputs in that set.
- The results from all of the AND gates are run through an `m`-way OR gate, where `m` is the number of sets.
- Finally, the output of the OR gate is run through a NOT gate (also called an inverter).

AOI gates are defined by a series of numbers, which specify exactly how many sets of inputs there are, and how many inputs are in each set. Each set can have a different number of inputs, and you can have an many sets as you like. This is in the format `a-b-c-...`, where `a`, `b`, `c`, etc. specify how many inputs each set has, in order. So a `2-3-1` AOI gate would have 3 sets with 2 inputs going to the first AND gate, 3 inputs going to the second AND gate, and the third set has only 1 input that goes directly to the OR gate stage (because AND only makes sense with 2 or more inputs).

Here is an example of an AOI2-2 gate using conventional combinational logic.

<img src="https://github.com/nimaid/DiscreteQLogic/raw/main/Images/Circuits/aoi2-2_function.PNG" width="400px" />

So why do we care about this odd gate as a single unit? Why don't we just use combinations of AND and NOR gates whenever we need to do these types of operations? The answer is that all of these logical operations can be easily implemented in a single NMOS logic block that uses far fewer transistors and resistors to achieve the same behavior.

Here is that same AIO2-2 gate in NMOS logic, using 4Q1R.

<img src="https://github.com/nimaid/DiscreteQLogic/raw/main/Images/Circuits/nm_aoi2-2.PNG" width="400px" />

The way this works is actually very clever. First, observe that this is still arranged with a pullup resistor and transistors that, with some combinations of inputs, shorts to ground. This is the same idea as the NOT gate, and this is where the "inversion" comes from.

Second, observe that there are 2 parallel paths to ground, just like the NOR gate. The only difference is that instead of a single transistor, each path has 2 transistors in series, which is exactly the same method used to construct the NAND gate. Indeed, when either set of series transistors is conducting, the output will be shorted to ground, providing the AND functionality for each set.

Finally, observe that because the sets of series transistors are in parallel with each other, the compound effect of ORing the results of the 2 AND operations is realized.

Here is an example of a 2-1 AOI gate.

<img src="https://github.com/nimaid/DiscreteQLogic/raw/main/Images/Circuits/nm_aoi2-1.PNG" width="400px" />

And just to make sure it makes sense, here is a 2-2-2-2 AOI gate.

<img src="https://github.com/nimaid/DiscreteQLogic/raw/main/Images/Circuits/nm_aoi2-2-2-2.PNG" width="400px" />

As you can see, you can customize the number of sets and their respective input count to fit your specific needs in the same way you can customize the number of inputs to a NAND or NOR gate.

The final transistor count of each AOI gate will be exactly equal to the total number of inputs, and each AOI gate will only ever use a single resistor.

</details>

### XOR (6Q3R)
<details>
<summary>Details</summary>

It is possible to use an AOI2-2 gate and 2 NOT gates to make an extremely elegant XOR gate, as shown below.

<img src="https://github.com/nimaid/DiscreteQLogic/raw/main/Images/Circuits/nm_xor.PNG" width="400px" />

To understand why this works, think about the AOI gate as "a gate that will set it's output to 0 only when a set of inputs is all 1". In this way, we can analyze the truth table of the XOR gate to find which input conditions result in a 0 and test for them with sets of AND gates that have their inputs set to 1 in those conditions.

XOR gate truth table:
```
┌───┬───┬─────┐
│ A │ B │ Out │
╞═══╪═══╪═════╡
│ 0 │ 0 │  0  │
├───┼───┼─────┤
│ 0 │ 1 │  1  │
├───┼───┼─────┤
│ 1 │ 0 │  1  │
├───┼───┼─────┤
│ 1 │ 1 │  0  │
└───┴───┴─────┘
```

We can see that the output is only 0 when both inputs are the same. Therefore, the first AND gate in the AOI2-2 is fed with both inputs directly, so that the output will go to 0 when both inputs are 1. Next, we need the output to also be 0 when both inputs are 0, and we can do this by simply inverting both inputs before feeding them into the second AND gate. Now we have a gate that outputs 0 when the inputs are either both 1 or both 0, and outputs 1 otherwise. This is an XOR gate!

</details>

### XNOR (6Q3R)
<details>
<summary>Details</summary>

We can implement the XNOR gate without using the classic XOR + NOT gate setup. To do so, we simply re-order the NOT gates in our XOR gate design so that the output goes to 0 in each case where the inputs are different, as opposed to the same.

<img src="https://github.com/nimaid/DiscreteQLogic/raw/main/Images/Circuits/nm_xnor.PNG" width="400px" />

</details>

### Enabler / 3-State Driver (!5Q1R/6Q2R)
<details>
<summary>Details</summary>

This component is a bit unique, as it is the only one which *requires* a few P-channel MOSFETs in addition to N-channel ones. This circuit takes 2 inputs, `In` (input) and `en` (enable). When `en` is 1, the output is equal to `In`. However, when `en` is 0, the output is in a state known as "high impedance". This is a state that is neither a 0 (ground) or 1 (VCC), but instead the output is electrically disconnected entirely.

This is extremely useful when you want to have 2 signals occupy the same wire at different times. To understand the reason why, lets take an example case where we connect the outputs of 2 AND gates to each other directly. If the first was outputting 1 (VCC) and the second was outputting 0 (ground), then there would be a short-circuit through that wire and those 2 AND gates, which would cause the device to malfunction and likely sustain damage. By putting enablers between the outputs and their shared wire, and by *only enabling a single output at a time*, you can avoid such a disaster.

Before showing you the enabler circuit, it will be useful to first understand how a CMOS-based NOT gate works:

<img src="https://github.com/nimaid/DiscreteQLogic/raw/main/Images/Circuits/cm_not.PNG" width="400px" />

The top transistor is P-channel, and the bottom one is N-channel. In the configuration shown, the N-channel MOSFET will conduct (to ground) when VCC (1) is applied to it's gate, and will act like an open switch when it is grounded (0). This works just like in the N-channel NOT gate. However, the P-channel MOSFET behaves in exactly the opposite way. When VCC (1) is applied to it's gate, it acts like an open switch, and it conducts (to VCC) when the gate is grounded (0).

With this understanding, we can see that when `In` is 0, the upper P-channel MOSFET will be conducting to VCC (1), and the lower N-channel MOSFET will be disconnected, resulting in `Out` being only connected to VCC, and therefore a 1. Conversely, when `In` is 1, the P-channel MOSFET will be open and the N-channel one will be conducting to ground, therefore resulting in a 0. This is the fundamental idea behind CMOS, and it is used in the construction of the enabler circuit.

Now, we are ready to look at the *inverted* enabler circuit (5Q1R):

<img src="https://github.com/nimaid/DiscreteQLogic/raw/main/Images/Circuits/nm_enablen.PNG" width="400px" />

The top 2 transistors are P-channel, while the lower two are N-channel. *(This means the circuit uses 3 N-channel MOSFETs and 2 P-channel MOSFETs.)*

First, note how to topmost (P-channel) and bottommost (N-channel) MOSFETs both have their gates connected directly to `In`, just like the CMOS NOT gate. This means that if those other 2 MOSFETs weren't in the way, this circuit would actually *be* a CMOS NOT gate, and would therefore just invert the input signal. (Out = !In) Alone this isn't very special, but those 2 MOSFETs in-between these ones and `Out` are what actually make this circuit useful as an enabler.

The 2 MOSFETs in-between the others (the ones connected to `Out`) are also a P-channel/N-channel pair, but with a single critical change from the CMOS NOT gate. Instead of both of their gates being directly connected, the upper-middle P-channel MOSFET has it's gate input inverted by a NOT gate. This means that when `en` is 1, *both* MOSFETs will conduct, but when `In` is 0, *neither* MOSFET will conduct (both act like an open switch). This means that when `en` is 1, the effect of the topmost and bottommost MOSFETs are uninterrupted and `Out` is equal to `!In`. However, when `en` is 0, `Out` is completely disconnected from both VCC and ground, *regardless* of the state of topmost and bottommost MOSFETs. This results in the desired behavior of an enabler, but with the input inverted.

In situations where an inverted input signal is already available without adding a NOT gate (like the inverted output on a latch or flip-flop), you can simply using this inverted version of the enabler and remove a few components from the design. However, there are times where you simply need an enabler with a non-inverted input. In these situations, you have to bite the bullet and add a NOT gate, as shown below.

Non-inverted Enabler (6Q2R):

<img src="https://github.com/nimaid/DiscreteQLogic/raw/main/Images/Circuits/nm_enable.PNG" width="400px" />

</details>

### WIP
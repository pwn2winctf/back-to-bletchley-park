# Instructions

To create qasm for the chall:

```
python synth.py -nb [NUM_BITS] -A [Secret number] -N [Number to factor] --obfuscate_setup --hide_names
```

Always use `nb = ceil( log2(N) ) + 1` to assure obfuscation step doesn't break


Run synth with parameters to generate circuit.qasm
E.G.

```
python synth.py -nb 5 -N 15 -A 9
```

This creates a circuit capable of calculating A^y % N using quantum registers
of nb qubits.

To create the classical counterpart of this circuit run parser_qasm.py
E.G.

```
python parser_qasm.py circuit.qasm
```

To test the (classical) circuit run the test suite

```
python test_code.py
```


# Solution

Please see the [write-up by sasdf](https://sasdf.github.io/ctf/writeup/2018/pwn2win/rev/back_to_bletchley_park/).

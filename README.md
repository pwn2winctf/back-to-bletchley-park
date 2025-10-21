# Back to Bletchley Park

## Description

We have gone quantum. A collaborator of ours built this quantum circuit to
compute the factorization of a Bavs RSA key and took note of the results.
Unfortunatly we could not get in touch with her lately, so we need your
help undestanding what she did. Once we figure out the circuit and
discover what are the values of A and N, we can run it through her script to
decode the message. We don't trust you enough yet, so give us the values of
A and N, and if we can decrypt the message, we'll tell you the result she got
so you too can decrypt the message.

## Solution

Please see the [write-up by sasdf](https://sasdf.github.io/ctf/writeup/2018/pwn2win/rev/back_to_bletchley_park/).

## How to rebuild challenge files

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


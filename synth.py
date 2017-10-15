LIB = """
include "qelib1.inc";
gate maj c,b,a
{
  cx a,b;
  cx a,c;
  ccx b,c,a;
}
gate ums c,s,a
{
  ccx s,c,a;
  cx a,c;
  cx c,s;
}
gate umj c,b,a
{
  ccx b,c,a;
  cx a,c;
  cx a,b;
}
gate cmj c,b,a,x
{
  ccx x,a,b;
  cx a,c;
  ccx b,c,a;
}
gate cus c,s,a,x
{
  ccx s,c,a;
  cx a,c;
  ccx x,c,s;
}
"""


def arg_list(name, n):
    """
    Argument list

    n qubits
    """
    return ','.join('{}{}'.format(name, i) for i in range(n))


def arg_vec(name, n):
    """
    Pass register as argument

    n qubits
    """
    return ','.join('{}[{}]'.format(name, i) for i in range(n))


def cdkm(n):
    """
    The Complete Adder

    input: b,a
    output: b+a,a

    a[n-1] is carry-in
    b[n-1] is carry-out and must be |0> at input
    """
    src = 'gate cdkm{n} {b},{a}\n'.format(n=n,
                                          b=arg_list('b',n),
                                          a=arg_list('a',n))
    src += '{\n'
    for i in range(n-1):
        src += '  maj a{},b{},a{};\n'.format((n + i - 1) % n, i, i)
    src += '  cx a{},b{};\n'.format(n-2, n-1)
    for i in range(n-2, -1, -1):
        src += '  ums a{},b{},a{};\n'.format((n + i - 1) % n, i, i)
    src += '}\n'
    return src


def ccdkm(n):
    """
    Controlled CDKM Adder

    input: b,a,x
    output: b+a*x,a,x

    a[n-1] is carry-in
    b[n-1] is carry-out and must be |0> at input
    x is control
    """
    src = 'gate ccdkm{n} {b},{a},x\n'.format(n=n,
                                             b=arg_list('b',n),
                                             a=arg_list('a',n))
    src += '{\n'
    for i in range(n-1):
        src += '  cmj a{},b{},a{},x;\n'.format((n + i - 1) % n, i, i)
    src += '  cx a{},b{};\n'.format(n-2, n-1)
    for i in range(n-2, -1, -1):
        src += '  cus a{},b{},a{},x;\n'.format((n + i - 1) % n, i, i)
    src += '}\n'
    return src


def plusone(n):
    """
    Plus 1

    input: b,s
    output: b+1,s

    b[n-1] is carry-out and must be |0> at input
    s is scratch and must be |0..0>
    """
    src = 'gate plusone{n} {b},{s}\n'.format(n=n,
                                             b=arg_list('b',n),
                                             s=arg_list('s',n))
    src += '{\n'
    src += '  x s0;\n'
    src += '  cdkm{} {},{};\n'.format(n, arg_list('b',n), arg_list('s',n))
    src += '  x s0;\n'
    src += '}\n'
    return src


def minusone(n):
    """
    Minus 1

    input: b,s
    output: b-1,s

    b[n-1] is carry-out and must be |0> at input
    s is scratch and must be |0..0>
    """
    src = 'gate minusone{n} {b},{s}\n'.format(n=n,
                                              b=arg_list('b',n),
                                              s=arg_list('s',n))
    src += '{\n'
    for i in range(n-1):
        src += '  x s{};\n'.format(i)
    src += '  cdkm{} {},{};\n'.format(n, arg_list('b',n), arg_list('s',n))
    for i in range(n-1):
        src += '  x s{};\n'.format(i)
    src += '  x b{};\n'.format(n-1)
    src += '}\n'
    return src


def cdkmsub(n):
    """
    CDKM Subtractor
    Known not to work with a==0

    input: b,a,s
    output: b-a,a,s

    a[n-1] is carry-in
    b[n-1] is carry-out and must be |0> at input
    s is scratch and must be |0..0>
    x is control
    """
    src = 'gate cdkmsub{n} {b},{a},{s}\n'.format(n=n,
                                                 b=arg_list('b',n),
                                                 a=arg_list('a',n),
                                                 s=arg_list('s',n))
    src += '{\n'
    for i in range(n-1):
        src += '  x a{};\n'.format(i)
    src += '  plusone{} {},{};\n'.format(n, arg_list('a',n), arg_list('s',n))
    src += '  cdkm{} {},{};\n'.format(n, arg_list('b',n), arg_list('a',n))
    src += '  x b{};\n'.format(n-1)
    src += '  minusone{} {},{};\n'.format(n, arg_list('a',n), arg_list('s',n))
    for i in range(n-1):
        src += '  x a{};\n'.format(i)
    src += '}\n'
    return src


def ccdkmsub(n):
    """
    Controlled CDKM Subtractor
    Known not to work with a==0

    input: b,a,s,x
    output: b-a,a,s,x

    a[n-1] is carry-in
    b[n-1] is carry-out and must be |0> at input
    s is scratch and must be |0..0>
    """
    src = 'gate ccdkmsub{n} {b},{a},{s},x\n'.format(n=n,
                                                    b=arg_list('b',n),
                                                    a=arg_list('a',n),
                                                    s=arg_list('s',n))
    src += '{\n'
    for i in range(n-1):
        src += '  x a{};\n'.format(i)
    src += '  plusone{} {},{};\n'.format(n, arg_list('a',n), arg_list('s',n))
    src += '  ccdkm{} {},{},x;\n'.format(n, arg_list('b',n), arg_list('a',n))
    src += '  cx x, b{};\n'.format(n-1)
    src += '  minusone{} {},{};\n'.format(n, arg_list('a',n), arg_list('s',n))
    for i in range(n-1):
        src += '  x a{};\n'.format(i)
    src += '}\n'
    return src


def synth():
    src = LIB
    src += cdkm(4)
    src += ccdkm(4)
    src += plusone(4)
    src += minusone(4)
    src += cdkmsub(4)
    src += ccdkmsub(4)
    src += """
    qreg a[4];
    qreg b[4];
    qreg scratch[4];
    qreg ctrl[1];
    creg c[4];

    //x ctrl[0];

    x b[2];
    x a[1];
    x a[0];

    ccdkmsub4 {},{},{},ctrl[0];

    measure b -> c;
    """.format(arg_vec('b',4),arg_vec('a',4),arg_vec('scratch',4))
    return src


if __name__ == '__main__':
    with open('circuit.qasm', 'w') as f:
        f.write(synth())
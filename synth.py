import sys
import argparse

qasm_code = ["""
include "qelib1.inc";
"""]


gates_declared = set()




class declare:
    class AlreadyDeclared(Exception):
        pass

    class Bomb:
        def __init__(self, exc):
            self.exc = exc
        def __getattr__(self, attr):
            raise self.exc()

    def __init__(self, name, params):
        self.name = name
        self.src = [
            'gate {name} {params}'.format(name=name, params=params),
            '{'
        ]

    def __enter__(self):
        if self.name in gates_declared:
            return self.Bomb(self.AlreadyDeclared)
        gates_declared.add(self.name)
        return self.src

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type == self.AlreadyDeclared:
            return True
        self.src.append('}')
        qasm_code.extend(self.src)


def arg_list(name, n):
    return ','.join('{}{}'.format(name, i) for i in range(n))


def arg_vec(name, n):
    return ','.join('{}[{}]'.format(name, i) for i in range(n))


def maj():
    with declare('maj', 'c,b,a') as src:
        src.extend([
            '  cx a,b;',
            '  cx a,c;',
            '  ccx b,c,a;',
        ])


def ums():
    with declare('ums', 'c,s,a') as src:
        src.extend([
            '  ccx s,c,a;',
            '  cx a,c;',
            '  cx c,s;',
        ])


def umj():
    with declare('umj', 'c,b,a') as src:
        src.extend([
            '  ccx b,c,a;',
            '  cx a,c;',
            '  cx a,b;',
        ])

def cuj():
    with declare('cuj', 'c,b,a,x') as src:
        src.extend([
            '  ccx b,c,a;',
            '  cx a,c;',
            '  ccx x,a,b;',
        ])


def cmj():
    with declare('cmj', 'c,b,a,x') as src:
        src.extend([
            '  ccx x,a,b;',
            '  cx a,c;',
            '  ccx b,c,a;',
        ])


def cus():
    with declare('cus', 'c,s,a,x') as src:
        src.extend([
            '  ccx s,c,a;',
            '  cx a,c;',
            '  ccx x,c,s;',
        ])






def add(n):
    """ CDKM adder without carry output """
    maj()
    ums()
    with declare('add{}'.format(n),
                 '{b},cin,{a}'.format(b=arg_list('b',n),
                                      a=arg_list('a',n))) as src:
        for i in range(n):
            cin = 'cin' if i == 0 else 'a{}'.format(i - 1)
            src.append('  maj {},b{},a{};'.format(cin, i, i))
        for i in range(n-1, -1, -1):
            cin = 'cin' if i == 0 else 'a{}'.format(i - 1)
            src.append('  ums {},b{},a{};'.format(cin, i, i))



def addc(n):
    """ CDKM adder with carry output """
    maj()
    ums()
    with declare('addc{}'.format(n),
                 'cout,{b},cin,{a}'.format(b=arg_list('b',n),
                                           a=arg_list('a',n))) as src:
        for i in range(n):
            cin = 'cin' if i == 0 else 'a{}'.format(i - 1)
            src.append('  maj {},b{},a{};'.format(cin, i, i))
        src.append('  cx a{},cout;'.format(n-2))
        for i in range(n-1, -1, -1):
            cin = 'cin' if i == 0 else 'a{}'.format(i - 1)
            src.append('  ums {},b{},a{};'.format(cin, i, i))


def cmb(n):
    maj()
    umj()
    """ Comparator base block (just like addc but only changes cout) """
    with declare('cmb{}'.format(n),
                 'cout,{b},cin,{a}'.format(b=arg_list('b',n),
                                           a=arg_list('a',n))) as src:
        for i in range(n):
            cin = 'cin' if i == 0 else 'a{}'.format(i - 1)
            src.append('  maj {},b{},a{};'.format(cin, i, i))
        src.append('  cx a{},cout;'.format(n-1))
        for i in range(n-1, -1, -1):
            cin = 'cin' if i == 0 else 'a{}'.format(i - 1)
            src.append('  umj {},b{},a{};'.format(cin, i, i))

def ccmb(n):
    cmj()
    cuj()
    """ Comparator base block (just like addc but only changes cout) """
    with declare('ccmb{}'.format(n),
                 'cout,{b},cin,{a},x'.format(b=arg_list('b',n),
                                           a=arg_list('a',n))) as src:
        for i in range(n):
            cin = 'cin' if i == 0 else 'a{}'.format(i - 1)
            src.append('  cmj {},b{},a{},x;'.format(cin, i, i))
        src.append('  cx a{},cout;'.format(n-1))
        for i in range(n-1, -1, -1):
            cin = 'cin' if i == 0 else 'a{}'.format(i - 1)
            src.append('  cuj {},b{},a{},x;'.format(cin, i, i))

def cadd(n):
    """ Controlled CDKM adder without carry output """
    cmj()
    cus()
    with declare('cadd{}'.format(n),
                 '{b},cin,{a},x'.format(b=arg_list('b',n),
                                        a=arg_list('a',n))) as src:
        for i in range(n):
            cin = 'cin' if i == 0 else 'a{}'.format(i - 1)
            src.append('  cmj {},b{},a{},x;'.format(cin, i, i))
        for i in range(n-1, -1, -1):
            cin = 'cin' if i == 0 else 'a{}'.format(i - 1)
            src.append('  cus {},b{},a{},x;'.format(cin, i, i))


def caddc(n):
    """ Controlled CDKM adder with carry output """
    cmj()
    cus()
    with declare('caddc{}'.format(n),
                 'cout,{b},cin,{a},x'.format(b=arg_list('b',n),
                                             a=arg_list('a',n))) as src:
        for i in range(n):
            cin = 'cin' if i == 0 else 'a{}'.format(i - 1)
            src.append('  cmj {},b{},a{},x;'.format(cin, i, i))
        src.append('  cx a{},cout;'.format(n-2))
        for i in range(n-1, -1, -1):
            cin = 'cin' if i == 0 else 'a{}'.format(i - 1)
            src.append('  cus {},b{},a{},x;'.format(cin, i, i))


def increment(n):
    """ Increment """
    add(n)
    with declare('increment{}'.format(n),
                 '{b},{s}'.format(b=arg_list('b',n),
                                  s=arg_list('s',n+1))) as src:
        src.append('  x s0;')
        src.append('  add{n} {b},s{n},{s};'.format(n=n,
                                                   b=arg_list('b',n),
                                                   s=arg_list('s',n)))
        src.append('  x s0;')


def decrement(n):
    """ Decrement """
    add(n)
    with declare('decrement{}'.format(n),
                 '{b},{s}'.format(b=arg_list('b',n),
                                  s=arg_list('s',n+1))) as src:
        for i in range(n):
            src.append('  x s{};'.format(i))
        src.append('  add{n} {b},s{n},{s};'.format(n=n,
                                                   b=arg_list('b',n),
                                                   s=arg_list('s',n)))
        for i in range(n-1, -1, -1):
            src.append('  x s{};'.format(i))


def sub(n):
    """ CDKM Subtractor """
    increment(n)
    add(n)
    decrement(n)
    with declare('sub{}'.format(n),
                 '{b},{a},{s}'.format(b=arg_list('b',n),
                                      a=arg_list('a',n),
                                      s=arg_list('s',n+1))) as src:
        for i in range(n):
            src.append('  x a{};'.format(i))
        src.append('  increment{n} {a},{s};'.format(n=n,
                                                    a=arg_list('a',n),
                                                    s=arg_list('s',n+1)))
        src.append('  add{n} {b},s{n},{a};'.format(n=n,
                                                   b=arg_list('b',n),
                                                   a=arg_list('a',n)))
        src.append('  decrement{n} {a},{s};'.format(n=n,
                                                    a=arg_list('a',n),
                                                    s=arg_list('s',n+1)))
        for i in range(n-1, -1, -1):
            src.append('  x a{};'.format(i))


def csub(n):
    """ Controlled CDKM Subtractor """
    increment(n)
    cadd(n)
    decrement(n)
    with declare('csub{}'.format(n),
                 '{b},{a},{s},x'.format(b=arg_list('b',n),
                                        a=arg_list('a',n),
                                        s=arg_list('s',n+1))) as src:
        for i in range(n):
            src.append('  x a{};'.format(i))
        src.append('  increment{n} {a},{s};'.format(n=n,
                                                    a=arg_list('a',n),
                                                    s=arg_list('s',n+1)))
        src.append('  cadd{n} {b},s{n},{a},x;'.format(n=n,
                                                      b=arg_list('b',n),
                                                      a=arg_list('a',n)))
        src.append('  decrement{n} {a},{s};'.format(n=n,
                                                    a=arg_list('a',n),
                                                    s=arg_list('s',n+1)))
        for i in range(n-1, -1, -1):
            src.append('  x a{};'.format(i))


def cmpge(n):
    """ Check if a >= b """
    increment(n)
    cmb(n)
    decrement(n)
    with declare('cmpge{}'.format(n),
                 '{b},{a},cout,{s}'.format(b=arg_list('b',n),
                                           a=arg_list('a',n),
                                           s=arg_list('s',n+1))) as src:
        src.append('  increment{n} {a},{s};'.format(n=n,
                                                    a=arg_list('a',n),
                                                    s=arg_list('s',n+1)))
        for i in range(n):
            src.append('  x a{};'.format(i))
        src.append('  increment{n} {a},{s};'.format(n=n,
                                                    a=arg_list('a',n),
                                                    s=arg_list('s',n+1)))
        src.append('  cmb{n} cout,{b},s{n},{a};'.format(n=n,
                                                        a=arg_list('a',n),
                                                        b=arg_list('b',n)))
        src.append('  decrement{n} {a},{s};'.format(n=n,
                                                    a=arg_list('a',n),
                                                    s=arg_list('s',n+1)))
        for i in range(n-1, -1, -1):
            src.append('  x a{};'.format(i))
        src.append('  decrement{n} {a},{s};'.format(n=n,
                                                    a=arg_list('a',n),
                                                    s=arg_list('s',n+1)))
        src.append('  x cout;')

def ccmpge(n):
    """ Check if a >= b """
    increment(n)
    ccmb(n)
    decrement(n)
    with declare('ccmpge{}'.format(n),
                 '{b},{a},cout,{s},x'.format(b=arg_list('b',n),
                                           a=arg_list('a',n),
                                           s=arg_list('s',n+1))) as src:
        src.append('  increment{n} {a},{s};'.format(n=n,
                                                    a=arg_list('a',n),
                                                    s=arg_list('s',n+1)))
        for i in range(n):
            src.append('  x a{};'.format(i))
        src.append('  increment{n} {a},{s};'.format(n=n,
                                                    a=arg_list('a',n),
                                                    s=arg_list('s',n+1)))
        src.append('  ccmb{n} cout,{b},s{n},{a},x;'.format(n=n,
                                                        a=arg_list('a',n),
                                                        b=arg_list('b',n)))
        src.append('  decrement{n} {a},{s};'.format(n=n,
                                                    a=arg_list('a',n),
                                                    s=arg_list('s',n+1)))
        for i in range(n-1, -1, -1):
            src.append('  x a{};'.format(i))
        src.append('  decrement{n} {a},{s};'.format(n=n,
                                                    a=arg_list('a',n),
                                                    s=arg_list('s',n+1)))
        src.append('  x cout;')

def ccmpg(n):
    """ Check if a >= b """
    increment(n)
    ccmb(n)
    decrement(n)
    with declare('ccmpg{}'.format(n),
                 '{b},{a},cout,{s},x'.format(b=arg_list('b',n),
                                           a=arg_list('a',n),
                                           s=arg_list('s',n+1))) as src:
        for i in range(n):
            src.append('  x a{};'.format(i))
        src.append('  increment{n} {a},{s};'.format(n=n,
                                                    a=arg_list('a',n),
                                                    s=arg_list('s',n+1)))
        src.append('  ccmb{n} cout,{b},s{n},{a},x;'.format(n=n,
                                                        a=arg_list('a',n),
                                                        b=arg_list('b',n)))
        src.append('  decrement{n} {a},{s};'.format(n=n,
                                                    a=arg_list('a',n),
                                                    s=arg_list('s',n+1)))
        for i in range(n-1, -1, -1):
            src.append('  x a{};'.format(i))
        src.append('  x cout;')


def crmod(n):
    """ Restricted a mod b """
    ccmpge(n)
    csub(n)
    with declare('crmod{}'.format(n),
                 '{b},{a},g,{s},x'.format(b=arg_list('b',n),
                                          a=arg_list('a',n),
                                          s=arg_list('s',n+1))) as src:
        src.append('  ccmpge{n} {b},{a},g,{s},x;'.format(n=n,
                                                      a=arg_list('a',n),
                                                      b=arg_list('b',n),
                                                      s=arg_list('s',n+1)))
        src.append('  csub{n} {a},{b},{s},g;'.format(n=n,
                                                     a=arg_list('a',n),
                                                     b=arg_list('b',n),
                                                     s=arg_list('s',n+1)))

def rmod(n):
    """ Restricted a mod b """
    cmpge(n)
    csub(n)
    with declare('rmod{}'.format(n),
                 '{b},{a},g,{s}'.format(b=arg_list('b',n),
                                          a=arg_list('a',n),
                                          s=arg_list('s',n+1))) as src:
        src.append('  cmpge{n} {b},{a},g,{s};'.format(n=n,
                                                      a=arg_list('a',n),
                                                      b=arg_list('b',n),
                                                      s=arg_list('s',n+1)))
        src.append('  csub{n} {a},{b},{s},g;'.format(n=n,
                                                     a=arg_list('a',n),
                                                     b=arg_list('b',n),
                                                     s=arg_list('s',n+1)))


def addmod(nb):
    """ b = b + a mod n """
    add(nb)
    rmod(nb)
    cmb(nb)
    with declare('addmod{}'.format(nb),
                 '{b},{a},{n},{s}'.format(b=arg_list('b',nb),
                                          a=arg_list('a',nb),
                                          n=arg_list('n',nb),
                                          s=arg_list('s',nb+2))) as src:
        src.append('  add{nb} {b},s{nb},{a};'.format(nb=nb,
                                                     b=arg_list('b',nb),
                                                     a=arg_list('a',nb)))
        src.append('  rmod{nb} {n},{b},s{nb1},{s};'.format(nb=nb,
                                                           nb1=nb+1,
                                                           n=arg_list('n',nb),
                                                           b=arg_list('b',nb),
                                                           s=arg_list('s',
                                                                      nb+1)))
        src.append('  cmb{nb} s{nb1},{b},s{nb},{a};'.format(nb=nb,
                                                            nb1=nb+1,
                                                            a=arg_list('a',nb),
                                                            b=arg_list('b',
                                                                       nb)))


def caddmod(nb):
    """ Controlled b = b + a mod n """
    cadd(nb)
    crmod(nb)
    cmb(nb)
    ccmpg(nb)
    with declare('caddmod{}'.format(nb),
                 '{b},{a},{n},{s},x'.format(b=arg_list('b',nb),
                                            a=arg_list('a',nb),
                                            n=arg_list('n',nb),
                                            s=arg_list('s',nb+2))) as src:
        src.append('  cadd{nb} {b},s{nb},{a},x;'.format(nb=nb,
                                                        b=arg_list('b',nb),
                                                        a=arg_list('a',nb)))
        src.append('  crmod{nb} {n},{b},s{nb1},{s},x;'.format(nb=nb,
                                                           nb1=nb+1,
                                                           n=arg_list('n',nb),
                                                           b=arg_list('b',nb),
                                                           s=arg_list('s',
                                                                      nb+1)))
        src.append('  ccmpg{nb} {b},{a},s{nb1},{s},x;'.format(nb=nb, 
                                                            nb1=nb+1,
                                                        s=arg_list('s',nb+1),
                                                        a=arg_list('a',nb),
                                                        b=arg_list('b',nb),
                                                        ))


def double(n):
    """ a = 2*a  (only works for a[n-1] = |0>) """
    with declare('double{}'.format(n),
                 '{a}'.format(a=arg_list('a',n))) as src:
        for i in range(n-1):
            src.append('  swap a{},a{};'.format(i, n-1))


def doublemod(nb):
    """ a = 2*a mod n  (only works for a[n-1] = |0>) """
    double(nb)
    rmod(nb)
    with declare('doublemod{}'.format(nb),
                 '{a},{n},g,{s}'.format(a=arg_list('a',nb),
                                          n=arg_list('n',nb),
                                          s=arg_list('s',nb+1))) as src:
        src.append('  double{nb} {a};'.format(nb=nb,
                                              a=arg_list('a',nb)))
        src.append('  rmod{nb} {n},{a},g,{s};'.format(nb=nb,
                                                      a=arg_list('a',nb),
                                                      n=arg_list('n',nb),
                                                      s=arg_list('s',nb+1)))


def multbstage(nb):
    """ Basic modular multiplication module stage """
    doublemod(nb)
    caddmod(nb)
    with declare('multbstage{}'.format(nb),
                 '{s},{a},{n},{z},g,x'.format(s=arg_list('s',nb),
                                              a=arg_list('a',nb),
                                              n=arg_list('n',nb),
                                              z=arg_list('z',nb+2))) as src:
        src.append('  caddmod{nb} {s},{a},{n},{z},x;'.format(nb=nb,
                                                             s=arg_list('s',
                                                                        nb),
                                                             a=arg_list('a',
                                                                        nb),
                                                             n=arg_list('n',
                                                                        nb),
                                                             z=arg_list('z',
                                                                        nb+2)))
        src.append('  doublemod{nb} {a},{n},g,{z};'.format(nb=nb,
                                                           a=arg_list('a',nb),
                                                           n=arg_list('n',nb),
                                                           z=arg_list('z',
                                                                      nb+1)))



def multbchain(nb):
    """ Chains basic modular multiplication stages """ 
    multbstage(nb)
    with declare('multbchain{}'.format(nb),
                 '{s},{a},{n},{z},ad,{g},{x}'.format(s=arg_list('s',nb),
                                                  a=arg_list('a',nb),
                                                  n=arg_list('n',nb),
                                                  z=arg_list('z',nb+1),
                                                  g=arg_list('g',nb),
                                                  x=arg_list('x',nb))) as src:
        for i in range(nb):
            src.append( '  multbstage{nb} {s},{a},{n},{z},ad,g{i},x{i};'.format(
                                                              nb=nb,
                                                              s=arg_list('s',nb),
                                                              a=arg_list('a',nb),
                                                              n=arg_list('n',nb),
                                                              z=arg_list('z',nb+1),
                                                              i=i))



def specificmultbchain(nb,A,N):
    multbstage(nb)
    with declare('specificmultbchain{nb}_{A}_{N}'.format(nb=nb,A=A,N=N),
                 '{s},{a},{n},{z},ad,md,{x}'.format(s=arg_list('s',nb),
                                                     a=arg_list('a',nb),
                                                     n=arg_list('n',nb),
                                                     z=arg_list('z',nb+1),
                                                     x=arg_list('x',nb))) as src:
        for i in range(nb):
            src.append('  multbstage{nb} {s},{a},{n},{z},ad,md,x{i};'.format(
                                                              nb=nb,
                                                              s=arg_list('s',nb),
                                                              a=arg_list('a',nb),
                                                              n=arg_list('n',nb),
                                                              z=arg_list('z',nb+1),
                                                              i=i))
            if 2*((A*2**i)%N)>=N:
                src.append('  x md;')

def tomodularinv(nb,A,N):
    A_inv = modular_inverse(A,N)
    mult_A = (A*2**nb)%N
    with declare('toAmodularinv{nb}_{A}_{N}'.format(nb=nb,A=A,N=N),
                '{a}'.format(a=arg_list('a',nb))) as src:
        for i in range(nb):
            mask=2**i
            if ((A_inv & mask) ^ (mult_A & mask)):
                src.append('  x a{};'.format(i))


def backtoA(nb,A,N):
    A_inv = modular_inverse(A,N)
    mult_A_inv = (A_inv * 2**nb) % N
    with declare('backtoA{nb}_{A}_{N}'.format(nb=nb,A=A,N=N),
                '{a}'.format(a=arg_list('a',nb))) as src:
        for i in range(nb):
            mask=2**i
            if ((mult_A_inv & mask) ^ (A & mask)):
                src.append('  x a{};'.format(i))

def modularmult(nb,A,N):
    A_inv = modular_inverse(A,N)

    specificmultbchain(nb,A_inv,N)
    specificmultbchain(nb,A,N)

    tomodularinv(nb,A,N)
    backtoA(nb,A,N)

    sub(nb)

    with declare('modularmult{nb}_{A}_{N}'.format(nb=nb,A=A,N=N),
                 '{s},{a},{n},{z},ad,md,{x}'.format(s=arg_list('s',nb),
                                                     a=arg_list('a',nb),
                                                     n=arg_list('n',nb),
                                                     z=arg_list('z',nb+1),
                                                     x=arg_list('x',nb))) as src:
        src.append('  specificmultbchain{nb}_{A}_{N} {s},{a},{n},{z},ad,md,{x};'.format(nb=nb,
                                                     A=A,
                                                     N=N,
                                                     s=arg_list('s',nb),
                                                     a=arg_list('a',nb),
                                                     n=arg_list('n',nb),
                                                     z=arg_list('z',nb+1),
                                                     x=arg_list('x',nb)))
        src.append('  toAmodularinv{nb}_{A}_{N} {a};'.format(nb=nb,
                                                            A=A,
                                                            N=N,
                                                            a=arg_list('a',nb)))
        for i in range(nb):
            src.append('  swap x{i},s{i};'.format(i=i))

        src.append('  sub{nb} {n},{s},{z};'.format(nb=nb,
                                                   n=arg_list('n',nb),
                                                   s=arg_list('s',nb),
                                                   z=arg_list('z',nb+1)))

        src.append('  add{nb} {s},z{nb},{n};'.format(nb=nb,
                                                      n=arg_list('n',nb),
                                                      s=arg_list('s',nb)))

        for i in range(nb):
            src.append('  swap n{i},s{i};'.format(i=i))

        src.append('  specificmultbchain{nb}_{A_inv}_{N} {s},{a},{n},{z},ad,md,{x};'.format(nb=nb,
                                                     A_inv=A_inv,
                                                     N=N,
                                                     s=arg_list('s',nb),
                                                     a=arg_list('a',nb),
                                                     n=arg_list('n',nb),
                                                     z=arg_list('z',nb+1),
                                                     x=arg_list('x',nb)))
        src.append('  backtoA{nb}_{A}_{N} {a};'.format(nb=nb,
                                                       A=A,
                                                       N=N,
                                                       a=arg_list('a',nb)))


def synth(nb,A,N):
    multbchain(nb)
    modularmult(nb,A,N)
    qasm_code.append("""
    qreg b[{nb}];
    qreg a[{nb}];
    qreg n[{nb}];
    qreg scratch[{nb1}];

    // recicled
    qreg ancilla_adder[1];

    // num is X in the article
    qreg num[{nb}];

    // one ancilla needed per bit in X
    qreg trash[{nbm1}];

    creg c[{nb}];

    x num[0];
    x num[1];

    x a[1];

    x n[0];
    x n[1];

    //multbstage{nb} {b},{a},{n},{s},ancilla_adder[0],trash[0],num[0];
    multbchain{nb} {b},{a},{n},{s},ancilla_adder[0],{t},{x};

    measure b -> c;
    """.format(nb=nb,nb1=nb+1,
               b=arg_vec('b',nb),
               a=arg_vec('a',nb),
               n=arg_vec('n',nb),
               s=arg_vec('scratch',nb+1),
               t=arg_vec('trash',nb-1),
               x=arg_vec('num',nb-1),
               nbm1=nb-1,
               ))
    return '\n'.join(qasm_code)

def modular_inverse(a,b):
    s = 0
    old_s = 1
    t = 1
    old_t = 1
    r = b
    old_r = a
    while r!=0:
        q = old_r//r
        old_r,r = r,old_r-q*r
        old_t,t = t,old_t-q*t
        old_s,s = s,old_s-q*s
    return old_s%b



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-nb',type=int,default=3,help='Number of bits in the registers')
    parser.add_argument('-A',type=int,default=2,help='Base of exponentiation')
    parser.add_argument('-N',type=int,default=3,help='All is mod N')
    args = parser.parse_args()
    nb = args.nb
    A = args.A
    N = args.N
    with open('circuit.qasm', 'w') as f:
        f.write(synth(nb,A,N))

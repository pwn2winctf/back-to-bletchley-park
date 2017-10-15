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
        src.append('  cx a{},cout;'.format(n-2))
        for i in range(n-1, -1, -1):
            cin = 'cin' if i == 0 else 'a{}'.format(i - 1)
            src.append('  umj {},b{},a{};'.format(cin, i, i))


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


def plusone(n):
    """ Plus 1 """
    add(n)
    with declare('plusone{}'.format(n),
                 '{b},{s}'.format(b=arg_list('b',n),
                                  s=arg_list('s',n+1))) as src:
        src.append('  x s0;')
        src.append('  add{n} {b},s{n},{s};'.format(n=n,
                                                   b=arg_list('b',n),
                                                   s=arg_list('s',n)))
        src.append('  x s0;')


def minusone(n):
    """ Minus 1 """
    add(n)
    with declare('minusone{}'.format(n),
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
    plusone(n)
    add(n)
    minusone(n)
    with declare('sub{}'.format(n),
                 '{b},{a},{s}'.format(b=arg_list('b',n),
                                      a=arg_list('a',n),
                                      s=arg_list('s',n+1))) as src:
        for i in range(n):
            src.append('  x a{};'.format(i))
        src.append('  plusone{n} {a},{s};'.format(n=n,
                                                  a=arg_list('a',n),
                                                  s=arg_list('s',n+1)))
        src.append('  add{n} {b},s{n},{a};'.format(n=n,
                                                   b=arg_list('b',n),
                                                   a=arg_list('a',n)))
        src.append('  minusone{n} {a},{s};'.format(n=n,
                                                   a=arg_list('a',n),
                                                   s=arg_list('s',n+1)))
        for i in range(n-1, -1, -1):
            src.append('  x a{};'.format(i))


def csub(n):
    """ Controlled CDKM Subtractor """
    plusone(n)
    cadd(n)
    minusone(n)
    with declare('csub{}'.format(n),
                 '{b},{a},x,{s}'.format(b=arg_list('b',n),
                                        a=arg_list('a',n),
                                        s=arg_list('s',n+1))) as src:
        for i in range(n):
            src.append('  x a{};'.format(i))
        src.append('  plusone{n} {a},{s};'.format(n=n,
                                                  a=arg_list('a',n),
                                                  s=arg_list('s',n+1)))
        src.append('  cadd{n} {b},s{n},{a},x;'.format(n=n,
                                                      b=arg_list('b',n),
                                                      a=arg_list('a',n)))
        src.append('  minusone{n} {a},{s};'.format(n=n,
                                                   a=arg_list('a',n),
                                                   s=arg_list('s',n+1)))
        for i in range(n-1, -1, -1):
            src.append('  x a{};'.format(i))


def synth():
    csub(4)
    qasm_code.append("""
    qreg b[4];
    qreg a[4];
    qreg scratch[5];
    qreg ctrl[1];
    creg c[4];

    x b[0];
    x b[1];
    x a[0];

    csub4 {b},{a},{s},ctrl[0];

    measure b -> c;
    """.format(b=arg_vec('b',4),a=arg_vec('a',4),s=arg_vec('scratch',5),))
    return '\n'.join(qasm_code)


if __name__ == '__main__':
    with open('circuit.qasm', 'w') as f:
        f.write(synth())
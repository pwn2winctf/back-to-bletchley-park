import sys

f = open(sys.argv[1])

base_code = '''
def swap(a,b):
    return b,a

def cx(a,b):
    return a, a^b

def ccx(a,b,c):
    return a, b, c^(a and b)

def x_b(a):
    return 1-a

def cswap(c,a,b):
    if c:
        return c,b,a
    return c,a,b
'''

code = []
indentation = '    '
for line in f:
    if line.startswith("//"):
        code.extend([line.replace("//","#")])
    tok = line.strip().split(' ')
    if tok[0] == 'gate':
        _ = f.readline()
        ret_vals = tok[2]
        code.extend(['def ' + tok[1] + '(' + tok[2] + '):'])
        l = f.readline().strip().split(' ')
        if l[0]=='}':
            code.extend([indentation+'return ' + ret_vals +'\n'])
        while l[0] != '}':
            func = l[0]
            if func == 'x':
                func = 'x_b'
            args = l[1][:-1]
            code.extend([indentation+args + '=' + func + '(' + args + ')'])
            l = f.readline().strip().split(' ')
            if l[0]=='}':
                code.extend([indentation+'return ' + ret_vals +'\n'])

with open('classical_code.py','w') as f:
    code =  '\n'.join(code) + base_code
    f.write(code)


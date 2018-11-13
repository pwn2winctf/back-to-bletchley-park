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

'''

code = []
indentation = '    '
for line in f:
    tok = line.strip().split(' ')
    if tok[0] == 'gate':
        _ = f.readline()
        ret_vals = tok[2]
        code.extend(['def ' + tok[1] + '(' + tok[2] + '):'])
        l = f.readline().strip().split(' ')
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
    code = base_code + '\n'.join(code)
    f.write(code)


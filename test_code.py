import sys
import classical_code as cc
import unittest as ut
import numpy as np

#Detect number of bits
with open("classical_code.py") as f:
    for a in f:
        if a.startswith('def double'):
            NUM_BITS = int(a.split('(')[0][-1])
        if a.startswith('def specificmultbchain'):
            aux = a.split('(')[0].split('_')
            CONST_A,CONST_N = int(aux[1]),int(aux[2])

def convert_to_bits(num,nbits):
    return [ (num//2**i) % 2 for i in range(nbits)]

def convert_to_num(bits):
    return sum([b*2**i for i,b in enumerate(bits)])

def nums_from_bits(bits,list_of_nums):
    list_num_bits = list(np.array(list_of_nums)[:,1])
    list_start = [0]+list(np.cumsum(list_num_bits))
    return [convert_to_num(bits[list_start[i]:list_start[i+1]])
                            for i in range(len(list_start)-1)]


def bits_from_nums(*kwargs):
    a = []
    for num,nbits in kwargs:
        a.extend(convert_to_bits(num,nbits))
    return a


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

class TestAdd(ut.TestCase):
    def test_with_overflow(self):
        for i in range(2**(NUM_BITS-1)):
            for j in range(2**(NUM_BITS-1)):
                if i+j<=2**(NUM_BITS-1)-1:
                    break
                list_of_nums = [(i,NUM_BITS),(0,1),(j,NUM_BITS)]
                func_input = bits_from_nums(*list_of_nums)
                func_output = getattr(cc,"add{}".format(NUM_BITS))(*func_input)
                conv = nums_from_bits(func_output, list_of_nums)
                self.assertEqual(i+j,conv[0])

    def test_no_overflow(self):
        for i in range(2**(NUM_BITS-1)):
            for j in range(2**(NUM_BITS-1)):
                if i+j>2**(NUM_BITS-1)-1:
                    break
                list_of_nums = [(i,NUM_BITS),(0,1),(j,NUM_BITS)]
                func_input = bits_from_nums(*list_of_nums)
                func_output = getattr(cc,"add{}".format(NUM_BITS))(*func_input)
                conv = nums_from_bits(func_output, list_of_nums)
                self.assertEqual(i+j,conv[0])

class TestIncrementDecrement(ut.TestCase):
    def test_increment(self):
        for i in range(2**(NUM_BITS-1)):
            list_of_nums = [(i,NUM_BITS),(0,NUM_BITS+1)]
            func_input = bits_from_nums(*list_of_nums)
            func_output = getattr(cc,"increment{}".format(NUM_BITS))(*func_input)
            conv = nums_from_bits(func_output, list_of_nums)
            self.assertEqual(i+1,conv[0])
            self.assertEqual(0,conv[1])

    def test_decrement(self):
        for i in range(1,2**(NUM_BITS-1)):
            list_of_nums = [(i,NUM_BITS),(0,NUM_BITS+1)]
            func_input = bits_from_nums(*list_of_nums)
            func_output = getattr(cc,"decrement{}".format(NUM_BITS))(*func_input)
            conv = nums_from_bits(func_output, list_of_nums)
            self.assertEqual(i-1,conv[0])
            self.assertEqual(0,conv[1])

class TestCmb(ut.TestCase):
    def test_no(self):
        for i,j in ((a,b) for a in range(2**NUM_BITS) for b in range(2**NUM_BITS)):
            if i+j>=2**NUM_BITS:
                continue
            list_of_nums = [(0,1),(i,NUM_BITS),(0,1),(j,NUM_BITS)]
            func_input = bits_from_nums(*list_of_nums)
            func_output = getattr(cc,"cmb{}".format(NUM_BITS))(*func_input)
            conv = nums_from_bits(func_output, list_of_nums)
            self.assertEqual(0,conv[0])

    def test_yes(self):
        for i,j in ((a,b) for a in range(2**NUM_BITS) for b in range(2**NUM_BITS)):
            if i+j<2**NUM_BITS:
                continue
            list_of_nums = [(0,1),(i,NUM_BITS),(0,1),(j,NUM_BITS)]
            func_input = bits_from_nums(*list_of_nums)
            func_output = getattr(cc,"cmb{}".format(NUM_BITS))(*func_input)
            conv = nums_from_bits(func_output, list_of_nums)
            self.assertEqual(1,conv[0])

class TestCmpge(ut.TestCase):
    def test_greater_equal(self):
        for i,j in ((a,b) for a in range(2**NUM_BITS) for b in range(2**NUM_BITS)):
            # want only j >= i
            if i>j:
                continue
            list_of_nums = [(i,NUM_BITS),(j,NUM_BITS),(0,1),(0,NUM_BITS+1)]
            func_input = bits_from_nums(*list_of_nums)
            func_output = getattr(cc,"cmpge{}".format(NUM_BITS))(*func_input)
            conv = nums_from_bits(func_output, list_of_nums)
            self.assertEqual(1,conv[2])

    def test_less_then(self):
        for i,j in ((a,b) for a in range(2**NUM_BITS) for b in range(2**NUM_BITS)):
            if i<=j:
                continue
            list_of_nums = [(i,NUM_BITS),(j,NUM_BITS),(0,1),(0,NUM_BITS+1)]
            func_input = bits_from_nums(*list_of_nums)
            func_output = getattr(cc,"cmpge{}".format(NUM_BITS))(*func_input)
            conv = nums_from_bits(func_output, list_of_nums)
            self.assertEqual(0,conv[2])


class TestCAdd(ut.TestCase):
    def test_enabled(self):
        for i,j in ((a,b) for a in range(2**NUM_BITS) for b in range(2**NUM_BITS)):
            if i+j>=2**NUM_BITS:
                continue
            list_of_nums = [(i,NUM_BITS),(0,1),(j,NUM_BITS),(1,1)]
            func_input = bits_from_nums(*list_of_nums)
            func_output = getattr(cc,"cadd{}".format(NUM_BITS))(*func_input)
            conv = nums_from_bits(func_output, list_of_nums)
            self.assertEqual(i+j,conv[0])

    def test_disabled(self):
        for i,j in ((a,b) for a in range(2**NUM_BITS) for b in range(2**NUM_BITS)):
            if i+j>=2**NUM_BITS:
                continue
            list_of_nums = [(i,NUM_BITS),(0,1),(j,NUM_BITS),(0,1)]
            func_input = bits_from_nums(*list_of_nums)
            func_output = getattr(cc,"cadd{}".format(NUM_BITS))(*func_input)
            conv = nums_from_bits(func_output, list_of_nums)
            self.assertEqual(i,conv[0])

class TestCSub(ut.TestCase):
    def test_enabled(self):
        for i,j in ((a,b) for a in range(2**NUM_BITS) for b in range(2**NUM_BITS)):
            if i<j:
                continue
            list_of_nums = [(i,NUM_BITS),(j,NUM_BITS),(0,NUM_BITS+1),(1,1)]
            func_input = bits_from_nums(*list_of_nums)
            func_output = getattr(cc,"csub{}".format(NUM_BITS))(*func_input)
            conv = nums_from_bits(func_output, list_of_nums)
            self.assertEqual(i-j,conv[0])

    def test_disabled(self):
        for i,j in ((a,b) for a in range(2**NUM_BITS) for b in range(2**NUM_BITS)):
            if i<j:
                continue
            list_of_nums = [(i,NUM_BITS),(j,NUM_BITS),(0,NUM_BITS+1),(0,1)]
            func_input = bits_from_nums(*list_of_nums)
            func_output = getattr(cc,"csub{}".format(NUM_BITS))(*func_input)
            conv = nums_from_bits(func_output, list_of_nums)
            self.assertEqual(i,conv[0])


class TestRMod(ut.TestCase):
    def test_mod2(self):
        for i in range(4):
            list_of_nums = [(2,NUM_BITS),(i,NUM_BITS),(0,1),(0,NUM_BITS+1)]
            func_input = bits_from_nums(*list_of_nums)
            func_output = getattr(cc,"rmod{}".format(NUM_BITS))(*func_input)
            conv = nums_from_bits(func_output, list_of_nums)
            self.assertEqual(i % 2,conv[1])

    def test_mod3(self):
        for i in range(6):
            list_of_nums = [(3,NUM_BITS),(i,NUM_BITS),(0,1),(0,NUM_BITS+1)]
            func_input = bits_from_nums(*list_of_nums)
            func_output = getattr(cc,"rmod{}".format(NUM_BITS))(*func_input)
            conv = nums_from_bits(func_output, list_of_nums)
            self.assertEqual(i % 3,conv[1])

class TestDoubleMod(ut.TestCase):
    def test_all_pairs(self):
        for n in range(2,2**(NUM_BITS-1)):
            for i in range(2**(NUM_BITS-1)):
                if i>=n:
                    continue
                list_of_nums = [(i,NUM_BITS),(n,NUM_BITS),(0,1),(0,NUM_BITS+1)]
                func_input = bits_from_nums(*list_of_nums)
                func_output = getattr(cc,"doublemod{}".format(NUM_BITS))(*func_input)
                conv = nums_from_bits(func_output, list_of_nums)
                self.assertEqual( (2*i) % n,conv[0])

class TestCAddMod(ut.TestCase):
    def test_all_combs_enabled(self):
        for n in range(3,2**(NUM_BITS-1)):
            # b is anything
            # a will never be zero, or we will have already found a factor of N
            for i,j in [(b,a) for b in range(0,2**(NUM_BITS-1)-1) for a in range(1,2**(NUM_BITS-1)-1)]:
                if i>=n or j>=n:
                    continue
                list_of_nums = [(i,NUM_BITS),(j,NUM_BITS),(n,NUM_BITS),(0,NUM_BITS+1),(0,1),(1,1)]
                func_input = bits_from_nums(*list_of_nums)
                func_output = getattr(cc,"caddmod{}".format(NUM_BITS))(*func_input)
                conv = nums_from_bits(func_output, list_of_nums)
                self.assertEqual( (i+j) % n,conv[0])
                self.assertEqual(0,conv[4])
    def test_all_combs_disabled(self):
        for n in range(3,2**(NUM_BITS-1)):
            # a will never be zero
            for i,j in [(b,a) for b in range(0,2**(NUM_BITS-1)-1) for a in range(1,2**(NUM_BITS-1)-1)]:
                if i>=n or j>=n:
                    continue
                list_of_nums = [(i,NUM_BITS),(j,NUM_BITS),(n,NUM_BITS),(0,NUM_BITS+1),(0,1),(0,1)]
                func_input = bits_from_nums(*list_of_nums)
                func_output = getattr(cc,"caddmod{}".format(NUM_BITS))(*func_input)
                conv = nums_from_bits(func_output, list_of_nums)
                self.assertEqual( i%n, conv[0])
                self.assertEqual(0,conv[4])


class TestMultBStage(ut.TestCase):
    def test_all_pairs_enabled(self):
        for n in range(3,2**(NUM_BITS-1)-1):
            for i,j in [(b,a) for b in range(0,2**(NUM_BITS-1)-1) for a in range(1,2**(NUM_BITS-1)-1)]:
                if i>=n or j>=n:
                    continue
                list_of_nums = [(i,NUM_BITS),(j,NUM_BITS),(n,NUM_BITS),(0,NUM_BITS+2),(0,1),(1,1)]
                func_input = bits_from_nums(*list_of_nums)
                func_output = getattr(cc,"multbstage{}".format(NUM_BITS))(*func_input)
                conv = nums_from_bits(func_output, list_of_nums)
                self.assertEqual( (i+j) % n,conv[0])
                self.assertEqual( (2*j) % n,conv[1])
                self.assertEqual( n, conv[2])
                self.assertEqual( 0, conv[3])
                self.assertEqual( 1, conv[5])
    def test_all_pairs_disabled(self):
        for n in range(3,2**(NUM_BITS-1)-1):
            for i,j in [(b,a) for b in range(0,2**(NUM_BITS-1)-1) for a in range(1,2**(NUM_BITS-1)-1)]:
                if i>=n or j>=n:
                    continue
                list_of_nums = [(i,NUM_BITS),(j,NUM_BITS),(n,NUM_BITS),(0,NUM_BITS+2),(0,1),(0,1)]
                func_input = bits_from_nums(*list_of_nums)
                func_output = getattr(cc,"multbstage{}".format(NUM_BITS))(*func_input)
                conv = nums_from_bits(func_output, list_of_nums)
                self.assertEqual( (i) % n,conv[0])
                self.assertEqual( (2*j) % n,conv[1])
                self.assertEqual( n, conv[2])
                self.assertEqual( 0, conv[3])
                self.assertEqual( 0, conv[5])


class TestMultBChain(ut.TestCase):
    def test_all_vals(self):
        for n in range(3,2**(NUM_BITS-1)):
            if n%2 == 0:
                continue
            for a,val in [(i,j) for i in range(1,n) for j in range(0,n)]:
                list_of_nums = [(0,NUM_BITS),(a,NUM_BITS),(n,NUM_BITS),(0,NUM_BITS+2),(0,NUM_BITS),(val,NUM_BITS)]
                func_input = bits_from_nums(*list_of_nums)
                func_output = getattr(cc,"multbchain{}".format(NUM_BITS))(*func_input)
                conv = nums_from_bits(func_output, list_of_nums)
                self.assertEqual( (a*val) % n,conv[0])
                self.assertEqual( (a*2**NUM_BITS) % n,conv[1])
                self.assertEqual( n, conv[2])
                self.assertEqual( 0, conv[3])
                self.assertEqual( val, conv[5])

class TestSpecificMultBChain(ut.TestCase):
    def test_all_x(self):
        for val in range(CONST_N):
            list_of_nums = [(0,NUM_BITS),
                            (CONST_A,NUM_BITS),
                            (CONST_N,NUM_BITS),
                            (0,NUM_BITS+3),
                            (val,NUM_BITS),
                           ]
            func_input = bits_from_nums(*list_of_nums)
            func_output = getattr(cc,"specificmultbchain{nb}_{A}_{N}".format(
                                    nb=NUM_BITS,
                                    A=CONST_A,N=CONST_N)
                                    )(*func_input)
            conv = nums_from_bits(func_output, list_of_nums)
            self.assertEqual( (CONST_A*val) % CONST_N,conv[0])
            self.assertEqual( (CONST_A*2**NUM_BITS) % CONST_N,conv[1])
            self.assertEqual( CONST_N, conv[2])
            self.assertEqual( 0, conv[3])
            self.assertEqual( val, conv[4])
    def test_all_x_inv(self):
        A_inv = modular_inverse(CONST_A,CONST_N)
        for val in range(CONST_N):
            list_of_nums = [(0,NUM_BITS),
                            (A_inv,NUM_BITS),
                            (CONST_N,NUM_BITS),
                            (0,NUM_BITS+3),
                            (val,NUM_BITS),
                           ]
            func_input = bits_from_nums(*list_of_nums)
            func_output = getattr(cc,"specificmultbchain{nb}_{A_inv}_{N}".format(
                                    nb=NUM_BITS,
                                    A_inv=A_inv,N=CONST_N)
                                    )(*func_input)
            conv = nums_from_bits(func_output, list_of_nums)
            self.assertEqual( (A_inv*val) % CONST_N,conv[0])
            self.assertEqual( (A_inv*2**NUM_BITS) % CONST_N,conv[1])
            self.assertEqual( CONST_N, conv[2])
            self.assertEqual( 0, conv[3])
            self.assertEqual( val, conv[4])

class TestToFromModularInverse(ut.TestCase):
    def test_to_modular_inverse(self):
        A_inv = modular_inverse(CONST_A,CONST_N)
        list_of_nums=[( (CONST_A * 2**NUM_BITS) % CONST_N, NUM_BITS)]
        func_input = bits_from_nums(*list_of_nums)
        func_output = getattr(cc,"toAmodularinv{nb}_{A}_{N}".format(
                                nb=NUM_BITS,
                                A=CONST_A,N=CONST_N)
                                )(*func_input)

        conv = nums_from_bits(func_output, list_of_nums)
        self.assertEqual( A_inv, conv[0])

    def test_from_modular_inverse(self):
        A_inv = modular_inverse(CONST_A,CONST_N)
        list_of_nums=[( (A_inv * 2**NUM_BITS) % CONST_N, NUM_BITS)]
        func_input = bits_from_nums(*list_of_nums)
        func_output = getattr(cc,"backtoA{nb}_{A}_{N}".format(
                                nb=NUM_BITS,
                                A=CONST_A,N=CONST_N)
                                )(*func_input)
        conv = nums_from_bits(func_output, list_of_nums)
        self.assertEqual( CONST_A, conv[0])

class TestModularMult(ut.TestCase):
    def test_all_vals(self):
        A_inv = modular_inverse(CONST_A,CONST_N)
        for x in range(1,2**(NUM_BITS-1)-1):
            list_of_nums=[(0,NUM_BITS),(CONST_A,NUM_BITS),(CONST_N,NUM_BITS),(0,NUM_BITS+3),(x,NUM_BITS)]
            func_input = bits_from_nums(*list_of_nums)
            func_output = getattr(cc,"modularmult{nb}_{A}_{N}".format(
                                    nb=NUM_BITS,
                                    A=CONST_A,N=CONST_N)
                                    )(*func_input)
            conv = nums_from_bits(func_output, list_of_nums)
            self.assertEqual(0,conv[0])
            self.assertEqual(CONST_A,conv[1])
            self.assertEqual(CONST_N,conv[2])
            self.assertEqual(0,conv[3])
            self.assertEqual((CONST_A*x)%CONST_N,conv[4])

class TestCModularMult(ut.TestCase):
    def test_all_vals_enabled(self):
        A_inv = modular_inverse(CONST_A,CONST_N)
        for x in range(1,2**(NUM_BITS-1)-1):
            list_of_nums=[(0,NUM_BITS),(CONST_A,NUM_BITS),(CONST_N,NUM_BITS),(0,NUM_BITS+3),(x,NUM_BITS),(1,NUM_BITS),(1,1)]
            func_input = bits_from_nums(*list_of_nums)
            func_output = getattr(cc,"cmodularmult{nb}_{A}_{N}".format(
                                    nb=NUM_BITS,
                                    A=CONST_A,N=CONST_N)
                                    )(*func_input)
            conv = nums_from_bits(func_output, list_of_nums)
            self.assertEqual(0,conv[0])
            self.assertEqual(CONST_A,conv[1])
            self.assertEqual(CONST_N,conv[2])
            self.assertEqual(0,conv[3])
            self.assertEqual((CONST_A*x)%CONST_N,conv[4])
            self.assertEqual(1,conv[5])
            self.assertEqual(1,conv[6])

    def test_all_vals_disabled(self):
        A_inv = modular_inverse(CONST_A,CONST_N)
        for x in range(1,2**(NUM_BITS-1)-1):
            list_of_nums=[(0,NUM_BITS),(CONST_A,NUM_BITS),(CONST_N,NUM_BITS),(0,NUM_BITS+3),(x,NUM_BITS),(1,NUM_BITS),(0,1)]
            func_input = bits_from_nums(*list_of_nums)
            func_output = getattr(cc,"cmodularmult{nb}_{A}_{N}".format(
                                    nb=NUM_BITS,
                                    A=CONST_A,N=CONST_N)
                                    )(*func_input)
            conv = nums_from_bits(func_output, list_of_nums)
            self.assertEqual(0,conv[0])
            self.assertEqual(CONST_A,conv[1])
            self.assertEqual(CONST_N,conv[2])
            self.assertEqual(0,conv[3])
            self.assertEqual(x%CONST_N,conv[4])
            self.assertEqual(1,conv[5])
            self.assertEqual(0,conv[6])

if __name__=='__main__':
    ut.main()


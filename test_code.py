import classical_code as cc
import unittest as ut
import numpy as np

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


class TestAdd(ut.TestCase):
    def test_with_overflow(self):
        for i in range(4):
            for j in range(4):
                if i+j<=3:
                    break
                list_of_nums = [(i,3),(0,1),(j,3)]
                func_input = bits_from_nums(*list_of_nums)
                func_output = cc.add3(*func_input)
                conv = nums_from_bits(func_output, list_of_nums)
                self.assertEqual(i+j,conv[0])

    def test_no_overflow(self):
        for i in range(4):
            for j in range(4):
                if i+j>3:
                    break
                list_of_nums = [(i,3),(0,1),(j,3)]
                func_input = bits_from_nums(*list_of_nums)
                func_output = cc.add3(*func_input)
                conv = nums_from_bits(func_output, list_of_nums)
                self.assertEqual(i+j,conv[0])

class TestIncrementDecrement(ut.TestCase):
    def test_increment(self):
        for i in range(4):
            list_of_nums = [(i,3),(0,4)]
            func_input = bits_from_nums(*list_of_nums)
            func_output = cc.increment3(*func_input)
            conv = nums_from_bits(func_output, list_of_nums)
            self.assertEqual(i+1,conv[0])
            self.assertEqual(0,conv[1])

    def test_decrement(self):
        for i in range(1,4):
            list_of_nums = [(i,3),(0,4)]
            func_input = bits_from_nums(*list_of_nums)
            func_output = cc.decrement3(*func_input)
            conv = nums_from_bits(func_output, list_of_nums)
            self.assertEqual(i-1,conv[0])
            self.assertEqual(0,conv[1])

class TestCmb(ut.TestCase):
    def test_no(self):
        for i,j in ((a,b) for a in range(8) for b in range(8)):
            if i+j>=8:
                continue
            list_of_nums = [(0,1),(i,3),(0,1),(j,3)]
            func_input = bits_from_nums(*list_of_nums)
            func_output = cc.cmb3(*func_input)
            conv = nums_from_bits(func_output, list_of_nums)
            self.assertEqual(0,conv[0])

    def test_yes(self):
        for i,j in ((a,b) for a in range(8) for b in range(8)):
            if i+j<8:
                continue
            list_of_nums = [(0,1),(i,3),(0,1),(j,3)]
            func_input = bits_from_nums(*list_of_nums)
            func_output = cc.cmb3(*func_input)
            conv = nums_from_bits(func_output, list_of_nums)
            self.assertEqual(1,conv[0])

class TestCmpge(ut.TestCase):
    def test_greater_equal(self):
        for i,j in ((a,b) for a in range(8) for b in range(8)):
            # want only j >= i
            if i>j:
                continue
            list_of_nums = [(i,3),(j,3),(0,1),(0,4)]
            func_input = bits_from_nums(*list_of_nums)
            func_output = cc.cmpge3(*func_input)
            conv = nums_from_bits(func_output, list_of_nums)
            self.assertEqual(1,conv[2])

    def test_less_then(self):
        for i,j in ((a,b) for a in range(8) for b in range(8)):
            if i<=j:
                continue
            list_of_nums = [(i,3),(j,3),(0,1),(0,4)]
            func_input = bits_from_nums(*list_of_nums)
            func_output = cc.cmpge3(*func_input)
            conv = nums_from_bits(func_output, list_of_nums)
            self.assertEqual(0,conv[2])


class TestCAdd(ut.TestCase):
    def test_enabled(self):
        for i,j in ((a,b) for a in range(8) for b in range(8)):
            if i+j>=8:
                continue
            list_of_nums = [(i,3),(0,1),(j,3),(1,1)]
            func_input = bits_from_nums(*list_of_nums)
            func_output = cc.cadd3(*func_input)
            conv = nums_from_bits(func_output, list_of_nums)
            self.assertEqual(i+j,conv[0])

    def test_disabled(self):
        for i,j in ((a,b) for a in range(8) for b in range(8)):
            if i+j>=8:
                continue
            list_of_nums = [(i,3),(0,1),(j,3),(0,1)]
            func_input = bits_from_nums(*list_of_nums)
            func_output = cc.cadd3(*func_input)
            conv = nums_from_bits(func_output, list_of_nums)
            self.assertEqual(i,conv[0])

class TestCSub(ut.TestCase):
    def test_enabled(self):
        for i,j in ((a,b) for a in range(8) for b in range(8)):
            if i<j:
                continue
            list_of_nums = [(i,3),(j,3),(0,4),(1,1)]
            func_input = bits_from_nums(*list_of_nums)
            func_output = cc.csub3(*func_input)
            conv = nums_from_bits(func_output, list_of_nums)
            self.assertEqual(i-j,conv[0])

    def test_disabled(self):
        for i,j in ((a,b) for a in range(8) for b in range(8)):
            if i<j:
                continue
            list_of_nums = [(i,3),(j,3),(0,4),(0,1)]
            func_input = bits_from_nums(*list_of_nums)
            func_output = cc.csub3(*func_input)
            conv = nums_from_bits(func_output, list_of_nums)
            self.assertEqual(i,conv[0])


class TestRMod(ut.TestCase):
    def test_mod2(self):
        for i in range(4):
            list_of_nums = [(2,3),(i,3),(0,1),(0,4)]
            func_input = bits_from_nums(*list_of_nums)
            func_output = cc.rmod3(*func_input)
            conv = nums_from_bits(func_output, list_of_nums)
            self.assertEqual(i % 2,conv[1])

    def test_mod3(self):
        for i in range(6):
            list_of_nums = [(3,3),(i,3),(0,1),(0,4)]
            func_input = bits_from_nums(*list_of_nums)
            func_output = cc.rmod3(*func_input)
            conv = nums_from_bits(func_output, list_of_nums)
            self.assertEqual(i % 3,conv[1])

class TestDoubleMod(ut.TestCase):
    def test_all_pairs(self):
        for n in range(2,4):
            for i in range(4):
                if i>=n:
                    continue
                list_of_nums = [(i,3),(n,3),(0,1),(0,4)]
                func_input = bits_from_nums(*list_of_nums)
                func_output = cc.doublemod3(*func_input)
                conv = nums_from_bits(func_output, list_of_nums)
                self.assertEqual( (2*i) % n,conv[0])

class TestCAddMod(ut.TestCase):
    def test_all_combs_enabled(self):
        for n in range(3,4):
            for i,j in [(a,b) for a in range(0,4) for b in range(0,4)]:
                if i+j>=2*n:
                    continue
                list_of_nums = [(i,3),(j,3),(n,3),(0,4),(0,1),(1,1)]
                func_input = bits_from_nums(*list_of_nums)
                func_output = cc.caddmod3(*func_input)
                conv = nums_from_bits(func_output, list_of_nums)
                print(i,j,conv)
                self.assertEqual( (i+j) % n,conv[0])
                #self.assertEqual(0,conv[4])
    def test_all_combs_disabled(self):
        for n in range(3,4):
            for i,j in [(a,b) for a in range(0,4) for b in range(0,4)]:
                if i+j>=2*n:
                    continue
                list_of_nums = [(i,3),(j,3),(n,3),(0,4),(0,1),(0,1)]
                func_input = bits_from_nums(*list_of_nums)
                func_output = cc.caddmod3(*func_input)
                conv = nums_from_bits(func_output, list_of_nums)
                print(i,j,conv)
                self.assertEqual( i%n, conv[0])
                #self.assertEqual(0,conv[4])





if __name__=='__main__':
    ut.main()


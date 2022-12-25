from collections import defaultdict
import pickle as pickle
import os

class Quran:
    '''
        sindex: sure index
        sid: sure id (1..114)
    '''

    def __init__(self, data_folder = 'data'):
        fn = data_folder + '/morphology_0.62.txt'
        fn_romantoarabic = data_folder + '/roman2arabic.pickle'
        fn_cache = data_folder + '/cache.pickle'

        if os.path.isfile(fn_cache):
            # print('cache loaded ...')
            all_data = pickle.load(open(fn_cache, "rb"))

            self.data_word_roman, self.data_root_roman = all_data['data_word_roman'], all_data['data_root_roman']
            self.info_count_sure, self.info_count_aye, self.info_count_token = all_data['info_count_sure'], all_data['info_count_aye'], all_data['info_count_token']
            self.roman2arabic = all_data['roman2arabic']

        else:
            self.data_word_roman, self.data_root_roman = {}, {}
            self.info_count_sure, self.info_count_aye, self.info_count_token = 0, {}, {}
            with open(fn) as f:
                for l in f:
                    if len(l) == 0 or l.startswith('LOCATION'): continue
                    l = l.strip()
                    x = l.split('\t')
                    loc = [int(i)-1 for i in x[0][1:-1].split(':')]
                    loc_pt = Quran.loc_pack_tocken(loc)

                    self.info_count_aye[loc[0]] = loc[1] + 1
                    self.info_count_sure = loc[0] + 1
                    self.info_count_token[Quran.loc_pack_tocken((loc[0], loc[1], 0))] = loc[2] + 1
                    
                    #TEST:
                    test_loc = Quran.loc_unpack_tocken(loc_pt)
                    # print(test_loc, loc[0:3], loc_pt)
                    assert test_loc == tuple(loc[0:3])
                    #TEST:~

                    if loc_pt not in self.data_word_roman:
                        self.data_word_roman[loc_pt] = ''
                    self.data_word_roman[loc_pt] += x[1]

                    props = [s.split(':') for s in x[4].split('|')]
                    if 'ROOT' in [s[0] for s in props]:
                        # print('set root for ', loc, loc_pt, props[[s[0] for s in props].index('ROOT')][1])
                        self.data_root_roman[loc_pt] = props[[s[0] for s in props].index('ROOT')][1]
            self.roman2arabic = pickle.load(open(fn_romantoarabic, "rb"))

            all_data = {'data_word_roman': self.data_word_roman, 'data_root_roman': self.data_root_roman, 'info_count_sure': self.info_count_sure, 'info_count_aye': self.info_count_aye, 'info_count_token': self.info_count_token, 'roman2arabic' : self.roman2arabic}
            pickle.dump(all_data, open(fn_cache, 'wb'))

    def deroman(self, s):
        return ''.join([self.roman2arabic[e1] for e1 in s if e1 in self.roman2arabic])

    @staticmethod
    def loc_pack_tocken(loc):
        'returns an int from a 4-ary tuple, only considers first three ones'
        #loc is zero-based
        # print(loc)
        return loc[2] + 200 * (loc[1] + 300 * loc[0])

    @staticmethod
    def loc_unpack_tocken(p):
        return (p // 200 // 300, (p // 200) % 300, p % 200)

    def __getitem__(self, sindex: int):
        return Sure(self, sindex)

    def root(self, sindex, aindex, tindex):
        rr = self.root_roman(sindex, aindex, tindex)
        if rr is None: return None
        return self.deroman(rr)

    def root_roman(self, sindex, aindex, tindex):
        ploc = Quran.loc_pack_tocken((sindex, aindex, tindex))
        if ploc not in self.data_root_roman:
            return None
        return self.data_root_roman[ploc]
    
    def token(self, sindex, aindex, tindex):
        return self.deroman(self.token_roman(sindex, aindex, tindex))

    def token_roman(self, sindex, aindex, tindex):
        return self.data_word_roman[Quran.loc_pack_tocken((sindex, aindex, tindex))]

    def aye(self, sindex, aindex):
        return ' '.join([self.token(sindex, aindex, tindex) for tindex in range(self.token_count(sindex, aindex))])

    def sure(self, sindex, print_besmellah = False):
        s = ''
        if print_besmellah:
            s += self.aye(0, 0) + ' '
        return s + ' '.join([self.aye(sindex, aindex) + ' (' + str(aindex+1) + ')' for aindex in range(self.aye_count(sindex)) ])

    def sure_count(self):
        return self.info_count_sure
    
    def aye_count(self, sindex: int):
        return self.info_count_aye[sindex]
    
    def token_count(self, sindex: int, aindex: int):
        return self.info_count_token[Quran.loc_pack_tocken((sindex, aindex, 0))]

    def items(self):
        return SureIterator(self)

    def search_root_roman(self, root_roman):
        #TODO: make it faster
        for l, r in self.data_root_roman.items():
            if r == root_roman:
                p = Quran.loc_unpack_tocken(l)
                yield Token(self, p[0], p[1], p[2])

    def search_root(self, root):
        #TODO: make it faster
        for l, r in self.data_root_roman.items():
            if self.deroman(r) == root:
                p = Quran.loc_unpack_tocken(l)
                yield Token(self, p[0], p[1], p[2])

class Token:
    def __init__(self, quran, sindex: int, aindex: int, tindex: int):
        self.quran = quran
        self.sindex = sindex
        self.aindex = aindex
        self.tindex = tindex
    
    def root(self):
        return self.quran.root(self.sindex, self.aindex, self.tindex)

    def root_roman(self):
        return self.quran.root_roman(self.sindex, self.aindex, self.tindex)

    def token(self):
        return self.quran.token(self.sindex, self.aindex, self.tindex)

    def token_roman(self):
        return self.quran.token_roman(self.sindex, self.aindex, self.tindex)

class Aye: 
    def __init__(self, quran, sindex: int, aindex: int):
        self.quran = quran
        self.sindex = sindex
        self.aindex = aindex
    
    def __getitem__(self, tindex: int):
        return Token(self.quran, self.sindex, self.aindex, tindex)

    def items(self):
        return TokenIterator(self.quran, self.sindex, self.aindex)


class Sure:
    def __init__(self, quran, sindex: int):
        self.quran = quran
        self.sindex = sindex

    def __getitem__(self, aindex: int):
        return Aye(self.quran, self.sindex, aindex)

    def items(self):
        return AyeIterator(self.quran, self.sindex)

    def range(self, aindex_begin: int, aindex_end: int):
        return AyeIterator(self.quran, self.sindex, aindex_begin, aindex_end)



class TokenIterator:
    def __init__(self, quran, sindex: int, aindex: int):
        self.quran = quran
        self.sindex = sindex
        self.aindex = aindex

    def __iter__(self):
        self.tindex = 0
        return self

    def __next__(self):
        if self.tindex < self.quran.token_count(self.sindex, self.aindex):
            self.tindex += 1
            return Token(self.quran, self.sindex, self.aindex, self.tindex - 1)
        else:
            raise StopIteration

class AyeIterator:
    def __init__(self, quran, sindex: int, aindex_begin: int = 0, aindex_end: int = -1):
        self.quran = quran
        self.sindex = sindex
        self.aindex_begin = aindex_begin
        self.aindex_end = aindex_end if aindex_end != -1 else self.quran.info_count_aye[self.sindex]

    def __iter__(self):
        self.aindex = self.aindex_begin 
        return self

    def __next__(self):
        if self.aindex < self.aindex_end:
            self.aindex += 1
            return Aye(self.quran, self.sindex, self.aindex - 1)
        else:
            raise StopIteration

class SureIterator:
    def __init__(self, quran):
        self.quran = quran
    
    def __iter__(self):
        self.sindex = 0
        return self

    def __next__(self):
        if self.sindex < self.quran.info_count_sure:
            self.sindex += 1
            return Sure(self.quran, self.sindex - 1)
        else:
            raise StopIteration

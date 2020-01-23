#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan  3 13:33:02 2020

@author: hh
"""
import pandas as pd
from konlpy.tag import Kkma, Okt, Komoran, Hannanum, Mecab
from collections import OrderedDict, defaultdict
import re

class ModelNotFittedError(Exception):
    def __init__(self):
        super().__init__('Model doesn\'t fitted.')
        
class HashTagging:
    
    def __init__(self, title_to_tag=False, theta=0.01):
        '''
        parameter:
            title_to_tag : use tagging title like <hello> or 'hello' and so on
            theta : this is parameter of fitting documents in function __fitted_get_r()
            
        ----------------------
        class global value:
            is_fitted : this value true if hashtagging is fit by documents
            fitted_title : this value saved trained documents
            fitted_num : this value saved trained documtents num
            lrgraph : this value saved graph of l-r
                    lr explain is in https://datacookbook.kr/attachment/cfile9.uf@9989C53359B55A0D16393A.pdf
            konlpy_dict : this dict is list of konlpy tagger
        '''
        self.__title_to_tag = title_to_tag
        self.__theta = theta
        self.__is_fitted= False
        self.fitted_title = pd.DataFrame(columns=['fitted_title'])
        self.fitted_num = 0
        self.__lrgraph = defaultdict(lambda: defaultdict(lambda: 0))
        self.__konlpy_dict = self.__get_konlpy_dict()
        
    def __title_tagging(self,text):
        '''
        parameter:
            text : String
        return:
            list of matching norm expression
        '''
        return re.findall('<[a-zA-Z0-9가-힣 .?!]+>|\"[a-zA-Z0-9가-힣 .?!]+\"|\[[a-zA-Z0-9가-힣 .?!]+\]|\'[a-zA-Z0-9가-힣 .?!]+\'|\{[a-zA-Z0-9가-힣 .?!]+\}', text)
    
    def __clean_normalized_text(self,text):
        '''
        parameter :
            text : String
        return:
            String of remove norm expression
        '''
        text = text.strip('\n').replace('\xa0',' ')
        cleanText = re.sub('[,#/\?:^$.@*\"\'~!%_&=+()\[\]{}<>-]',' ',text)
        return cleanText.lower()
    
    def __get_r(self,L):
        '''
        parameter :
            L : String this is L of lrgraph
        return:
            list of sorted lrgraph[L] items 
        '''
        return sorted(self.__lrgraph[L].items(), key=lambda x: -x[1])
    
    def __get_konlpy_dict(self):
        '''
        return:
            dict of Konlpy tagger
        '''
        kkma, okt, komoran, hannanum, mecab = Kkma(), Okt(), Komoran(), Hannanum(), Mecab()
        return {'kkma':kkma, 'okt':okt, 'komoran':komoran, 'hannanum':hannanum, 'mecab':mecab}
    
    def get_english_tag(self,text):
        '''
        parameter :
            text : String
        return:
            List of english by norm expression
        '''
        return list(map(lambda x : x.lower(), re.findall('[a-zA-Z]{2,}',text)))
    
    def __word_similarity(self,word1, word2):
        '''
        parameter :
            word<1,2> : String
        return:
            float by similarity of word by frequency of word[i]
        '''
        word1_set= set(word1)
        word2_set = set(word2)
        return len(word1_set.intersection(word2_set)) / len(word1_set.union(word2_set))
    
    def fit_data(self, docs):
        '''
        parameter :
            docs : docs is training set
        return:
            None
        ---------------
        This function make lrgraph and if fit_data ended then class value
        is_fitted = True
        '''
        docs_clean = []
        for doc in docs:
            if doc in docs_clean:
                continue
            self.fitted_title.loc[self.fitted_num] = doc
            self.fitted_num += 1
            doc = self.__clean_normalized_text(doc)
            for w in doc.split():
                n = len(w)
                for i in range(1, n+1):
                    try:
                        self.__lrgraph[w[:i]][w[i:][0]] += 1
                    except IndexError:
                        self.__lrgraph[w[:i]][w[i:]] += 1
        
        self.__is_fitted = True
    
    def __fitted_get_r(self, doc):
        '''
        parameter :
            doc : String
        return:
            noun_ls : List of nouns in doc
        ---------------------
        If model was fitted then user can use this function
        This function get nouns by lrgraph
        If model wasn't fitted then this function isn't useful.
        '''
        if not self.__is_fitted:
            raise ModelNotFittedError
        noun_ls=[]
        for index, word in enumerate(doc.split()):
            n = len(word)
            if n < 2 and word:
                continue
            word_probability = OrderedDict()
            for i in range(1, n+1):
                w = word[:i]
                get_r = self.__get_r(w)
                count = sum([f for _, f in get_r])
                for R, freq in get_r:
                    now_word = w+R
                    if now_word == word[:i+1] and len(now_word) > 1:
                        try:
                            word_probability[now_word] **= (freq/count)
                        except KeyError:
                            word_probability[now_word] = (freq/count)
            prev_noun, prev_prob = '', -1
            for noun, prob in word_probability.items():
                if (prob + self.__theta) < prev_prob:
                    break
                prev_noun, prev_prob = noun, prob
            noun_ls.append((prev_noun, index))
        return noun_ls 
    
    def __konlpy_nouns(self,tagger, doc):
        '''
        parameter :
            tagger : this is konlpy tagger
            doc : document
        return:
            list of nouns
        '''
        return  [(tagger.nouns(word), i) for i, word in enumerate(doc.split())]

    
    
    def get_tag_probability(self, doc):
        '''
        parameter :
            doc : String(document)
        return:
            defaultdict of probability of nouns
        '''
        nouns_cases = {}
        hashtagging_prob = defaultdict(lambda: defaultdict(lambda: 0))

            
        if doc not in self.fitted_title.values:
            print('Input title doesn\'t in this model.\nIt may not be accurate.')
            
        if self.__title_to_tag:
            for title in self.__title_tagging(doc):
                doc = doc.replace(title, ' ')
                hashtagging_prob['foreign'][title[1:-1]] += 1
        
        for english in self.get_english_tag(doc):
            doc = doc.replace(english, ' ')
            hashtagging_prob['foreign'][english] += 1
                
        doc = re.sub('[^가-힣0-9A-Za-z ]+','',self.__clean_normalized_text(doc))
        
        if self.__is_fitted:
            nouns_cases['lrgraph'] = self.__fitted_get_r(doc)
            
        for tagger, tagger_nouns in self.__konlpy_dict.items():
            nouns_cases['{}_noun'.format(tagger)] = self.__konlpy_nouns(tagger_nouns, doc)
        
        print('Calculating probability...')
        for tagger, nouns in nouns_cases.items():
            if 'kkma' in tagger:
                for tup in nouns_cases[tagger]:
                    if type(tup) is str:
                        hashtagging_prob['foreign'][tup] += 1
                        continue
                    
                    noun_ls, index = tup
                    if len(noun_ls) == 0:
                        hashtagging_prob[str(index)]['not_noun'] += 1
                        continue
                    for noun in noun_ls:
                        hashtagging_prob[str(index)][noun] += 1

            elif 'lrgraph' in tagger:
                for tup in nouns_cases[tagger]:
                    if type(tup) is str:
                        hashtagging_prob['foreign'][tup] += 1
                        continue
                    noun, index = tup
                    hashtagging_prob[str(index)][noun] += 1
                    
            else:
                for tup in nouns_cases[tagger]:
                    if type(tup) is str:
                        hashtagging_prob['foreign'][tup] += 1
                        continue
                    noun_ls, index = tup
                    if len(noun_ls) == 0:
                        hashtagging_prob[str(index)]['not_noun'] += 1
                        continue
                    for i in range(1, len(noun_ls)+1):
                        hashtagging_prob[str(index)][''.join(noun_ls[:i])] += 1
                    
        for k, v in hashtagging_prob.items():
            if k == 'foreign':
                for k2, v2 in v.items():
                    hashtagging_prob[k][k2] = 1.0
                continue
            total = sum([f for _, f in v.items()])
            for word, freq in v.items():
                hashtagging_prob[k][word] /= total
#                if word != 'not_noun':
#                    try:
#                        hashtagging_prob[k][word] *= self.__word_similarity(doc.split()[int(k)], word)
#                    except IndexError:
#                        hashtagging_prob[k][word] = 0

        return hashtagging_prob
    def get_tags(self, doc):
        '''
        parameter :
            doc : String(document)
        return:
            List of tags
        '''
        tag_ls = []
        tag_prob = self.get_tag_probability(doc)
        for index, word_dict in tag_prob.items():
            word_prob = sorted([(word, prob) for word, prob in word_dict.items()], key= lambda x: -x[1])
            max_prob = word_prob[0][1]
            temp_ls = []
            for tup in word_prob:
                word, prob = tup
                if prob > 0.5 and word is 'not_noun':
                    temp_ls.append(word)
                    break
                if prob == max_prob and len(word) > 1:
                    temp_ls.append(word)
                
            if 'not_noun' not in temp_ls:
                for word in temp_ls:
                    if word not in tag_ls:
                        tag_ls.append(word)
    
        return tag_ls

import re
import urllib.request
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import csv
import requests
import nltk
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
import string
from word_forms.word_forms import get_word_forms
from bloomfilter import BloomFilter, ScalableBloomFilter, SizeGrowthRate
import argparse

#usage message
def msg():
    message='''You failed to provide required files.\nYou must provide it as input on command line'''
    return message

#argparse object
parser = argparse.ArgumentParser(usage=msg())
parser.add_argument("file",metavar="english.csv,custom.csv",nargs=2)
args = parser.parse_args()

# bloom filter object
custom = BloomFilter(size=10000000, fp_prob=1e-10)
common = BloomFilter(size=10000000, fp_prob=1e-10)

# to add all words
all_custom_words = set()
all_common_english_words = set()

count = 0
# 2
# 4
# function to extract words


def extract_word(url):
    # parsing html and getting clear text from it
    words_set = set()
    req = Request(str(url), headers={'User-Agent': 'Mozilla/5.0'})
    try:
        html = urlopen(req).read()
    #html = urllib.request.urlopen(str(url))
        soup = BeautifulSoup(html, features="lxml")
        data = soup.findAll(text=True)

        def visible(element):
            if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
                return False
            elif re.match('<!--.*-->', str(element.encode('utf-8'))):
                return False
            return True
        result = filter(visible, data)
        list_to_str = ' '.join([str(element) for element in list(result)])

    # sentence tokenizing the clear text
        sent = nltk.sent_tokenize(list_to_str)
    # operations to extract words
        for item in sent:
            tokens = nltk.word_tokenize(item)
        # removing punctuation
            table = str.maketrans('', '', string.punctuation)
            stripped = [word.translate(table) for word in tokens]
        # taking only alphabet
            words = [word for word in stripped if word.isalpha()]
            for word in words:
                word = ''.join([char for char in word if not char.isdigit()])
                # removing hexadecimal
                word = re.sub(r'[^\x00-\x7f]', r'', word)
                if len(word) >= 1:
                    words_set.add(str(word.casefold()))
                # to get different form of a word
                    word_form = get_word_forms(word)
                    for item in word_form.values():
                        for inner_item in item:
                            words_set.add(str(inner_item.casefold()))
        return words_set

    except:
        with open('unavailable_url.csv', 'a') as file:
            writer = csv.writer(file)
            writer.writerow([count])
            writer.writerow([url])
        return set("page " + str(count) + " not available")


# 1
# ENGLISH-DICTIONARY
# for getting url from csv file

fname = args.file[0]
with open(fname, 'rt')as urls:
    url = csv.reader(urls)
    for item in url:
        for data in item:
            count += 1
            print("parsing english dictionary web page "+str(count))
            # passing one url at a time from english.csv file
            all_common_english_words.update(extract_word(data))
# adding words in bloom filter object
for item in all_common_english_words:
    common.add(item)
# adding bloom filter object to file
with open("bloom_filter_english_dictionary.bin", "wb") as file_obj:
    common.save(file_obj)

# 3
# CUSTOM-DICTIONARY
# for getting url from csv file
fname = args.file[1]
with open(fname, 'rt')as urls:
    count = 0
    url = csv.reader(urls)
    for item in url:
        for data in item:
            count += 1
            print("parsing custom dictionary web page "+str(count))
            # passing one url at a time from custom.csv file
            all_custom_words.update(extract_word(data))
# adding words in bloom filter object
for item in all_custom_words:
    custom.add(item)
# adding bloom filter object to file
with open("bloom_filter_custom_dictionary.bin", "wb") as file_obj:
    custom.save(file_obj)

print("English and Custom dictionary is created")
#!/usr/bin/env python
# coding: utf-8

def convert_chars(string):
    '''
    Converts problematic characters. Usually, tend to be accented vowels.
    Takes the following parameters:

    string (str): a string where one or more characters raise a UnicodeEncodeError.

    Returns a modified string.
    '''

    if 'â\x80\x93' in string:
        string = string.replace('â\x80\x93', '-')
    if 'Ã¤' in string:
        string = string.replace('Ã¤', 'ä')
    if 'Ã¹' in string:
        string = string.replace('Ã¹', 'ù')
    if 'Å\x8d' in string:
        string = string.replace('Å\x8d', 'ō')
    if 'Ã\xa0' in string:
        string = string.replace('Ã\xa0', 'à')

    return string

#! /usr/bin/env pypy

import hashlib
from argparse import ArgumentParser
import random
import string
import re
import multiprocessing

letters = string.ascii_letters


MIN_LEN = 6
MAX_LEN = 12

NCORES = multiprocessing.cpu_count()

encodings = {'hex', 'string_escape'}

charset = {'letters': letters,
            'lower' : string.lowercase,
            'upper' : string.uppercase,
            'digits': string.digits,
            'alphanum': letters + string.digits,
            'punctuation': string.punctuation,
            'printable': string.printable,
            'ws': string.whitespace}

default_charset = charset['alphanum']

def rand_str(length=None, charset=default_charset, exclude=''):
    if length is None:
        length = random.randint(MIN_LEN, MAX_LEN)
    elif type(length) is list:
        length = random.choice(length)
    elif type(length) is tuple:
        length = random.randint(*length[:2])

    charset = ''.join(set(charset).difference(set(exclude)))

    return ''.join([random.choice(charset) for _ in range(length)])

def check(s, alg, regex):

    h = alg(s).digest()

    if re.match(regex, h) is None:
        return False

    return True

def __prove(alg, length, prefix, suffix, regex, charset, exclude, queue):
    regex = re.compile(regex)
    while True:
        if charset:
            s = rand_str(length, charset=charset, exclude=exclude)
        else:
            s = rand_str()
        s = prefix + s + suffix

        if check(s, alg, regex):
            queue.put(s)
            return s

    return None

def prove(alg=hashlib.sha1, length=None, prefix='', suffix='', regex='', charset=default_charset, exclude='', ncores=NCORES):

    queue = multiprocessing.Queue()

    args = (alg, length, prefix, suffix, regex, charset, exclude, queue)
    processes = [multiprocessing.Process(target=__prove, args=args) for _ in xrange(NCORES)]

    [p.start() for p in processes]

    s = queue.get()
    print(s)

    for p in processes:
        p.terminate()
    return s


if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument('-p', '--prefix', default='', action='store')
    parser.add_argument('-s', '--suffix', default='', action='store')
    parser.add_argument('-e', '--regexp', default='', action='store')
    parser.add_argument('-c', '--charset', default=default_charset, action='store')
    parser.add_argument('-x', '--exclude', default='', action='store')
    parser.add_argument('-a', '--alg', action='store', choices=hashlib.algorithms,default='sha1')

    args = parser.parse_args()

    prefix = args.prefix.decode('hex')
    suffix = args.suffix.decode('hex')

    regex = args.regexp

    alg = getattr(hashlib, args.alg)

    cs = args.charset
    exclude = args.exclude

    args = (alg, prefix, suffix, regex, cs, exclude, queue)
    processes = [multiprocessing.Process(target=prove, args=args) for _ in xrange(NCORES)]

    [p.start() for p in processes]

    s = queue.get()
    print(s)
    for p in processes:
        p.terminate()



from Crypto.Random.random import choice
from string import printable, ascii_lowercase, ascii_letters, digits
from math import log, ceil, floor
from os.path import isfile


def max_len_exception(max_length,min_length,min_entropy):
    return Exception("Went over max_length ("+str(max_length) +
                     ") trying to achieve min_length "+str(min_length) +
                     " and min_entropy "+str(min_entropy)+".")


def make_pass(pool='chars',
              min_entropy=20,
              min_length=6,
              max_length=30,
              filter_fn=None,
              mod_fn=None,
              join_str='',
              verbose=False,
              **kwargs):

    option_names = ['word_file']

    for arg_name in list(kwargs.keys()):
        if arg_name not in option_names:
            print('Warning: option',arg_name,'not known.')

    if min_length > max_length:
        raise Exception('min_length must be <= max_length.')

    if pool == 'chars':
        pool = printable.strip()

    elif pool == 'lowercase':
        pool = lowercase

    elif pool == 'alphanumeric':
        pool = ascii_letters + digits

    elif pool == 'words':

        if 'word_file' not in kwargs:
            word_file = '/usr/share/dict/words'
        else:
            word_file = kwargs['word_file']

        if not isfile(word_file):
            raise Exception('\''+word_file+'\' does not exist.')

        f = open(word_file)
        pool = [word.strip() for word in f.readlines()]

    elif type(pool) != list:
        raise Exception("Pool must be a list, 'chars', or 'words'.")

    # get rid of the empty string, obviously
    pool = [x for x in pool if x != '']

    # use a set to remove duplicates. also it's a more appropriate data structure
    pool = set(pool)

    if len(pool) == 0:
        raise Exception("Pool is the empty set!")

    # filter by the given function
    if filter_fn:
        pool = {x for n,x in enumerate(pool) if filter_fn(n,x)}
        if len(pool) == 0:
            raise Exception("Filter returned False for every element of pool.")

    # modify pool using the given function
    if mod_fn:
        pool = set(map(mod_fn, pool))

    ind_entropy = log(len(pool), 2)
    min_elements = int(ceil(min_entropy/ind_entropy))

    # only need to do this if elements are not length 1
    if any([len(x) > 1 for x in pool]):

        avg_req_element_length = floor( (max_length - len(join_str)*(min_elements - 1)) / min_elements )

        # figure out distribution of lengths
        len_dist = [0]*(max([len(x) for x in pool]))
        for x in pool:
            len_dist[len(x)-1] += 1

        # now figure out the distribution to get the right average
        

        # remove elements of the pool to achieve correct average length (so we probably nail max_length)
        while avg_req_element_length < float(sum([len(x) for x in pool]))/len(pool):

            max_element_length = max([len(x) for x in pool])

            # get rid of the longest ones
            pool = {x for x in pool if len(x) < max_element_length}
            if len(pool) == 0:
                raise max_len_exception(max_length, min_length, min_entropy)

            ind_entropy = log(len(pool), 2) # this has changed!
            min_elements = int(ceil(min_entropy/ind_entropy))
            avg_req_element_length = floor( (max_length - len(join_str)*(min_elements - 1)) / min_elements )

        if verbose:
            print('Average pool element length:', float(sum([len(x) for x in pool]))/len(pool))

    # need to switch back to a list for the random module
    pool = list(pool)

    element_lst = [choice(pool) for i in range(min_elements)]
    # we might get unlucky and have it too long. keep trying until we don't
    while len(join_str.join(element_lst)) > max_length:
        # no reason to limit entropy by not allowing repeats
        element_lst = [choice(pool) for i in range(min_elements)]

    while len(join_str.join(element_lst)) < min_length:
        element_lst += [choice(pool)]

    if len(join_str.join(element_lst)) > max_length:
        raise max_len_exception(max_length, min_length, min_entropy)

    if verbose:
        print('Password: ', join_str.join(element_lst))
        print('Bits entropy: ', ind_entropy*len(element_lst))
        print('Length: ', len(join_str.join(element_lst)))
        print('N. elements: ', len(element_lst))

    return join_str.join(element_lst)

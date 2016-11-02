
from Crypto.Random.random import choice, sample
from string import printable, ascii_lowercase, ascii_letters, digits
from math import log, ceil, floor
from os.path import isfile


def max_len_exception(max_length,min_length,min_entropy):
    return Exception("Went over max_length ("+str(max_length) +
                     ") trying to achieve min_length "+str(min_length) +
                     " and min_entropy "+str(min_entropy)+".")


def make_pass(pool='chars',
              min_entropy=20,
              min_length=8,
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
        pool = ascii_lowercase

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

        avg_req_element_length = float(max_length - len(join_str)*(min_elements - 1)) / min_elements

        # figure out distribution of lengths
        len_dist = [0]*(max([len(x) for x in pool]))
        for x in pool:
            len_dist[len(x)-1] += 1

        while True:
            tot_len = 0
            n_elements = 0
            # now figure out the distribution to get the right average
            for n,val in enumerate(len_dist):
                if float(tot_len+(n+1)*val)/(n_elements+val) > avg_req_element_length: # average has exceeded our max
                    break
                tot_len += (n+1)*val
                n_elements += val

            # figure out how many we need of that last category to bring the average up to what we want
            n_last = int(((avg_req_element_length - float(tot_len/n_elements))/(n+1 - avg_req_element_length)) * n_elements)

            if n+1 == len(len_dist) and n_last > len_dist[n]: # then we are using everything. no need to trim
                n_last = len_dist[n]

            # new pool size
            pool_size = n_elements + n_last

            ind_entropy = log(pool_size,2)
            if min_elements == int(ceil(min_entropy/ind_entropy)): # don't need to recalculate
                break
            min_elements = int(ceil(min_entropy/ind_entropy))

        pool = {x for x in pool if len(x) < n+1} | set( sample([x for x in pool if len(x) == n+1], n_last))

    # need to switch back to a list for the random module
    pool = list(pool)

    # no reason to limit entropy by not allowing repeats
    element_lst = [choice(pool) for i in range(min_elements)]
    # we might get unlucky and have it too long. keep trying until we don't
    # this reduces the entropy a bit. But I think it's not too bad
    while len(join_str.join(element_lst)) > max_length:
        print('Redoing... too long')
        element_lst = [choice(pool) for i in range(min_elements)]

    while len(join_str.join(element_lst)) < min_length:
        element_lst += [choice(pool)]

    if len(join_str.join(element_lst)) > max_length:
        raise max_len_exception(max_length, min_length, min_entropy)

    if verbose:
        print('Password: ', join_str.join(element_lst),'\n')
        if any([len(x) > 1 for x in pool]):
            print('Average pool element length: ', float(sum([len(x) for x in pool]))/len(pool))
        print('Bits entropy: ', ind_entropy*len(element_lst))
        print('Length: ', len(join_str.join(element_lst)))
        print('N. elements: ', len(element_lst))

    return join_str.join(element_lst)


if __name__ == "__main__":

    from sys import argv

    kwargs = {'verbose':True}
    
    for n,arg in enumerate(argv):
        if arg[0] == '-':
            try:
                kwargs[arg.lstrip('-')] = int(argv[n+1])
            except ValueError:
                try:
                    kwargs[arg.lstrip('-')] = float(argv[n+1])
                except ValueError:
                    pass

            if arg.lstrip('-') not in kwargs:
                kwargs[arg.lstrip('-')] = argv[n+1]
            pass
        pass

    make_pass(**kwargs)

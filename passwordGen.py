
from Crypto.Random.random import choice, sample
from string import printable, ascii_lowercase, ascii_letters, digits
from math import log, ceil, floor
from os.path import isfile
from sys import stderr


def max_len_exception(max_length,min_length,min_entropy):
    return Exception("Impossible to achieve min_entropy "+ str(min_entropy) +
                     " and max_length "+str(max_length)+". Try increasing max_length?")


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

    # error checking
    if pool != 'words' and 'word_file' in kwargs:
        print('Warning: word file supplied but pool not set to words. Ignoring file...',file=stderr)

    # figure out what pool we are using
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
            raise Exception('File \''+word_file+'\' does not exist.')

        f = open(word_file)
        pool = [word.strip() for word in f.readlines()]

        # set the modification to capitalize first letter of each
        if mod_fn is None:
            mod_fn = lambda x: x[0].upper() + x[1:].lower()

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
        pool = {x for x in pool if filter_fn(x)}
        if len(pool) == 0:
            raise Exception("Filter returned False for every element of pool.")

    # modify pool using the given function
    if mod_fn:
        pool = set(map(mod_fn, pool))

    entropy_per_element = log(len(pool), 2)

    # figure out the smallest number of elements needed to achieve the minimum requested entropy
    min_elements = int(ceil(min_entropy/entropy_per_element))

    # we want a length distribution that stays under max_length but still achieves the entropy needed.
    # so we drop really long words from the pool, so that the average word length is correct.
    # this only matters if the strings in pool are multiple characters
    if any([len(x) > 1 for x in pool]):

        # figure out distribution of lengths
        len_dist = [0]*(max([len(x) for x in pool]))
        for x in pool:
            len_dist[len(x)-1] += 1

        for n,freq in enumerate(len_dist):
            element_length = n+1 # zero indexed...
            average_length = sum(((np+1)*freqp for np,freqp in enumerate(len_dist[:n+1]))) / sum((x+1 for x in len_dist[:n+1]))
            entropy_per_element = log(sum((x+1 for x in len_dist[:n+1])),2)
            if float(max_length)/average_length * entropy_per_element < min_entropy:
                if sum((x+1 for x in len_dist[:n])) == 0: # started below the min_entropy :(
                    raise max_len_exception(max_length, min_length, min_entropy)
                break

        max_element_size = n

        # now generate the final pool we want.
        # it is everything with length less than or equal to element_size (which is now the max value we would want)
        # could also add some from the last group with length equal to element_size? need to calculate n_last
        pool = {x for x in pool if len(x) < max_element_size+1} # | set( sample([x for x in pool if len(x) == max_element_size+1], n_last))
        
        # recalculate these values
        entropy_per_element = log(sum((x+1 for x in len_dist[:n])),2)
        min_elements = int(ceil(min_entropy/entropy_per_element))

    # make sure it is at least possible to achieve the entropy we want, while keeping it under max_length
    if min_elements*min([len(x) for x in pool]) > max_length:
        raise max_len_exception(max_length, min_length, min_entropy)

    # need to switch back to a list for the random module
    pool = list(pool)

    # no reason to limit entropy by not allowing repeats, so use choice instead of sample
    element_lst = [choice(pool) for i in range(min_elements)]

    # we might get unlucky and have it too long. keep trying until we don't
    # this reduces the entropy a small bit, since we are rejecting some possibilities.
    # but calculating the true entropy is annoying so... sorry
    while len(join_str.join(element_lst)) > max_length:
        print('Redoing... too long. Entropy slightly less than advertised.\nMaybe try increasing max_length, or using a word list with shorter words.')
        element_lst = [choice(pool) for i in range(min_elements)]

    # if we are below min_length still, add elements until we get there
    while len(join_str.join(element_lst)) < min_length:
        element_lst += [choice(pool)]

    if verbose:
        print('Password: ', join_str.join(element_lst),'\n')
        if any([len(x) > 1 for x in pool]):
            print('Average word length: ', '{:.2f}'.format(float(sum([len(x) for x in pool]))/len(pool)))
        print('Bits entropy: ', '{:.2f}'.format(entropy_per_element*len(element_lst)))
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


Generate random passwords.

**Requires**: Python 3, `pycrypto`

Includes ability to use words in the style of [xkcd: Password Strength](https://xkcd.com/936/).

----

#### Options (= default):

When calling on the command line as `python3 passwordGen.py`, give options as `-option value`. Otherwise in Python 3 you can call `make_pass(option=value)`.

 - `min_entropy = 30`: The minimum entropy of the generated password. Entropy is defined as $\log_2$ of the total number of "similar" passwords. For a sense of scale, entropy of 30 or 40 is probably reasonable for general use. Entropy of >60 or so, you are pretty safe from even a powerful offline brute force attack.
 - `min_length = 8`: The minimum length in characters of the password.
 - `max_length = 20`: The maximum length in characters.
 - `join_str = ''`: The string used to join elements of the password. For example, `join_str=''` -> `thepassword`, `join_str='_'` -> `the_password`
 - `pool = 'chars'`: The pool from which to draw password elements (the set of things the password is generated from). Possibilities are:
    - `chars`: The set of all standard non-whitespace characters, i.e. punctuation, upper and lowercase letters, and digits. Note that if you are required to have a letter, number, and punctuation in your password, you might have to generate a few passwords before getting one that satisfies all the requirements.
    - `alphanumeric`: Just letters and numbers (no punctuation). Useful because they are very quick to type--and can still have a safe amount of entropy with a slightly longer password.
    - `lowercase`: lowercase letters only.
    - `words`: These passwords are designed to be easy to remember. Based off of the idea presented by Randall Munroe in [xkcd: Password Strength](https://xkcd.com/936/). By default, loads a list of words from `/usr/share/dict/words`, and make password by choosing random words from that list. If you pass this option, you can also pass `-word_file <path>` to give your own custom word list. I think using the set of 1000 most common English words is nice, some good lists can be found [here](https://github.com/first20hours/google-10000-english).
    - Finally, if calling in Python, you can simply pass a list of strings to `pool` and it will use that directly.
 - `verbose`: By default `True` when called from the command line, by default `False` when called in Python. Whether to print out the password and information about its length, entropy, etc.
 - `filter_fn = None`: Only can be used when calling in Python (not from command line). This option gives the ability to apply some filter to the list. Should be a function that returns True or False when passed a string. For example, if you only want words shorter than 5 characters, do `make_pass(pool='words',filter_fn=lambda x: len(x) < 6)`.
 - `mod_fn`: Also can only be used when calling in Python. This is a function that is applied to all elements before they are used. Default is none unless `pool='words'`. For example:
    - If you want all words in your password to be lowercase, do: `make_pass(pool='words',mod_fn=lambda x: x.lower())` 
    - Or maybe make first letters uppercase: `make_pass(pool='words',mod_fn=lambda x: x[0].upper() + x[1:].lower())`. This is the default if `pool='words'`.

----

Enjoy!
def deep_get(dictionary, key_separated_by_dots):
    levels = key_separated_by_dots.split('.')
    for level in levels:
        dictionary = dictionary.get(level)
    return dictionary
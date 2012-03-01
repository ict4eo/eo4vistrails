

level = 0

def msg(lvl, *args):
    if lvl <= level:
        print " ".join([str(x) for x in args])


import sublime_plugin
from sublime import Region

from operator import neg, mul

class UnquoteCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        """ If the selection starts and ends with matching quotes, just remove them.
            Otherwise, expand the selection one char each way and try again.
        """
        v = self.view

        def find_num_quotes(reg, size=1):
            """ Find `size` number of quotes/backticks in Region `reg`.
                Returns number of chars to delete on either end.
            """
            text = v.substr(reg)
            chars = 0 # default to not finding (and erasing) anything

            for x in ["'", '"', "`"]:
                if (text[0:size] == text[neg(size):] == mul(x, size)): # slicing FTW!
                    chars = size

            return chars

        def trimquotes(reg, chars=0):
            """ Erase `char` characters from either end of Region `reg`
            """
            v.erase(edit, Region(reg.end() - chars, reg.end()))
            v.erase(edit, Region(reg.begin(), reg.begin() + chars))

        def grow_region(reg, size=0):
            """ Expand Region `reg` by `size` chars on each end
            """
            return Region(reg.begin() - size, reg.end() + size)

        for reg in v.sel():
            trimsize = find_num_quotes(reg, 3) or find_num_quotes(reg, 1)
            if trimsize: # the selection includes quotes
                trimquotes(reg, trimsize)
            else: # we can't find quotes yet...
                newreg = grow_region(reg, 3)
                if find_num_quotes(newreg, 3): # we found a triplet
                    trimquotes(newreg, 3)
                else:
                    newreg = grow_region(reg, 1)
                    trimquotes(newreg, find_num_quotes(newreg))

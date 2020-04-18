from bitdic import make_initial_bitdic


def test():
    bdic = make_initial_bitdic('config1.json')
    bdic.visualize()    # this will write to Org.txt

    # split into 2: bdic0(Org-7@0) / bdic1(Org-7@1)
    # Tx (bdic1) -> bdic1t
    bdic0, bdic1, bdic1t = bdic.split_topbit()
    bdic0.visualize()   # this will write to Org-7@0.txt
    bdic1.visualize()   # this will write to Org-7@1.txt
    bdic1t.visualize()  # this will write to Org-7@1t.txt

    # split bdic0 into 2: bdic00()
    bdic00, bdic01, bdic01t = bdic0.split_topbit()
    bdic00.visualize()   # => Org-7@0-6@0.txt
    bdic01.visualize()   # => Org-7@0-6@1.txt
    bdic01t.visualize()  # => Org-7@0-6@1t.txt

    bdic10, bdic11, bdic11t = bdic1t.split_topbit()
    bdic10.visualize()   # => Org-7@1-6@0.txt
    bdic11.visualize()   # => Org-7@1-6@1.txt
    bdic11t.visualize()  # => Org-7@1-6@1t.txt
    x = 0


if __name__ == '__main__':
    test()
    x = 1

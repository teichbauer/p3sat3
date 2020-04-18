from bitdic import make_initial_bitdic


def test():
    bdic = make_initial_bitdic('config1.json')
    bdic.visualize()    # this will write to Org.txt

    # split into 2: bdic0(bit-7 = 0) / bdic1(bit-7 = 1)
    # Tx (bdic1) -> bdic1t
    bdic0, bdic1, bdic1t = bdic.split_topbit()
    bdic0.visualize()   # this will write to Org-0.txt
    bdic1.visualize()   # this will write to Org-1.txt
    bdic1t.visualize()  # this will write to Org-1t.txt

    # split bdic0 into 2: bdic00()


if __name__ == '__main__':
    test()
    x = 1

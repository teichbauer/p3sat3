from bitdic import make_initial_bitdic, BitDic
from basics import get_sdic
from TransKlauseEngine import make_vkdic, trans_vkdic


def test():
    # ----------((8bit))
    org = make_initial_bitdic('config1.json')
    # org.visualize()    # this will write to Org.txt

    # ----------((7bit)): 2 parts
    # split into 2: bdic0(Org-7@0) / bdic1(Org-7@1)
    # Tx (bdic1) -> bdic1t
    # == Org -> Org-7@0 and Org-7@1t
    org70, org71, org71t = org.split_topbit()
    # org70.visualize()   # this will write to Org-7@0.txt
    # org71.visualize()   # this will write to Org-7@1.txt
    # org71t.visualize()  # this will write to Org-7@1t.txt

    # -----------((6bit)): 4 parts ------------------------
    # ------ part0, part1
    # == Org-7@0 -> Org-7@0-6@0, Org-7@0-6@1t
    org7060, org7061, org7061t = org70.split_topbit()
    # org7060.visualize()   # => Org-7@0-6@0.txt
    # org7061.visualize()   # => Org-7@0-6@1.txt
    # org7061t.visualize()  # => Org-7@0-6@1t.txt

    # ------- part2, part3
    # == Org-7@1t -> Org-7@1t-6@0, Org-7@1t-6@1t
    org7160, org7161, org7161t = org71t.split_topbit()
    # org7160.visualize()   # => Org-7@1-6@0.txt
    # org7161.visualize()   # => Org-7@1-6@1.txt
    # org7161t.visualize()  # => Org-7@1-6@1t.txt

    # -----------((5bit)): 8 parts ---------------
    # part0 part1
    # == Org-7@0-6@0 -> Org-7@0-6@0-5@0, Org-7@0-6@0-5@1
    org706050, org706051, org706051t = org7060.split_topbit()
    org706050.visualize()
    org706051.visualize()   # transition bdic. For reading only
    org706051t.visualize()

    # part2 part3
    # == Org-7@0-6@1t -> Org-7@0-6@1t-5@0, Org-7@0-6@1t-5@1t
    org706150, org706151, org706151t = org7061t.split_topbit()
    org706150.visualize()
    org706151.visualize()   # transition bdic. For reading only
    org706151t.visualize()
    # ---------------------------------
    # part4 part5
    # == Org-7@1t-6@0 -> Org-7@1t-6@0-5@0, Org-7@1t-6@0-5@1t
    org716050, org716051, org716051t = org7160.split_topbit()
    org716050.visualize()
    org716051.visualize()   # transition bdic. For reading only
    org716051t.visualize()

    # part6 part7
    # == Org-7@1t-6@1t -> Org-7@1t-6@1t-5@0, Org-7@1t-6@1t-5@1t
    org716150, org716151, org716151t = org7161t.split_topbit()
    org716150.visualize()
    org716151.visualize()   # transition bdic. For reading only
    org716151t.visualize()

    x = 0


def initial_bitdic(conf_filename, seed):
    sdic = get_sdic(conf_filename)
    vkdic = make_vkdic(sdic['kdic'], sdic['nov'])
    bitdic = BitDic(seed, seed, vkdic, sdic['nov'])
    return bitdic


def sub_tree(bdic):
    bdic.visualize()


def loop_tree(conf_filename, seed):
    bitdic = initial_bitdic(conf_filename, seed)
    sub_tree(bitdic)


if __name__ == '__main__':
    # test()
    loop_tree('config1.json', 'C001')
    x = 1

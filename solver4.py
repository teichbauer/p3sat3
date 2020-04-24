from bitdic import make_initial_bitdic, BitDic, perf_count
from basics import get_sdic
from TransKlauseEngine import make_vkdic, trans_vkdic
import pprint
import sys


def initial_bitdic(conf_filename, seed):
    sdic = get_sdic(conf_filename)
    vkdic = make_vkdic(sdic['kdic'], sdic['nov'])
    bitdic = BitDic(seed, seed, vkdic, sdic['nov'])
    return bitdic


def sub_tree(bdic, debug=False):
    perf_count["subtree-call"] += 1
    if debug:
        bdic.visualize()

    if not bdic.done:
        bdic0, bdic1 = bdic.split_topbit(debug)
        if type(bdic0) == type(1):
            print(f'SAT found: {bdic0}')    # SAT!
        else:
            sub_tree(bdic0, debug)
            sub_tree(bdic1, debug)


def loop_tree(conf_filename, seed, debug=False):
    root0 = initial_bitdic(conf_filename, seed)
    if debug:
        root0.visualize()
    seed = root0.set_txseed()
    root = root0.TxTopKn(seed)
    # sub_tree(root, debug)
    search_sat(root, debug)


def search_sat(root, debug):
    nodes = [root]
    while len(nodes) > 0:
        node = nodes.pop(0)
        if not node.done:
            node0, node1 = node.split_topbit(debug)
            # in split_topbit, the two children are tested to see
            # if 1 of them has sat. If yes, return will be
            # <sat>, None
            if type(node0) == type(1):  # see if it is sat(integer)
                print(f'SAT found: {bdic0}')    # SAT!
            else:
                nodes.append(node0)
                nodes.append(node1)


if __name__ == '__main__':
    pp = pprint.PrettyPrinter(indent=4)
    debug = len(sys.argv) > 1
    # debug = False
    loop_tree('config1.json', 'C001', debug)
    print('perf-count: ')
    pp.pprint(perf_count)

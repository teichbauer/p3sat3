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


def loop_tree(conf_filename, seed, debug=False):
    root0 = initial_bitdic(conf_filename, seed)
    if debug:
        root0.visualize()
    seed = root0.set_txseed()
    root = root0.TxTopKn(seed)
    search_sat(root, debug)


def search_sat(root, debug):
    nodes = [root]
    while len(nodes) > 0:
        node = nodes.pop(0)
        if node.done:
            print(f'{node.name} is done.')
        else:
            print(f'split {node.name}')
            node0, node1 = node.split_topbit(debug)
            # in split_topbit, the two children are tested to see
            # if 1 of them has sat. If yes, return will be
            # <sat>, None
            if type(node0) == type(1):  # see if it is sat(integer)
                print(f'SAT found: {node0}')    # SAT!
                break
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

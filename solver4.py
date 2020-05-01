from vklause import VKlause
from bitdic import BitDic, perf_count
from basics import get_sdic
import pprint
import sys
import time


_time_count = 0


def make_vkdic(kdic, nov):
    vkdic = {}
    for kn, klause in kdic.items():
        vkdic[kn] = VKlause(kn, klause, nov)
    return vkdic


def initial_bitdic(conf_filename, seed='C001'):
    sdic = get_sdic(conf_filename)
    vkdic = make_vkdic(sdic['kdic'], sdic['nov'])
    bitdic = BitDic(seed, seed, vkdic, sdic['nov'])
    return bitdic


def loop_tree(conf_filename, msg=False, debug=False):
    global _time_count
    root0 = initial_bitdic(conf_filename)
    if debug:
        root0.visualize()
    seed, top_bit = root0.set_txseed()
    root = root0.TxTopKn(seed, top_bit)

    tx = root.conversion
    # test_tx(tx, root0.vkdic)

    _time_count = time.time()
    search_sat(root, msg, debug)


def search_sat(root, msg, debug):
    nodes = [root]
    while len(nodes) > 0:
        node = nodes.pop(0)
        if debug:
            node.visualize()
        if node.done:
            if msg:
                print(f'{node.name} is done.')
        else:
            if msg:
                print(f'split {node.name}')
            node0, node1 = node.split_topbit(debug)
            # in split_topbit, the two children are tested to see
            # if 1 of them has sat. If yes, return will be
            # <sat>, None
            if type(node0) == type(1):  # see if it is sat(integer)
                print(f'{node0} SATs found ')    # SAT!
                # print(f'start time: {_time_count}')
                perf_count['time-used'] = time.time() - _time_count
                break
            else:
                if node0.done:
                    if msg:
                        print(f'{node0.name} is done.')
                else:
                    nodes.append(node0)
                if node1.done:
                    if msg:
                        print(f'{node1.name} is done.')
                else:
                    nodes.append(node1)


if __name__ == '__main__':
    pp = pprint.PrettyPrinter(indent=4)
    msg = len(sys.argv) == 3
    debug = len(sys.argv) == 4
    if len(sys.argv) == 1:
        config_file_name = 'config20_80.json'
        # config_file_name = 'config1.json'
    else:
        config_file_name = sys.argv[1]
    loop_tree('./configs/' + config_file_name, msg, debug)
    print('perf-count: ')
    pp.pprint(perf_count)

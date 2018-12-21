from statistics import mean, median
from bitcoinrpc import Bitcoind

BLOCK_HASH = "0000000000000000000e0d3a46b57450ca7d3af3533f8e682823b48035cdf725"


raw = Bitcoind.getblock(BLOCK_HASH)

info = {'ins':  [],
        'outs': [],
        'out_value': [],
        'size': [],
       }

for tx in raw['tx']:
    parsed = Bitcoind.get_parsed_tx(tx)
    info['ins'].append(sum([1 for _ in parsed['vin']]))
    info['outs'].append(sum([1 for _ in parsed['vout']]))
    info['out_value'].append(sum([o['value'] for o in parsed['vout']]))
    info['size'].append(parsed['size'])
    for out in parsed['vout']:
        print("type: %s" % out['scriptPubKey']['type'])
        #if 'addresses' not in out['scriptPubKey']:
        #    #print("bech32?")
        #    continue
        #for o in out['scriptPubKey']['addresses']:
        #    print(o)


print("")
print("transactions: %d" % len(raw['tx']))
print("")
print("count ins: %d" % sum(info['ins']))
print("mean ins: %0.2f" % mean(info['ins']))
print("median ins: %d" % median(info['ins']))
print("")
print("count outs: %d" % sum(info['outs']))
print("mean outs: %0.2f" % mean(info['outs']))
print("median outs: %d" % median(info['outs']))
print("")
print("count coins: %0.8f" % sum(info['out_value']))
print("mean coins: %0.8f" % mean(info['out_value']))
print("median coins: %0.8f" % median(info['out_value']))
print("")
print("count bytes: %d" % sum(info['size']))
print("mean bytes: %0.2f" % mean(info['size']))
print("median bytes: %d" % median(info['size']))


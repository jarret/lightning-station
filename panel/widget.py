# Copyright (c) 2020 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import urwid
import time
import datetime
from datetime import datetime
from fixed_draw import FreeDrawFont, HalfBlock5x6Font

def recent(items, secs):
    now = time.time()
    stripped = []
    for i in items:
        #print(i)
        if (i[1] + secs < now):
            return tuple(None for i in items)
        stripped.append(i)
    return tuple(i[0] for i in items)

class Widget():

    @staticmethod
    def btc_symb():
        w = urwid.BigText(('orange', "B"), FreeDrawFont())
        w = urwid.Padding(w, align='left', width='clip')
        #w = urwid.SimpleFocusListWalker([w])
        w = urwid.ListBox([w])
        w = urwid.BoxAdapter(w, 15)
        w = urwid.Filler(w, valign="top")
        #w = urwid.AttrWrap(w, "orange")
        return w

    @staticmethod
    def itcoin():
        w = urwid.BigText(('orange', "ITCOIN"),
                           urwid.font.HalfBlock7x7Font())
        w = urwid.Padding(w, align='left', width='clip')
        #w = urwid.SimpleFocusListWalker([w])
        w = urwid.ListBox([w])
        w = urwid.BoxAdapter(w, 7)
        w = urwid.Filler(w, valign="middle")
        #w = urwid.AttrWrap(w, "orange")
        return w

    @staticmethod
    def subtitle_top():
        markup = [('orange', "A Peer-to-Peer")]
        w = urwid.BigText(markup,
                          urwid.font.HalfBlock5x4Font())
        w = urwid.Padding(w, align='center', width='clip')
        w = urwid.ListBox([w])
        w = urwid.BoxAdapter(w, 7)
        w = urwid.Filler(w, valign="middle")
        return w

    @staticmethod
    def subtitle_bottom():
        markup = [('orange', "Electronic Cash System")]
        w = urwid.BigText(markup,
                          urwid.font.HalfBlock5x4Font())
        w = urwid.Padding(w, align='center', width='clip')
        w = urwid.ListBox([w])
        w = urwid.BoxAdapter(w, 7)
        w = urwid.Filler(w, valign="middle")
        return w

    @staticmethod
    def subtitle():
        top = Widget.subtitle_top()
        bottom = Widget.subtitle_bottom()
        return urwid.Filler(urwid.Pile([(6, top), (6, bottom)]), top=2)

    def big_5x6(markup, align):
        w = urwid.BigText(markup, HalfBlock5x6Font())
        w = urwid.Padding(w, align=align, width='clip')
        w = urwid.ListBox([w])
        w = urwid.BoxAdapter(w, 6)
        w = urwid.Filler(w)
        w = urwid.Padding(w)
        return w

    ###########################################################################

    @staticmethod
    def total_supply(total_supply):
        #print("t1: %s" % total_supply)
        (total_supply,) = recent((total_supply,), 60 * 60 * 24 * 14)
        #print("t2: %s" % total_supply)
        if total_supply is None:
            markup = [("orange_minor_text", " ~ "),
                      ("major_text", "(no supply info)"),
                      ("grey_minor_text", " total"),
                      ("orange_minor_text", " BTC ")]
            w = Widget.big_5x6(markup, "center")
            return w
        totalstr = "{:,}".format(total_supply)
        markup = [("orange_minor_text", " ~ "),
                  ("major_text", totalstr),
                  ("grey_minor_text", " total"),
                  ("orange_minor_text", " BTC ")]
        w = Widget.big_5x6(markup, "center")
        return w

    @staticmethod
    def mkt_cap(mkt_cap):
        (mkt_cap,) = recent((mkt_cap,), 60 * 60 * 24 * 14)
        if mkt_cap is None:
            markup = [("grey_minor_text", " Mkt Cap:"),
                      ("dark_red_minor_text", " $ "),
                      ("major_text", "(no mkt cap info)"),
                      ("dark_red_minor_text", " CAD ")]
            w = Widget.big_5x6(markup, "center")
            return w
        mkt_cap_str = "{:,} ".format(int(mkt_cap))
        markup = [("grey_minor_text", " Mkt Cap:"),
                  ("dark_red_minor_text", " $ "),
                  ("major_text", mkt_cap_str),
                  ("dark_red_minor_text", " CAD ")]
        w = Widget.big_5x6(markup, "center")
        return w

    @staticmethod
    def price(price):
        (price,) = recent((price,), 60 * 60)
        if price is None:
            markup = [("dark_red_minor_text", " $ "),
                      ("major_text", "(no recent price info)"),
                      ("dark_red_minor_text", " CAD "),
                      ("grey_minor_text", "per"),
                      ("orange_minor_text", " BTC ")]
            w = Widget.big_5x6(markup, "center")
            return w
        pricestr = "{:,.2f} ".format(round(price, 2))
        markup = [("dark_red_minor_text", " $ "),
                  ("major_text", pricestr),
                  ("dark_red_minor_text", " CAD "),
                  ("grey_minor_text", "per"),
                  ("orange_minor_text", " BTC ")]
        w = Widget.big_5x6(markup, "center")
        return w

    @staticmethod
    def inv_price(price):
        (price,) = recent((price,), 60 * 60)
        if price is None:
            markup = [("dark_red_minor_text", " $ "),
                      ("major_text", "(no recent price info)"),
                      ("dark_red_minor_text", " CAD "),
                      ("grey_minor_text", "per"),
                      ("orange_minor_text", " BTC ")]
            w = Widget.big_5x6(markup, "center")
            return w
        price = round(price, 8)
        pricestr = " %0.8f" % price
        markup = [("orange_minor_text", " ~ "),
                  ("major_text", pricestr),
                  ("orange_minor_text", " BTC "),
                  ("grey_minor_text", "per"),
                  ("dark_red_minor_text", " CAD ")]
        w = Widget.big_5x6(markup, "center")
        return w

    ###########################################################################

    @staticmethod
    def _wrap_box(widget, title, theme):
        lb = urwid.LineBox(widget, title=title)
        return urwid.AttrMap(lb, theme['panel'])

    @staticmethod
    def _dummy_box(title, theme):
        return Widget._wrap_box(urwid.Pile([]), title, theme)

    ###########################################################################

    @staticmethod
    def _progress_bar(pct, theme):
        return urwid.ProgressBar(theme['progress_n'], theme['progress_c'],
                                 current=pct, done=100)

    @staticmethod
    def _stat_line(label, value, unit, theme):
        mu = []
        if label != None:
            mu.append((theme['minor_text'], " %s: " % label))
        if value != None:
            mu.append((theme['major_text'], "%s " % value))
        if unit != None:
            mu.append((theme['minor_text'], "%s " % unit))
        return urwid.Text(mu, align='center')

    @staticmethod
    def _line_pile_box(lines, title, theme):
        return Widget._wrap_box(urwid.Pile(lines), title, theme)

    ###########################################################################

    @staticmethod
    def _fmt_seconds(seconds):
        m = seconds // 60
        s = seconds % 60
        return "%d min %d sec" % (m, s)

    @staticmethod
    def _fmt_timestamp(timestamp):
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime('%b %d, %H:%M:%S')

    @staticmethod
    def _elapsed_line(elapsed, since, theme):
        a = (theme['major_text'], " " + Widget._fmt_seconds(elapsed))
        i = (theme['minor_text'], " since %s " % since)
        return urwid.Text([a, i], align='center')

    ###########################################################################
    def _center_major_text(string, theme):
        return urwid.Text((theme['major_text'], " %s " % string),
                          align='center')
    def _center_minor_text(string, theme):
        return urwid.Text((theme['minor_text'], " %s " % string),
                           align='center')

    @staticmethod
    def _title_row(strs, theme):
        return Widget._center_minor_text(" ".join(strs), theme)

    @staticmethod
    def _row(strs, theme):
        t = (theme['minor_text'], " " + strs[0] + " ")
        m = (theme['major_text'], " ".join(strs[1:]) + " ")
        return urwid.Text([t, m], align='center')


    ###########################################################################

    @staticmethod
    def cpu_box(cpu_pcts, theme):
        (cpu_pcts,) = recent((cpu_pcts,), 60 * 60)
        if cpu_pcts is None:
            return Widget._dummy_box("(no recent cpu data)", theme)
        lines = []
        for cpu in cpu_pcts:
            lines.append(Widget._progress_bar(cpu, theme))
        title = "%d CPUs" % len(cpu_pcts)
        return Widget._line_pile_box(lines, title, theme)

    @staticmethod
    def ram_box(mem_total, mem_used, mem_used_pct, theme):
        (mem_total, mem_used, mem_used_pct) = recent(
            (mem_total, mem_used, mem_used_pct), 60 * 60)
        if mem_total is None:
            return Widget._dummy_box("(no recent ram data)", theme)

        r = Widget._stat_line("Total", "{:,}".format(mem_total),
                            "bytes", theme)
        u = Widget._stat_line("Used", "{:,}".format(mem_used),
                            "bytes", theme)
        up = Widget._progress_bar(mem_used_pct, theme)

        lines = [r, u, up]
        return Widget._line_pile_box(lines, "RAM", theme)


    @staticmethod
    def mempool_box(mempool_txes, mempool_bytes, mempool_max_used,
                    mempool_mem_used, theme):
        (mempool_txes, mempool_bytes, mempool_max_used,
                    mempool_mem_used) = recent(
            (mempool_txes, mempool_bytes, mempool_max_used, mempool_mem_used),
             60 * 60)
        if mempool_txes is None:
            return Widget._dummy_box("(no recent mempool data)", theme)

        h = Widget._stat_line("Mempool Txes", "{:,}".format(mempool_txes),
                              None, theme)
        at = Widget._stat_line("Tx Bytes", "{:,}".format(mempool_bytes),
                               None, theme)
        m = Widget._stat_line("Max Mempool RAM",
                              "{:,}".format(mempool_max_used), None, theme)
        x = Widget._stat_line("RAM Used", "{:,}".format(mempool_mem_used),
                              None, theme)
        lines = [h, at, m, x]
        return Widget._line_pile_box(lines, "Mempool", theme)

    @staticmethod
    def estimates_box(fee_estimates, fee_estimates_eco, theme):
        (fee_estimates, fee_estimates_eco) = recent(
            (fee_estimates, fee_estimates_eco), 60 * 60)
        if fee_estimates is None:
            return Widget._dummy_box("(no recent estimate data)", theme)

        blocks = sorted(fee_estimates.keys(), key=lambda x: int(x))

        b_row = ["Blks"]
        b_row += [str(b) for b in blocks]

        c_row = ["Norm"]
        c_row += [str(int(round(fee_estimates[b]))) for b in
                  blocks]

        e_row = ["Econ"]
        e_row += [str(int(round(fee_estimates_eco[b]))) for b in
                  blocks]

        b_strs = []
        c_strs = []
        e_strs = []
        for i in range(len(blocks) + 1):
            b = b_row[i]
            c = c_row[i]
            e = e_row[i]
            width = max(len(b), len(c), len(e))
            fmt = "%%%ds" % width
            b_strs.append(fmt % b)
            c_strs.append(fmt % c)
            e_strs.append(fmt % e)

        b_str = Widget._title_row(b_strs, theme)
        c_str = Widget._row(c_strs, theme)
        e_str = Widget._row(e_strs, theme)
        lines = [b_str, c_str, e_str]
        return Widget._line_pile_box(lines, "Fee Estimates (sat/byte)", theme)

    @staticmethod
    def cad_estimates_box(fee_estimates_cad_250, theme):
        (fee_estimates_cad_250,) = recent((fee_estimates_cad_250,), 60 * 60)
        if fee_estimates_cad_250 is None:
            return Widget._dummy_box("(no recent estimate data)", theme)
        blocks = sorted(fee_estimates_cad_250.keys(), key=lambda x: int(x))
        b_row = ["Blks"]
        b_row += [str(b) for b in blocks]
        c_row = ["CAD"]
        c_row += ["$" + str(round(fee_estimates_cad_250[b], 2)) for b in
                  blocks]
        b_strs = []
        c_strs = []
        for i in range(len(blocks) + 1):
            b = b_row[i]
            c = c_row[i]
            width = max(len(b), len(c))
            fmt = "%%%ds" % width
            b_strs.append(fmt % b)
            c_strs.append(fmt % c)
        b_str = Widget._title_row(b_strs, theme)
        c_str = Widget._row(c_strs, theme)
        lines = [b_str, c_str]
        return Widget._line_pile_box(lines, "CAD Fee Estimate - 250 byte tx",
                                     theme)

    @staticmethod
    def block_id_box(block_height, block_arrival_timestamp, block_timestamp,
                     theme):
        (block_height, block_arrival_timestamp, block_timestamp) = (
            recent((block_height, block_arrival_timestamp, block_timestamp),
                    60 * 60 *  4))
        if block_height is None:
            return Widget._dummy_box("(no recent block data)", theme)
        h = Widget._stat_line("Height", str(block_height), None, theme)
        arrival = Widget._fmt_timestamp(block_arrival_timestamp)
        at = Widget._stat_line("Arrive Time", arrival, None, theme)
        miner = Widget._fmt_timestamp(block_timestamp)
        t = Widget._stat_line("Miner Time", miner, None, theme)
        lines = [h, at, t]
        return Widget._line_pile_box(lines, "Block ID", theme)


    @staticmethod
    def block_stat_box(block_n_txes, block_size, block_weight,
                       block_arrival_timestamp, theme):
        (block_n_txes, block_size, block_weight, block_arrival_timestamp) = (
            recent((block_n_txes, block_size, block_weight,
                   block_arrival_timestamp), 60 * 60 *  4))
        if block_n_txes is None:
            return Widget._dummy_box("(no recent block data)", theme)
        tx = Widget._stat_line("Included",
                               "{:,}".format(block_n_txes),
                               "txs", theme)
        s = Widget._stat_line("Block Size",
                              "{:,}".format(block_size),
                              "bytes", theme)
        w = Widget._stat_line("Block Weight",
                              "{:,}".format(block_weight),
                              "bytes", theme)
        elapsed = time.time() - block_arrival_timestamp
        e = Widget._elapsed_line(elapsed, "last block", theme)
        lines = [tx, s, w, e]
        return Widget._line_pile_box(lines, "Block Stats", theme)

    @staticmethod
    def block_details_box(grind_stats, rewards, block, theme):
        (grind_stats, rewards) = recent((grind_stats, rewards), 60 * 60)
        if grind_stats is None:
            return Widget._dummy_box("(no recent block data)", theme)
        grind_stats = grind_stats[block]
        reward = rewards[block]
        size = Widget._stat_line("Block Size", "{:,}".format(
            grind_stats['size']), "bytes", theme)
        weight = Widget._stat_line("Block Weight", "{:,}".format(
            grind_stats['weight']), "vbytes", theme)
        new_coins = Widget._stat_line("New Coins", "{:,}".format(
            grind_stats['new_coins']), "BTC", theme)
        miner_fees = Widget._stat_line("Miner Fees", "{:,}".format(
            grind_stats['miner_fees']), "BTC", theme)
        miner_reward = Widget._stat_line("Miner Reward", "${:,}".format(reward),
            "CAD", theme)
        lines = [size, weight, new_coins, miner_fees, miner_reward]
        return Widget._line_pile_box(lines, "Block %s" % block, theme)

    @staticmethod
    def value_transferred(grind_stats, price_btccad, theme):
        (grind_stats, price_btccad) = recent((grind_stats, price_btccad),
                                             60 * 60)
        if grind_stats is None:
            return Widget._dummy_box("(no recent block data)", theme)

        lines = []
        title = urwid.Text([(theme['minor_text'], "  block         "),
                            (theme['minor_text'], "  BTC      "),
                            (theme['minor_text'], "  CAD   "),
                            (theme['minor_text'], "  min CAD tx  "),
                            (theme['minor_text'], "  median CAD tx  "),
                            (theme['minor_text'], "  mean CAD tx  "),
                            (theme['minor_text'], "  max CAD  tx "),
                           ],
                            align='center')
        lines.append(title)
        for block in sorted(grind_stats.keys(), reverse=True):
            inputs = grind_stats[block]['total_input_btc']
            cad = round(price_btccad * inputs, 2)
            mincad = round(price_btccad *
                           grind_stats[block]['tx_out_btc']['min'], 2)
            meancad = round(price_btccad *
                            grind_stats[block]['tx_out_btc']['mean'], 2)
            mediancad = round(price_btccad *
                              grind_stats[block]['tx_out_btc']['median'], 2)
            maxcad = round(price_btccad *
                           grind_stats[block]['tx_out_btc']['max'], 2)
            line = urwid.Text([(theme['minor_text'], "  %s  " % block),
                               (theme['major_text'], "  %0.8f   " % inputs),
                               (theme['major_text'],
                                "  ${:,}  ".format(round(cad, 2))),
                               (theme['major_text'],
                                "  ${:,}  ".format(round(mincad, 2))),
                               (theme['major_text'],
                                "  ${:,}  ".format(round(mediancad, 2))),
                               (theme['major_text'],
                                "  ${:,}  ".format(round(meancad, 2))),
                               (theme['major_text'],
                                "  ${:,}  ".format(round(maxcad, 2))),
                              ],
                               align='center')
            lines.append(line)

        return Widget._line_pile_box(lines, "Value Transferred", theme)


    @staticmethod
    def pad_align_cols(rows):
        new_rows = []
        for i in range(len(rows[0])):
            new_rows.append([])
            max_width = 0
            for j in range(len(rows)):
                max_width = max(max_width, len(rows[j][i]))
            for j in range(len(rows)):
                fmt = "%%%ds" % max_width
                new_rows[i].append(fmt % rows[j][i])
        return [list(i) for i in zip(*new_rows)]

    @staticmethod
    def value_transferred(grind_stats, price_btccad, theme):
        (grind_stats, price_btccad) = recent((grind_stats, price_btccad),
                                             60 * 60)
        if grind_stats is None:
            return Widget._dummy_box("(no recent tx data)", theme)

        t_row = ['Block', 'BTC', "Txs", 'CAD', ' Mean CAD/tx', 'Min CAD/tx',
                 'Median CAD/tx', 'Max CAD/tx']
        rows = [t_row]
        for block in sorted(grind_stats.keys(), reverse=True):
            inputs = grind_stats[block]['total_input_btc']
            txs = grind_stats[block]['n_transactions']
            cad = round(price_btccad * inputs, 2)
            mincad = round(price_btccad *
                           grind_stats[block]['tx_out_btc']['min'], 2)
            meancad = round(price_btccad *
                            grind_stats[block]['tx_out_btc']['mean'], 2)
            mediancad = round(price_btccad *
                              grind_stats[block]['tx_out_btc']['median'], 2)
            maxcad = round(price_btccad *
                           grind_stats[block]['tx_out_btc']['max'], 2)
            rows.append([str(block), "%0.8f" % inputs,
                         "{:,}".format(txs),
                         "${:,.2f}".format(round(cad, 2)),
                         "${:,.2f}".format(round(meancad, 2)),
                         "${:,.2f}".format(round(mincad, 2)),
                         "${:,.2f}".format(round(mediancad, 2)),
                         "${:,.2f}".format(round(maxcad, 2))])
        rows = Widget.pad_align_cols(rows)
        lines = []
        lines.append(Widget._title_row(rows[0], theme))
        for row in rows[1:]:
            lines.append(Widget._row(row, theme))
        return Widget._line_pile_box(lines, "Value Transferred", theme)

    @staticmethod
    def tx_size(grind_stats, price_btccad, theme):
        (grind_stats, price_btccad) = recent((grind_stats, price_btccad),
                                             60 * 60)
        if grind_stats is None:
            return Widget._dummy_box("(no recent tx data)", theme)

        t_row = ['Block', "Txs", 'Mean b/tx', 'Min b/tx', 'Median b/tx',
                 'Max b/tx', "Mean vb/tx", "Min vb/tx", "Median vb/tx",
                 "Max vb/tx"]
        rows = [t_row]
        for block in sorted(grind_stats.keys(), reverse=True):
            txs = grind_stats[block]['n_transactions']
            meanb = int(grind_stats[block]['tx_size']['mean'])
            minb = grind_stats[block]['tx_size']['min']
            medianb = int(grind_stats[block]['tx_size']['median'])
            maxb = grind_stats[block]['tx_size']['max']
            meanvb = int(grind_stats[block]['tx_vsize']['mean'])
            minvb = grind_stats[block]['tx_vsize']['min']
            medianvb = int(grind_stats[block]['tx_vsize']['median'])
            maxvb = grind_stats[block]['tx_vsize']['max']
            rows.append([str(block),
                         "{:,}".format(txs),
                         "{:,}".format(meanb),
                         "{:,}".format(minb),
                         "{:,}".format(medianb),
                         "{:,}".format(maxb),
                         "{:,}".format(meanvb),
                         "{:,}".format(minvb),
                         "{:,}".format(medianvb),
                         "{:,}".format(maxvb),
                        ])
        rows = Widget.pad_align_cols(rows)
        lines = []
        lines.append(Widget._title_row(rows[0], theme))
        for row in rows[1:]:
            lines.append(Widget._row(row, theme))
        return Widget._line_pile_box(lines, "Transaction Size", theme)

    @staticmethod
    def inputs_outputs(grind_stats, price_btccad, theme):
        (grind_stats, price_btccad) = recent((grind_stats, price_btccad),
                                             60 * 60)
        if grind_stats is None:
            return Widget._dummy_box("(no recent tx data)", theme)

        t_row = ['Block', "Txs", "UTXO Delta", 'MeanVin', 'MinVin', 'MedianVin',
                 'MaxVin', "MeanVout", "MinVout", "MedianVout",
                 "MaxVout"]
        rows = [t_row]
        for block in sorted(grind_stats.keys(), reverse=True):
            txs = grind_stats[block]['n_transactions']
            delta = grind_stats[block]['utxo_delta']
            meanin = int(grind_stats[block]['tx_n_vins']['mean'])
            minin = int(grind_stats[block]['tx_n_vins']['min'])
            medianin = int(grind_stats[block]['tx_n_vins']['median'])
            maxin = int(grind_stats[block]['tx_n_vins']['max'])
            meanout = int(grind_stats[block]['tx_n_vouts']['mean'])
            minout = int(grind_stats[block]['tx_n_vouts']['min'])
            medianout = int(grind_stats[block]['tx_n_vouts']['median'])
            maxout = int(grind_stats[block]['tx_n_vouts']['max'])
            rows.append([str(block),
                         "{:,}".format(txs),
                         "{:,}".format(delta),
                         "{:,}".format(meanin),
                         "{:,}".format(minin),
                         "{:,}".format(medianin),
                         "{:,}".format(maxin),
                         "{:,}".format(meanout),
                         "{:,}".format(minout),
                         "{:,}".format(medianout),
                         "{:,}".format(maxout),
                        ])
        rows = Widget.pad_align_cols(rows)
        lines = []
        lines.append(Widget._title_row(rows[0], theme))
        for row in rows[1:]:
            lines.append(Widget._row(row, theme))
        return Widget._line_pile_box(lines, "Transaction Vins/Vouts", theme)

    @staticmethod
    def input_output_types(grind_stats, price_btccad, theme):
        (grind_stats, price_btccad) = recent((grind_stats, price_btccad),
                                             60 * 60)
        if grind_stats is None:
            return Widget._dummy_box("(no recent tx data)", theme)

        t_row = ['Block', "Total In",
                 "1* In", "3* In", 'b32 In', 'b32s In',
                 "Total Out", "1* Out", "3* Out", 'b32 Out',
                 'b32s Out', 'OP_RETURN']
        rows = [t_row]
        for block in sorted(grind_stats.keys(), reverse=True):
            total_in = grind_stats[block]['n_inputs']
            opin = grind_stats[block]['1_prefixed_inputs']
            tpin = grind_stats[block]['3_prefixed_inputs']
            bc1in = grind_stats[block]['key_bc1_prefixed_inputs']
            sbcin = grind_stats[block]['script_bc1_prefixed_inputs']
            total_out = grind_stats[block]['n_outputs']
            opout = grind_stats[block]['1_prefixed_outputs']
            tpout = grind_stats[block]['3_prefixed_outputs']
            bc1out = grind_stats[block]['key_bc1_prefixed_outputs']
            sbcout = grind_stats[block]['script_bc1_prefixed_outputs']
            orout = grind_stats[block]['op_return_outputs']

            rows.append([str(block),
                         "{:,}".format(total_in),
                         "{:,}".format(opin),
                         "{:,}".format(tpin),
                         "{:,}".format(bc1in),
                         "{:,}".format(sbcin),
                         "{:,}".format(total_out),
                         "{:,}".format(opout),
                         "{:,}".format(tpout),
                         "{:,}".format(bc1out),
                         "{:,}".format(sbcout),
                         "{:,}".format(orout),
                        ])
        rows = Widget.pad_align_cols(rows)
        lines = []
        lines.append(Widget._title_row(rows[0], theme))
        for row in rows[1:]:
            lines.append(Widget._row(row, theme))
        return Widget._line_pile_box(lines, "Transaction Vins/Vouts", theme)

    @staticmethod
    def fees_paid(grind_stats, price_btccad, theme):
        (grind_stats, price_btccad) = recent((grind_stats, price_btccad),
                                             60 * 60)
        if grind_stats is None:
            return Widget._dummy_box("(no recent tx data)", theme)

        #import json
        #print(json.dumps(grind_stats, indent=1))
        t_row = ['Block', "Mean BTC", "Min BTC", "Median BTC", "Max BTC",
                 "Mean CAD", "Min CAD", "Median CAD", "Max CAD"]
        rows = [t_row]
        for block in sorted(grind_stats.keys(), reverse=True):
            meanbtc = grind_stats[block]['fees_paid']['mean']
            minbtc = grind_stats[block]['fees_paid']['min']
            medianbtc = grind_stats[block]['fees_paid']['median']
            maxbtc = grind_stats[block]['fees_paid']['max']
            meancad = grind_stats[block]['fees_paid']['mean'] * price_btccad
            mincad = grind_stats[block]['fees_paid']['min'] * price_btccad
            mediancad = grind_stats[block]['fees_paid']['median'] * price_btccad
            maxcad = grind_stats[block]['fees_paid']['max'] * price_btccad

            rows.append([str(block),
                         "%0.8f" % meanbtc,
                         "%0.8f" % minbtc,
                         "%0.8f" % medianbtc,
                         "%0.8f" % maxbtc,
                         "${:,.2f}".format(round(meancad, 2)),
                         "${:,.2f}".format(round(mincad, 2)),
                         "${:,.2f}".format(round(mediancad, 2)),
                         "${:,.2f}".format(round(maxcad, 2)),
                        ])
        rows = Widget.pad_align_cols(rows)
        lines = []
        lines.append(Widget._title_row(rows[0], theme))
        for row in rows[1:]:
            lines.append(Widget._row(row, theme))
        return Widget._line_pile_box(lines, "Transaction Fees Paid", theme)

    @staticmethod
    def date_and_time_box(timestamp, theme):
        timestr = datetime.fromtimestamp(timestamp).strftime(
            " %d/%m/%y %H:%M:%S ")
        markup = [("grey_minor_text", timestr)]
        t = urwid.Text(markup, align='center')
        return Widget._line_pile_box([t], "Time", theme)

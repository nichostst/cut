import time
from operator import add
from functools import reduce
from rectpack import newPacker
from utils import fig2buf

import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap
from matplotlib import patches
from itertools import permutations, product


class CustomPacker(object):
    def __init__(self, **kwargs):
        self.packer = newPacker(**kwargs)
        self.packed = False
        self.area = None
        self.remaining = None
        self.types = {}
        self.cuts = []

    def binpack(self, bins, types):
        self.cuts = []
        self.types = {tuple(sorted(x, reverse=True)): i+1 for i, x in enumerate(types.keys())}
        rectangles = reduce(add, [x*(i,) for i, x in types.items()])
        for r in rectangles:
            self.packer.add_rect(*r)

        for b in bins:
            self.packer.add_bin(*b)

        self.packer.pack()
        self.packed = True

        for _, abin in enumerate(self.packer):
            bw, bh  = abin.width, abin.height
            self.area = self.remaining = bw*bh
            for rect in abin:
                x, y, w, h = rect.x, rect.y, rect.width, rect.height
                self.remaining -= w*h
                self.cuts.append((x, y, w, h))

    def plot(self, **kwargs):
        output = []
        figs = []
        used_types = []
        n = len(self.types)
        cmap = get_cmap('viridis')
        for abin in self.packer:
            bw, bh  = abin.width, abin.height
            fig = plt.figure(**kwargs)
            ax = fig.add_subplot(111, aspect='equal')
            tiled = 0
            for rect in abin:
                x, y, w, h = rect.x, rect.y, rect.width, rect.height
                tiled += w*h
                output.append([x, y, w, h])
                # Get type number for coloring
                type_num = self.types[tuple(sorted((w, h), reverse=True))]
                plt.axis([0, bw, 0, bh])

                if type_num not in used_types:
                    patch = patches.Rectangle(
                        (x, y), w, h,
                        facecolor=cmap(type_num/n),
                        edgecolor="black",
                        linewidth=1,
                        label=type_num
                    )
                    used_types.append(type_num)
                else:
                    patch = patches.Rectangle(
                        (x, y), w, h,
                        facecolor=cmap(type_num/n),
                        edgecolor="black",
                        linewidth=1
                    )
                ax.add_patch(patch)
            figs.append(fig)
            plt.legend(bbox_to_anchor=(0.2, -0.2))

        return figs

def draw_packer(packer):
    figs = packer.plot(figsize=(3, 3))
    fig = figs[0]

    buf = fig2buf(fig)
    st.image(buf)
    st.download_button('Download', data=buf, file_name=f'{int(time.time())}.png')

def bin_permute(bins):
    # Store each 2-permutations of each bin
    perms = []
    if len(bins) > 1:
        for bin in bins:
            perms.append(permutations(bin))
        return product(perms)
    else:
        return [[x] for x in permutations(bins[0])]
    
def select_best(algos, bins, types, min_fill=0.8):
    results = []
    valid_algos = []
    bps = []
    vts = []

    binperms = bin_permute(bins)
    progress = st.progress(0.0)
    c = 0
    if len(bins) == 1:
        vtypes = valid_types(types, bins[0], min_fill)
        combs = product(algos, binperms, vtypes)
        ncombs = len(algos)*len(binperms)*len(vtypes)
        for algo, bp, vt in combs:
            try:
                packer = CustomPacker(pack_algo=algo)
                packer.binpack(bp, vt)

                valid_algos.append(algo)
                bps.append(bp)
                vts.append(vt)
                results.append(packer.remaining)
            except Exception as e:
                # print(e)
                pass
            c += 1
            progress.progress(c/ncombs)

        arg = np.argmin(results)
        return valid_algos[arg], bps[arg], vts[arg]
    else:
        raise NotImplementedError('Not implemented yet!')

def _get_area(types):
    return sum([x*y*i for (x, y), i in types.items()])

def valid_types(types, binsize, min_fill=0.8):
    '''
    Search valid types for single bin problem.
    '''
    total_area = _get_area(types)
    bin_area = binsize[0]*binsize[1]
    if total_area < bin_area:
        return [types]
    else:
        
        possible_cuts = []
        for (x, y), i in types.items():
            cut_area = x*y
            max_cuts = min(i, int(bin_area/cut_area))
            possible_cuts.append([(x, y, num_cuts) for num_cuts in range(max_cuts+1)])

        possible_cut_sets = [{(x, y): i for x, y, i in pcs} for pcs in product(*possible_cuts)]

        valid_cut_sets = []
        for pcs in possible_cut_sets:
            a = _get_area(pcs)
            ratio = a/bin_area
            if min_fill < ratio < 1:
                valid_cut_sets.append(pcs)
        return valid_cut_sets

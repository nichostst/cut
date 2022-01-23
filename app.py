import streamlit as st
import pandas as pd

from collections import Counter

from packer import draw_packer, select_best, CustomPacker
from table import get_state, TableEditor
from enums import (
    MAXRECT_ALGOS, SKYLINE_ALGOS, GUILLOTINE_ALGOS, TESTCASES, BIN_TESTCASES
)

testcase = 'D'
ALGOS = [*MAXRECT_ALGOS, *GUILLOTINE_ALGOS, *SKYLINE_ALGOS]

# st.info('INFO: Enter bin size in the sidebar.')
st.header('Stock Cut Calculator')
# st.caption('''Lorem ipsum dolor sit amet. Ligma balls.''')

st.markdown('---')
st.subheader('Editor')
st.caption('Enter the sizes of cuts and maximum number of cuts for each size.')
# Get state and initialize editor
state = get_state()

if state.data is None:
    state.data = TESTCASES[testcase]

start_binsize = BIN_TESTCASES[testcase]
# Input bin size
st.sidebar.header('Input Bin Size')
l = st.sidebar.number_input('Length', min_value=10.0, max_value=400.0, value=start_binsize[0], step=0.1, format="%.1f")
w = st.sidebar.number_input('Width',  min_value=10.0, max_value=400.0, value=start_binsize[1], step=0.1, format="%.1f")
bins = [(l, w)]

with st.expander('Open to see editor'):
    editor = TableEditor("Table", state.data)
    editor.interact()

# Check for button interactions and updates the internal data state
interacted = True
state.data = editor.data

st.caption('Current cuts:')
st.dataframe(state.data.style.format("{:.1f}", subset=['Length', 'Width']))

rot = st.checkbox(label='Allow rotation?', value=True, help='Uncheck if stock rotation is not allowed.')

st.markdown('*Click button below to get optimal stock cut*')
fig_update = st.button('Get Figure')

if fig_update:
    # Update state
    types = state.data.set_index(['Length', 'Width'])['Count'].to_dict()
    best_algo, bp, vt = select_best(algos=ALGOS, bins=bins, types=types)
    packer = CustomPacker(pack_algo=best_algo, rotation=rot)
    packer.binpack(bp, vt)

    # Get cuts
    cuts = Counter([tuple(sorted(x[2:], reverse=True)) for x in packer.cuts])
    ser = pd.Series(cuts).rename_axis(['Length', 'Width'])
    ser = ser.rename('count').reset_index()
    ser['type'] = ser[['Length', 'Width']].apply(lambda x: packer.types[tuple(sorted(x, reverse=True))], axis=1)

    # Stats
    st.subheader('Result')
    with st.expander('Open to see results'):
        area = packer.area
        rem = packer.remaining
        usage = area - rem
        to_pack = sum(state.data['Length']*state.data['Width']*state.data['Count'])
        usage_pct = round(100*usage/area, 2)
        packed_pct = round(100*usage/to_pack, 2)

        cols = st.columns(3)
        cols[0].metric('Used', f'{usage_pct:.2f}%')
        cols[1].metric('Remaining', f'{rem:.2f} cm2')
        cols[2].metric('Packed', f'{packed_pct:.2f}%')

        # Output
        st.dataframe(ser.set_index('type').style.format("{:.1f}", subset=['Length', 'Width']))
        draw_packer(packer)

        st.write(pd.DataFrame(packer.cuts, columns=['x', 'y', 'w', 'h']).round(1).style.format("{:.1f}"))

state.sync()
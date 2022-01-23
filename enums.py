from rectpack.maxrects import MaxRectsBl, MaxRectsBlsf, MaxRectsBaf, MaxRectsBssf
from rectpack.guillotine import (
    GuillotineBafMinas, GuillotineBafMaxas, GuillotineBafLlas, GuillotineBaf,
    GuillotineBafLas, GuillotineBafSas, GuillotineBafSlas, GuillotineBlsf, GuillotineBlsfLas,
    GuillotineBlsfLlas, GuillotineBlsfMaxas, GuillotineBlsfMinas, GuillotineBlsfSas,
    GuillotineBlsfSlas, GuillotineBssf, GuillotineBssfLas, GuillotineBssfLlas,
    GuillotineBssfMaxas, GuillotineBssfMinas, GuillotineBssfSas, GuillotineBssfSlas,
    GuillotineLas, GuillotineLlas, GuillotineMaxas, GuillotineMinas, GuillotineSas,
    GuillotineSlas
)
from rectpack.skyline import (
    SkylineBl, SkylineMwflWm, SkylineBlWm, SkylineMwf, SkylineMwfl, SkylineMwfWm
)
import pandas as pd


MAXRECT_ALGOS = [MaxRectsBl, MaxRectsBlsf, MaxRectsBaf, MaxRectsBssf]

GUILLOTINE_ALGOS = [
    GuillotineBafMinas, GuillotineBafMaxas, GuillotineBafLlas, GuillotineBaf,
    GuillotineBafLas, GuillotineBafSas, GuillotineBafSlas, GuillotineBlsf, GuillotineBlsfLas,
    GuillotineBlsfLlas, GuillotineBlsfMaxas, GuillotineBlsfMinas, GuillotineBlsfSas,
    GuillotineBlsfSlas, GuillotineBssf, GuillotineBssfLas, GuillotineBssfLlas,
    GuillotineBssfMaxas, GuillotineBssfMinas, GuillotineBssfSas, GuillotineBssfSlas,
    GuillotineLas, GuillotineLlas, GuillotineMaxas, GuillotineMinas, GuillotineSas,
    GuillotineSlas
]

SKYLINE_ALGOS = [
    SkylineBl, SkylineMwflWm, SkylineBlWm, SkylineMwf, SkylineMwfl, SkylineMwfWm
]

TESTCASES = {
    'A': pd.DataFrame({
        'Length': [59.0, 39.5, 120.0, 88.7], 'Width': [34.0, 19.7, 0.3, 2], 'Count':[4, 4, 2, 2]
    }),
    'B': pd.DataFrame({
        'Length': [39.0, 31.0, 19.7], 'Width': [39.0, 30.0, 39.5], 'Count':[5, 5, 5]
    }),
    'C': pd.DataFrame({
        'Length': [39.5, 39.5], 'Width': [23.0, 19.7], 'Count':[6, 6]
    }),
    'D': pd.DataFrame({
        'Length': [36.0], 'Width': [19.7], 'Count':[15]
    }),
    'E': pd.DataFrame({
        'Length': [40.0], 'Width': [29.6], 'Count':[15]
    }),
}

BIN_TESTCASES = {
    'A': (89.0, 120.0),
    'B': (90.0, 120.0),
    'C': (79.0, 109.0),
    'D': (79.0, 109.0),
    'E': (89.0, 120.0)
}
import numbers
import json
import pandas as pd
import streamlit as st
from streamlit.report_thread import get_report_ctx
from streamlit.server.server import Server


class TableEditor:
    """Encapsulates editable tables using streamlit.
    Usage:
    >>> original_df = pd.DataFrame(...)
    >>> editor = TableEditor("editor uid", original_df)
    >>> editor.interact()
    >>> edited_df = editor.data
    """
    def __init__(self, uid, dataframe, layout=None):
        """Initialize TableEditor instance.
        Args:
            uid (str): Table unique identifier to avoid widget key conflict.
            dataframe (pandas.DataFrame): Data to be edited.
            layout (list, optional): List of column proportions. See
            https://docs.streamlit.io/en/stable/api.html#streamlit.beta_columns.
            Defaults to None.
        """
        self._uid = uid
        self._data = dataframe.copy()
        self._n_rows = dataframe.shape[0]
        self._n_cols = dataframe.shape[1]
        self._cells = {}
        self._update_button = None
        self._add_row_button = None
        self._delete_buttons = {}
        if layout is None:
            # If layout not defined the dataframe columns will be 5 times bigger
            # than Delete buttons column
            layout = st.columns(
                [5 if col < self._n_cols else 1 for col in range(self._n_cols + 1)]
            )
        self._layout = layout
        self._create_table()
        self._create_buttons()

    @property
    def data(self):
        return self._data

    def interact(self):
        if self._update_button:
            self._update()

        if self._add_row_button:
            self._add_row()
            self._update()

        for key, button in self._delete_buttons.items():
            if button:
                # key[1] is always the row index
                self._delete_row(key[1])
                break

    def _create_table(self):
        # Gets only layout columns to put actual data from dataframe - indices [0:n_cols]
        data_columns = self._layout[:self._n_cols]

        for col_index, column in enumerate(data_columns):
            # Writes column names
            column.markdown(f"**{self._data.columns[col_index]}**")
            for row_index in range(self._n_rows):
                key = (self._uid, col_index, row_index)
                with column:
                    self._add_cell(key, self._data.iloc[row_index, col_index])


    def _create_delete_button(self):
        # Always the last column in column layout
        button_del_column = self._layout[self._n_cols]

        # The buttons are not horizontally aligned with input widgets, so we need this little hack
        button_del_column.markdown("<div style='margin-top:5em;'></div>", unsafe_allow_html=True)

        for row_index in range(self._n_rows):
            key = (self._uid, row_index)
            self._delete_buttons[key] = button_del_column.button("Delete", key=str(key))
            button_del_column.markdown(
                "<div style='margin-top:2.73em;'></div>", unsafe_allow_html=True
            )

    def _create_buttons(self):
        self._create_delete_button()
        self._add_row_button = st.button("Add Row", key=f"add_row_button_{self._uid}")
        self._update_button = st.button(label="Update Data", key=f"update_button_{self._uid}")

    def _update(self):
        for col_index in range(self._n_cols):
            for row_index in range(self._n_rows):
                new_value = self._cells[(self._uid, col_index, row_index)].value
                self._data.iloc[row_index, col_index] = new_value
        self._data = self._data.sort_values(by=self._data.columns.to_list(), ignore_index=True)

    def _add_row(self):
        columns = self._data.columns.to_list()
        values = [[1] for _ in columns]
        row = pd.DataFrame(dict(zip(columns, values)))
        self._data = self._data.append(row).reset_index(drop=True)

        for col_index in range(self._n_cols):
            row_index = self._n_rows
            key = (self._uid, col_index, row_index)
            with(self._layout[col_index]):
                self._add_cell(key, self._data.iloc[row_index, col_index])

    def _delete_row(self, row_index):
        self._data = self._data.drop([row_index]).reset_index(drop=True)
        for col_index in range(self._n_cols):
            key = (self._uid, col_index, row_index)
            self._delete_cell(key)

    def _add_cell(self, key, value):
        new_cell = _Cell(key)
        new_cell.value = value
        self._cells[key] = new_cell

    def _delete_cell(self, key):
        del self._cells[key]


class _Cell:
    def __init__(self, uid):
        self._uid = uid
        self._value = None
        self._widget = st.empty()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if isinstance(value, numbers.Integral):
            self._value = self._widget.number_input(
                label="",
                value=value,
                min_value=1,
                step=1,
                key=self._uid
            )
        elif isinstance(value, float):
            self._value = self._widget.number_input(
                label="",
                value=value,
                min_value=0.,
                step=0.1,
                format="%.1f",
                key=self._uid
            )
        else:
            self._value = self._widget.text_input(
                label="",
                value=value,
                key=self._uid
            )

class _SessionState:

    def __init__(self, session):
        """Initialize SessionState instance."""
        self.__dict__["_state"] = {
            "data": {},
            "hash": None,
            "is_rerun": False,
            "session": session,
        }

    def __call__(self, **kwargs):
        """Initialize state data once."""
        for item, value in kwargs.items():
            if item not in self._state["data"]:
                self._state["data"][item] = value

    def __getitem__(self, item):
        """Return a saved state value, None if item is undefined."""
        return self._state["data"].get(item, None)

    def __getattr__(self, item):
        """Return a saved state value, None if item is undefined."""
        return self._state["data"].get(item, None)

    def __setitem__(self, item, value):
        """Set state value."""
        self._state["data"][item] = value

    def __setattr__(self, item, value):
        """Set state value."""
        self._state["data"][item] = value

    def clear(self):
        """Clear session state and request a rerun."""
        self._state["data"].clear()

    def sync(self):
        """Rerun the app with all state values up to date from the beginning to fix rollbacks."""

        # Ensure to rerun only once to avoid infinite loops
        # caused by a constantly changing state value at each run.
        #
        # Example: state.value += 1
        if self._state["is_rerun"]:
            self._state["is_rerun"] = False

        elif self._state["hash"] is not None:
            if self._state["hash"] != json.dumps(self._state['data']['data'].to_dict(), sort_keys=True):
                self._state["is_rerun"] = True

        self._state["hash"] = json.dumps(self._state['data']['data'].to_dict(), sort_keys=True)


def _get_session():
    session_id = get_report_ctx().session_id
    session_info = Server.get_current()._get_session_info(session_id)

    if session_info is None:
        raise RuntimeError("Couldn't get your Streamlit Session object.")

    return session_info.session


def get_state():
    session = _get_session()

    if not hasattr(session, "_custom_session_state"):
        session._custom_session_state = _SessionState(session)

    return session._custom_session_state
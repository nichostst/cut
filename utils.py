import io

def fig2buf(fig):
    """
    Convert a Matplotlib figure to a buffer
    """
    buf = io.BytesIO()
    fig.savefig(buf)
    buf.seek(0)
    return buf
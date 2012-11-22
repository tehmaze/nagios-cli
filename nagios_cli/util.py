import os
import stat
import pwd
import shlex
import time
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

QUOTE_CHARS = ['"', "'"]
SEEK_SET, SEEK_CUR, SEEK_END = range(0, 3)

def get_username():
    uid = os.geteuid()
    try:
        return pwd.getpwuid(uid).pw_name
    except:
        return uid

def token_split(text, quote_chars=QUOTE_CHARS):
    for char in [''] + quote_chars:
        try:
            return shlex.split(text + char)
        except ValueError:
            pass

    raise ValueError, "Quotation mismatch"

def tail(filename, wait=0.1, seek=0):
    st = os.stat(filename)
    fp = open(filename, 'rb')

    # Seek to the end
    if seek <= 0:
        fp.seek(abs(seek), 2)
    else:
        fp.seek(seek)

    # Read until file is truncated, collect results in a string buffer
    size = st[stat.ST_SIZE]
    line = StringIO()
    while True:
        char = fp.read(1)

        # Check if there was something for us to collect
        if char == '':
            st = os.stat(filename)
            if st[stat.ST_SIZE] < size:
                # File truncated
                break
            else:
                try:
                    time.sleep(wait)
                except:
                    break
        else:
            line.write(char)
            # Yield lines
            if char == '\n':
                yield line.getvalue()
                line.seek(0)
                line.truncate()

    fp.close()

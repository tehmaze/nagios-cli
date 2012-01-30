import os
import pwd
import shlex

QUOTE_CHARS = ['"', "'"]

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

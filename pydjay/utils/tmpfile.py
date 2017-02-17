
import os
import tempfile


_tmp_dir = os.path.abspath(os.path.expanduser("~/.pydjay/tmp"))
_tmp_files = []


if not os.path.exists(_tmp_dir):
    os.makedirs(_tmp_dir)

def new_temp_file(prefix = 'tmp', extension = ""):
    foo, name = tempfile.mkstemp(prefix = prefix, suffix = extension, dir=_tmp_dir)
    #foo.close()
    _tmp_files.append(name)
    return name


def cleanup():
    print 'CLEANING UP'
    pass

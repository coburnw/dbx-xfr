# dbx-xfr
Dead simple dropbox file transfer library in Python

# Description
A dead simple (and brain dead) python library for getting and putting files on Dropbox.  Heavily leans on the example code found in the dropbox [python api](https://github.com/dropbox/dropbox-sdk-python)

# Dependencies
pip3 install dropbox

# Example
    import dbx_xfr
    
    filename = 'junk.txt'
    
    with dbx_xfr.AWDropBox() as awd:
        if not awd.status():
            print('Failed to connect to dropbox')
            exit()

        awd.put(filename)

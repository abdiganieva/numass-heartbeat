import os

# Check status
class Status:
    # File passed the check
    OK = 0
    # File is empty (0 bytes)
    EMPTY = 1
    EMPTY_CANDIDATE = 101
    # The header is damaged or incomplete
    INVALID_HEADER = 2
    INVALID_HEADER_CANDIDATE = 102
    # File is not empty, but does not contain any data
    EMPTY_DATA = 3
    # Acquisition stopped in the middle of the file
    ACQ_STOPPED = 4
    ACQ_STOPPED_CANDIDATE = 104
    # File has data, but it looks corrupted
    SUS_DATA = 5
    SUS_DATA_CANDIDATE = 105

def check(filename):
    if os.stat(filename).st_size == 0:
        return Status.EMPTY
    try:
        header, meta, data = envelope_parser.parse_from_file(filename)
    except BaseException as error:
        return Status.INVALID_HEADER
    
    if header['data_len'] == 0:
        return Status.EMPTY_DATA
    
    Point = dfparser.Point()
    message = Point.ParseFromString(data)
    
    frames = get_raw(Point)
    if len(frames) < 7:
        return Status.ACQ_STOPPED
    
    return Status.OK

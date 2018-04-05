from boa.interop.Neo.Blockchain import GetHeight, GetHeader
from boa.interop.Neo.Header import GetTimestamp


# Get unix time form block header
def get_now():
    height = GetHeight()
    current_block = GetHeader(height)
    return current_block.Timestamp

def ip_to_long (ip):
    """
    Convert ip address to a network byte order 32-bit integer.
   """
    quad = ip.split('.')
    if len(quad) == 1:
        quad = quad + [0, 0, 0]
    elif len(quad) < 4:
        host = quad[-1:]
        quad = quad[:-1] + [0,] * (4 - len(quad)) + host

    lip = 0
    for q in quad:
        lip = (lip << 8) | int(q)
    return lip


def long_to_ip (l):
    """
    Convert 32-bit integerto to a ip address.
    """
    return '%d.%d.%d.%d' % (l>>24 & 255, l>>16 & 255, l>>8 & 255, l & 255) 




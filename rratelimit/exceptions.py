class UnsupportedRedisVersion(ValueError):
    def __init__(self, version):
        message = ("rratelimit requires redis-server >= 2.6.0, version {}"
                   " currently installed".format(version))
        ValueError.__init__(self, message)

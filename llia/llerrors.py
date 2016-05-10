# llia.llerrors
# 2016.05.10

class LliaError(Exception):

    def __init__(self, msg=""):
        super(LliaError, self).__init__(msg)

class LliaPingError(LliaError):

    def __init__(self, msg=""):
        super(LliaPingError, self).__init__(msg)

class LliascriptError(LliaError):

    def __init__(self, msg=""):
        super(LliascriptError, self).__init__(msg)

class LliascriptParseError(LliascriptError):

    def __init__(self, msg=""):
        super(LliascriptParseError, self).__init__(msg)

class NoSuchBusError(LliascriptError):

    def __init__(self, msg=""):
        super(NoSuchBusError, self).__init__(msg)
                        
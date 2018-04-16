class UnsupportedFieldException(Exception):
    """
    Raised when an attempt is made to convert a field that we don't understand.
    """
    def __init__(self, field_class):
        self.message = "Field %s is not supported." % field_class

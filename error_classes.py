class ParserError(Exception):
    pass


class HubMetadataError(ParserError):
    pass


class ConnectionMetadataError(ParserError):
    pass


class HubFormatError(ParserError):
    pass


class Grapherror(Exception):
    pass

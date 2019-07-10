class ImageExpiredError(Exception):
    MESSAGE = "(35, 'gnutls_handshake() failed: An unexpected TLS handshake packet was received.')"

    @staticmethod
    def catch(other):
        if str(other) == ImageExpiredError.MESSAGE:
            return True
        return False


class NotInCatalogError(Exception):
    MESSAGE = "Could not find a catalog entry for the given id"

    @staticmethod
    def catch(other):
        if str(other).startswith(NotInCatalogError.MESSAGE):
            return True
        return False

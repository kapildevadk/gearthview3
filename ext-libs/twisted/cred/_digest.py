# -*- test-case-name: twisted.test.test_digestauth -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Calculations for HTTP Digest authentication.

@see: U{http://www.faqs.org/rfcs/rfc2617.html}
"""

from typing import Any, BinaryIO, Optional

import hashlib


algorithms = {
    "md5": hashlib.md5,
    "md5-sess": hashlib.md5,
    "sha": hashlib.sha1,
}


def calcHA1(
    algo: str,
    user_name: Optional[str],
    realm: Optional[str],
    password: Optional[str],
    nonce: Optional[str],
    cnonce: Optional[str],
    preHA1: Optional[str] = None,
) -> str:
    """
    Compute H(A1) from RFC 2617.

    @param algo: The name of the algorithm to use to calculate the digest.
        Currently supported are md5, md5-sess, and sha.
    @param user_name: The username
    @param realm: The realm
    @param password: The password
    @param nonce: The nonce
    @param cnonce: The cnonce
    @param preHA1: If available this is a str containing a previously
        calculated H(A1) as a hex string. If this is given then the values for
        user_name, realm, and password must be C{None} and are ignored.
    """
    if preHA1 and (user_name or realm or password):
        raise ValueError("preHA1 is incompatible with the user_name, " "realm, and password arguments")

    if preHA1 is None:
        m = algorithms[algo]()
        m.update(user_name.encode())
        m.update(b":")
        m.update(realm.encode())
        m.update(b":")
        m.update(password.encode())
        HA1 = m.digest()
    else:
        HA1 = bytes.fromhex(preHA1)

    if algo == "md5-sess":
        m = algorithms[algo]()
        m.update(HA1)
        m.update(nonce.encode())
        m.update(b":")
        m.update(cnonce.encode())
        HA1 = m.digest()

    return HA1.hex()


def calcHA2(
    algo: str, method: str, digest_uri: str, qop: str, entity: Optional[BinaryIO] = None
) -> str:
    """
    Compute H(A2) from RFC 2617.

    @param algo: The name of the algorithm to use to calculate the digest.
        Currently supported are md5, md5-sess, and sha.
    @param method: The request method.
    @param digest_uri: The request URI.
    @param qop: The Quality-of-Protection value.
    @param entity: The entity body or C{None} if C{qop} is not C{'auth-int'}.
    @return: The hash of the A2 value for the calculation of the response
        digest.
    """
    m = algorithms[algo]()
    m.update(method.encode())
    m.update(b":")
    m.update(digest_uri.encode())

    if qop == "auth-int":
        entity_data = entity.read()
        m.update(b":")
        m.update(hashlib.md5(entity_data).digest())

    return m.digest().hex()


def calcHEntity(entity: BinaryIO) -> str:
    """
    Compute H(entity) for auth-int qop.

    @param entity: The entity body.
    @return: The hash of the entity body.
    """
    return hashlib.md5(entity.read()).hexdigest()


def calcResponse(
    HA1: str,
    HA2: str,
    algo: str,
    nonce: str,
    nonce_count: str,
    cnonce: str,
    qop: str,
) -> str:
    """
    Compute the digest for the given parameters.

    @param HA1: The H(A1) value, as computed by L{calcHA1}.
    @param HA2: The H(A2) value, as computed by L{calcHA2}.
    @param algo: The name of the algorithm to use to calculate the digest.
        Currently supported are md5, md5-sess, and sha.
    @param nonce: The challenge nonce.
    @param nonce_count: The (client) nonce count value for this response.
    @param cnonce: The client nonce.
    @param qop: The Quality-of-Protection value.
    """
    m = algorithms[algo]()
    m.update(HA1.encode())
    m.update(b":")
    m.update(nonce.encode())
    m.update(b":")

    if nonce_count and cnonce:
        m.update(nonce_count.encode())
        m.update(b":")
        m.update(cnonce.encode())
        m.update(b":")
        m.update(qop.encode())
        m.update(b":")

    m.update(HA2.encode())
    resp_hash = m.digest()
    return resp_hash.hex()

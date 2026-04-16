from dataclasses import FrozenInstanceError
from orionis.test import TestCase
from orionis.foundation.config.http.entitites.http import HTTP
from orionis.foundation.config.http.entitites.cors import Cors
from orionis.foundation.config.http.entitites.proxies import HTTPProxies
from orionis.foundation.config.http.entitites.rate_limit import HTTPRateLimit
from orionis.foundation.config.http.entitites.request import HTTPRequest
from orionis.foundation.config.http.entitites.security import HTTPSecurity

# ===========================================================================
# HTTP entity
# ===========================================================================


class TestHTTP(TestCase):

    def testDefaultConstruction(self) -> None:
        """
        Construct HTTP with all default values.

        Verifies that an HTTP instance can be created without providing
        any arguments.

        Returns
        -------
        None
            This method does not return a value.
        """
        http = HTTP()
        self.assertIsInstance(http, HTTP)

    def testDefaultProxiesIsHTTPProxiesInstance(self) -> None:
        """
        Verify proxies defaults to an HTTPProxies instance.

        Ensures the composite proxies field is properly initialised
        with its entity type.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(HTTP().proxies, HTTPProxies)

    def testDefaultSecurityIsHTTPSecurityInstance(self) -> None:
        """
        Verify security defaults to an HTTPSecurity instance.

        Ensures the composite security field is properly initialised
        with its entity type.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(HTTP().security, HTTPSecurity)

    def testDefaultRateLimitIsHTTPRateLimitInstance(self) -> None:
        """
        Verify rate_limit defaults to an HTTPRateLimit instance.

        Ensures the composite rate_limit field is properly initialised
        with its entity type.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(HTTP().rate_limit, HTTPRateLimit)

    def testDefaultRequestIsHTTPRequestInstance(self) -> None:
        """
        Verify request defaults to an HTTPRequest instance.

        Ensures the composite request field is properly initialised
        with its entity type.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(HTTP().request, HTTPRequest)

    def testDefaultCorsIsCorsInstance(self) -> None:
        """
        Verify cors defaults to a Cors instance.

        Ensures the composite cors field is properly initialised with
        its entity type.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(HTTP().cors, Cors)

    def testProxiesDictConversion(self) -> None:
        """
        Coerce a dict for proxies to an HTTPProxies instance.

        Verifies that passing an empty dict for proxies results in
        a properly constructed HTTPProxies instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        http = HTTP(proxies={})
        self.assertIsInstance(http.proxies, HTTPProxies)

    def testSecurityDictConversion(self) -> None:
        """
        Coerce a dict for security to an HTTPSecurity instance.

        Verifies that passing an empty dict for security results in
        a properly constructed HTTPSecurity instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        http = HTTP(security={})
        self.assertIsInstance(http.security, HTTPSecurity)

    def testRateLimitDictConversion(self) -> None:
        """
        Coerce a dict for rate_limit to an HTTPRateLimit instance.

        Verifies that passing an empty dict for rate_limit results in
        a properly constructed HTTPRateLimit instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        http = HTTP(rate_limit={})
        self.assertIsInstance(http.rate_limit, HTTPRateLimit)

    def testRequestDictConversion(self) -> None:
        """
        Coerce a dict for request to an HTTPRequest instance.

        Verifies that passing an empty dict for request results in
        a properly constructed HTTPRequest instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        http = HTTP(request={})
        self.assertIsInstance(http.request, HTTPRequest)

    def testCorsDictConversion(self) -> None:
        """
        Coerce a dict for cors to a Cors instance.

        Verifies that passing an empty dict for cors results in
        a properly constructed Cors instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        http = HTTP(cors={})
        self.assertIsInstance(http.cors, Cors)

    def testInvalidProxiesTypeRaisesTypeError(self) -> None:
        """
        Raise TypeError when proxies is not an HTTPProxies or dict.

        Verifies that a string value triggers a TypeError during
        construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            HTTP(proxies="bad")  # type: ignore[arg-type]

    def testInvalidSecurityTypeRaisesTypeError(self) -> None:
        """
        Raise TypeError when security is not an HTTPSecurity or dict.

        Verifies that an integer value triggers a TypeError during
        construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            HTTP(security=42)  # type: ignore[arg-type]

    def testInvalidRateLimitTypeRaisesTypeError(self) -> None:
        """
        Raise TypeError when rate_limit is not an HTTPRateLimit or dict.

        Verifies that a list value triggers a TypeError during
        construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            HTTP(rate_limit=[])  # type: ignore[arg-type]

    def testInvalidRequestTypeRaisesTypeError(self) -> None:
        """
        Raise TypeError when request is not an HTTPRequest or dict.

        Verifies that a tuple value triggers a TypeError during
        construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            HTTP(request=())  # type: ignore[arg-type]

    def testInvalidCorsTypeRaisesTypeError(self) -> None:
        """
        Raise TypeError when cors is not a Cors or dict.

        Verifies that a boolean value triggers a TypeError during
        construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            HTTP(cors=True)  # type: ignore[arg-type]

    def testFrozenRaisesAttributeError(self) -> None:
        """
        Raise FrozenInstanceError when mutating an HTTP instance.

        Confirms the dataclass is immutable and rejects attribute
        reassignment after construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        http = HTTP()
        with self.assertRaises(FrozenInstanceError):
            http.cors = Cors()  # type: ignore[misc]

    def testToDictReturnsDict(self) -> None:
        """
        Verify toDict returns a plain dictionary representation.

        Ensures the inherited toDict helper converts the HTTP instance
        to a dict containing all composite section keys.

        Returns
        -------
        None
            This method does not return a value.
        """
        result = HTTP().toDict()
        self.assertIsInstance(result, dict)
        for key in ("proxies", "security", "rate_limit", "request", "cors"):
            self.assertIn(key, result)

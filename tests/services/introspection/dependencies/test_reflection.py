import inspect
from typing import Any
from orionis.test import TestCase
from orionis.services.introspection.dependencies.reflection import (
    ReflectDependencies,
)
from orionis.services.introspection.dependencies.entities.argument import Argument
from orionis.services.introspection.dependencies.entities.signature import (
    Signature,
)

# ---------------------------------------------------------------------------
# Target fixtures used across multiple test classes
# ---------------------------------------------------------------------------

class _NoArgs:
    """Class with a no-argument constructor (only self)."""

    def __init__(self) -> None:  # noqa: D107
        pass

class _AllResolved:
    """Class whose constructor uses only type-annotated, non-builtin params."""

    def __init__(self, dep: "_AllResolved") -> None:  # noqa: D107
        self.dep = dep

class _WithDefault:
    """Class whose constructor has a parameter with a default value."""

    def __init__(self, value: int = 10) -> None:  # noqa: D107
        self.value = value

class _WithBuiltin:
    """Class whose constructor has a bare builtin-typed parameter."""

    def __init__(self, name: str) -> None:  # noqa: D107
        self.name = name

class _Unannotated:
    """Class whose constructor has a completely unannotated parameter."""

    def __init__(self, x) -> None:  # noqa: ANN001, D107
        self.x = x

class _Mixed:
    """
    Class with a mix of annotated and default-valued constructor params.
    """

    def __init__(
        self,
        dep: "_Mixed",
        name: str,
        count: int = 0,
    ) -> None:  # noqa: D107
        self.dep = dep
        self.name = name
        self.count = count

    def process(self, value: int, mode: str = "fast") -> str:
        """
        Return a string combining value and mode.

        Parameters
        ----------
        value : int
            Numeric value to process.
        mode : str, optional
            Processing mode, by default 'fast'.

        Returns
        -------
        str
            Formatted result string.
        """
        return f"{value}-{mode}"

class _KeywordOnly:
    """Class whose constructor has keyword-only parameters."""

    def __init__(self, *, label: str, count: int = 0) -> None:  # noqa: D107
        self.label = label
        self.count = count

def _plain_function(a: int, b: str = "hello") -> str:
    """
    Return a concatenation of a and b.

    Parameters
    ----------
    a : int
        Integer operand.
    b : str, optional
        String operand, by default 'hello'.

    Returns
    -------
    str
        String combining both arguments.
    """
    return f"{a}-{b}"

async def _async_function(x: int) -> int: # NOSONAR
    """
    Return x unchanged (async fixture).

    Parameters
    ----------
    x : int
        Input value.

    Returns
    -------
    int
        Same value as x.
    """
    return x

# ---------------------------------------------------------------------------
# ReflectDependencies — constructor
# ---------------------------------------------------------------------------

class TestReflectDependenciesInit(TestCase):

    def testInitWithNoneTarget(self) -> None:
        """
        Assert that ReflectDependencies accepts None as a valid target.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        rd = ReflectDependencies(None)
        self.assertIsInstance(rd, ReflectDependencies)

    def testInitWithClassTarget(self) -> None:
        """
        Assert that ReflectDependencies accepts a class as its target.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        rd = ReflectDependencies(_Mixed)
        self.assertIsInstance(rd, ReflectDependencies)

    def testInitWithCallableTarget(self) -> None:
        """
        Assert that ReflectDependencies accepts a plain function as target.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        rd = ReflectDependencies(_plain_function)
        self.assertIsInstance(rd, ReflectDependencies)

    def testInitWithNoArgs(self) -> None:
        """
        Assert that ReflectDependencies can be instantiated without arguments.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        rd = ReflectDependencies()
        self.assertIsInstance(rd, ReflectDependencies)

# ---------------------------------------------------------------------------
# constructorSignature
# ---------------------------------------------------------------------------

class TestConstructorSignatureNoArgs(TestCase):

    def setUp(self) -> None:
        """
        Prepare a ReflectDependencies instance wrapping _NoArgs.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.rd = ReflectDependencies(_NoArgs)

    def testReturnsSignature(self) -> None:
        """
        Assert that constructorSignature returns a Signature instance.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.rd.constructorSignature(), Signature)

    def testOrderedIsEmpty(self) -> None:
        """
        Assert that ordered is empty when constructor has no parameters.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = self.rd.constructorSignature()
        self.assertEqual(sig.ordered, {})

    def testNoArgumentsRequiredIsTrue(self) -> None:
        """
        Assert that noArgumentsRequired returns True for a no-arg constructor.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = self.rd.constructorSignature()
        self.assertTrue(sig.noArgumentsRequired())

    def testHasUnresolvedArgumentsIsFalse(self) -> None:
        """
        Assert that hasUnresolvedArguments is False for a no-arg constructor.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = self.rd.constructorSignature()
        self.assertFalse(sig.hasUnresolvedArguments())

class TestConstructorSignatureWithDefault(TestCase):

    def setUp(self) -> None:
        """
        Prepare a ReflectDependencies instance wrapping _WithDefault.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.rd = ReflectDependencies(_WithDefault)

    def testValueIsInResolved(self) -> None:
        """
        Assert that the 'value' parameter appears in resolved dependencies.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = self.rd.constructorSignature()
        self.assertIn("value", sig.resolved)

    def testValueIsInOrdered(self) -> None:
        """
        Assert that the 'value' parameter appears in ordered dependencies.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = self.rd.constructorSignature()
        self.assertIn("value", sig.ordered)

    def testValueIsNotInUnresolved(self) -> None:
        """
        Assert that the 'value' parameter is absent from unresolved.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = self.rd.constructorSignature()
        self.assertNotIn("value", sig.unresolved)

    def testArgumentHasCorrectDefault(self) -> None:
        """
        Assert that the Argument for 'value' stores 10 as its default.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = self.rd.constructorSignature()
        self.assertEqual(sig.resolved["value"].default, 10)

    def testArgumentIsResolvedTrue(self) -> None:
        """
        Assert that the Argument for 'value' has resolved set to True.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = self.rd.constructorSignature()
        self.assertTrue(sig.resolved["value"].resolved)

class TestConstructorSignatureWithBuiltin(TestCase):

    def setUp(self) -> None:
        """
        Prepare a ReflectDependencies instance wrapping _WithBuiltin.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.rd = ReflectDependencies(_WithBuiltin)

    def testNameIsInUnresolved(self) -> None:
        """
        Assert that a builtin-typed parameter ends up in unresolved.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = self.rd.constructorSignature()
        self.assertIn("name", sig.unresolved)

    def testNameIsNotInResolved(self) -> None:
        """
        Assert that a builtin-typed parameter is absent from resolved.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = self.rd.constructorSignature()
        self.assertNotIn("name", sig.resolved)

    def testArgumentIsResolvedFalse(self) -> None:
        """
        Assert that the Argument for 'name' has resolved set to False.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = self.rd.constructorSignature()
        self.assertFalse(sig.unresolved["name"].resolved)

    def testArgumentClassNameIsStr(self) -> None:
        """
        Assert that the Argument for 'name' records 'str' as class_name.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = self.rd.constructorSignature()
        self.assertEqual(sig.unresolved["name"].class_name, "str")

class TestConstructorSignatureUnannotated(TestCase):

    def setUp(self) -> None:
        """
        Prepare a ReflectDependencies instance wrapping _Unannotated.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.rd = ReflectDependencies(_Unannotated)

    def testXIsInUnresolved(self) -> None:
        """
        Assert that an unannotated parameter appears in unresolved.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = self.rd.constructorSignature()
        self.assertIn("x", sig.unresolved)

    def testXIsNotInResolved(self) -> None:
        """
        Assert that an unannotated parameter is absent from resolved.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = self.rd.constructorSignature()
        self.assertNotIn("x", sig.resolved)

    def testArgumentResolvedIsFalse(self) -> None:
        """
        Assert that the Argument for 'x' has resolved set to False.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = self.rd.constructorSignature()
        self.assertFalse(sig.unresolved["x"].resolved)

class TestConstructorSignatureMixed(TestCase):

    def setUp(self) -> None:
        """
        Prepare a ReflectDependencies instance wrapping _Mixed.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.rd = ReflectDependencies(_Mixed)

    def testDepIsInResolved(self) -> None:
        """
        Assert that the non-builtin annotated 'dep' param is in resolved.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = self.rd.constructorSignature()
        self.assertIn("dep", sig.resolved)

    def testNameIsInUnresolved(self) -> None:
        """
        Assert that the builtin-typed 'name' param is in unresolved.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = self.rd.constructorSignature()
        self.assertIn("name", sig.unresolved)

    def testCountIsInResolved(self) -> None:
        """
        Assert that the default-valued 'count' param is in resolved.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = self.rd.constructorSignature()
        self.assertIn("count", sig.resolved)

    def testOrderedHasThreeKeys(self) -> None:
        """
        Assert that ordered contains exactly three entries for _Mixed.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = self.rd.constructorSignature()
        self.assertEqual(len(sig.ordered), 3)

# ---------------------------------------------------------------------------
# methodSignature
# ---------------------------------------------------------------------------

class TestMethodSignature(TestCase):

    def setUp(self) -> None:
        """
        Prepare a ReflectDependencies instance wrapping _Mixed.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.rd = ReflectDependencies(_Mixed)

    def testReturnsSignature(self) -> None:
        """
        Assert that methodSignature returns a Signature instance.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.rd.methodSignature("process"), Signature)

    def testValueIsInUnresolved(self) -> None:
        """
        Assert that 'value' (builtin int) appears in unresolved.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = self.rd.methodSignature("process")
        self.assertIn("value", sig.unresolved)

    def testModeIsInResolved(self) -> None:
        """
        Assert that 'mode' (default-valued) appears in resolved.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = self.rd.methodSignature("process")
        self.assertIn("mode", sig.resolved)

    def testOrderedHasTwoKeys(self) -> None:
        """
        Assert that ordered contains exactly two entries for process().

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = self.rd.methodSignature("process")
        self.assertEqual(len(sig.ordered), 2)

    def testModeDefaultIsHello(self) -> None:
        """
        Assert that the Argument for 'mode' stores 'fast' as its default.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = self.rd.methodSignature("process")
        self.assertEqual(sig.resolved["mode"].default, "fast")

    def testMissingMethodRaisesAttributeError(self) -> None:
        """
        Assert that requesting a non-existent method raises AttributeError.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(AttributeError):
            self.rd.methodSignature("non_existent_method_xyz")

# ---------------------------------------------------------------------------
# callableSignature
# ---------------------------------------------------------------------------

class TestCallableSignaturePlainFunction(TestCase):

    def setUp(self) -> None:
        """
        Prepare a ReflectDependencies instance wrapping _plain_function.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.rd = ReflectDependencies(_plain_function)

    def testReturnsSignature(self) -> None:
        """
        Assert that callableSignature returns a Signature instance.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.rd.callableSignature(), Signature)

    def testAIsInUnresolved(self) -> None:
        """
        Assert that 'a' (builtin int, no default) appears in unresolved.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = self.rd.callableSignature()
        self.assertIn("a", sig.unresolved)

    def testBIsInResolved(self) -> None:
        """
        Assert that 'b' (default value) appears in resolved.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = self.rd.callableSignature()
        self.assertIn("b", sig.resolved)

    def testOrderedHasTwoKeys(self) -> None:
        """
        Assert that ordered contains exactly two entries.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = self.rd.callableSignature()
        self.assertEqual(len(sig.ordered), 2)

    def testBDefaultIsHello(self) -> None:
        """
        Assert that the Argument for 'b' stores 'hello' as its default.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = self.rd.callableSignature()
        self.assertEqual(sig.resolved["b"].default, "hello")

class TestCallableSignatureAsyncFunction(TestCase):

    def setUp(self) -> None:
        """
        Prepare a ReflectDependencies instance wrapping _async_function.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.rd = ReflectDependencies(_async_function)

    def testReturnsSignature(self) -> None:
        """
        Assert that callableSignature on an async function returns Signature.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.rd.callableSignature(), Signature)

    def testXIsInUnresolved(self) -> None:
        """
        Assert that 'x' (builtin int) appears in unresolved for async fn.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = self.rd.callableSignature()
        self.assertIn("x", sig.unresolved)

class TestCallableSignatureNonCallable(TestCase):

    def testNonCallableRaisesTypeError(self) -> None:
        """
        Assert that calling callableSignature on a non-callable raises TypeError.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        # A plain integer is not callable; signature inspection must fail
        rd = ReflectDependencies(42)
        with self.assertRaises(TypeError):
            rd.callableSignature()

# ---------------------------------------------------------------------------
# Keyword-only parameters
# ---------------------------------------------------------------------------

class TestKeywordOnlyParameters(TestCase):

    def setUp(self) -> None:
        """
        Prepare a ReflectDependencies instance wrapping _KeywordOnly.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.rd = ReflectDependencies(_KeywordOnly)

    def testLabelIsKeywordOnly(self) -> None:
        """
        Assert that 'label' is marked is_keyword_only in the Argument.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = self.rd.constructorSignature()
        self.assertTrue(sig.unresolved["label"].is_keyword_only)

    def testCountIsKeywordOnly(self) -> None:
        """
        Assert that 'count' (with default) is marked is_keyword_only.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = self.rd.constructorSignature()
        self.assertTrue(sig.resolved["count"].is_keyword_only)

    def testGetKeywordOnlyContainsLabel(self) -> None:
        """
        Assert that getKeywordOnly returns 'label' from the signature.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = self.rd.constructorSignature()
        self.assertIn("label", sig.getKeywordOnly())

    def testGetPositionalOnlyIsEmpty(self) -> None:
        """
        Assert that getPositionalOnly is empty for an all-keyword-only class.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = self.rd.constructorSignature()
        self.assertEqual(sig.getPositionalOnly(), {})

# ---------------------------------------------------------------------------
# Signature entity — Argument
# ---------------------------------------------------------------------------

class TestArgumentEntity(TestCase):

    def testValidArgumentInstantiates(self) -> None:
        """
        Assert that a fully specified Argument can be instantiated.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        arg = Argument(
            name="x",
            resolved=True,
            module_name="builtins",
            class_name="int",
            type=int,
            full_class_path="builtins.int",
        )
        self.assertIsInstance(arg, Argument)

    def testArgumentIsHashable(self) -> None:
        """
        Assert that a frozen Argument instance is hashable.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        arg = Argument(
            name="x",
            resolved=True,
            module_name="builtins",
            class_name="int",
            type=int,
            full_class_path="builtins.int",
        )
        # Frozen dataclasses must be hashable
        self.assertIsNotNone(hash(arg))

    def testModuleNameNonStringRaisesTypeError(self) -> None:
        """
        Assert that a non-string module_name raises TypeError.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(TypeError):
            Argument(
                name="x",
                resolved=True,
                module_name=123,  # type: ignore[arg-type]
                class_name="int",
                type=int,
                full_class_path="builtins.int",
            )

    def testClassNameNonStringRaisesTypeError(self) -> None:
        """
        Assert that a non-string class_name raises TypeError.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(TypeError):
            Argument(
                name="x",
                resolved=True,
                module_name="builtins",
                class_name=999,  # type: ignore[arg-type]
                type=int,
                full_class_path="builtins.int",
            )

    def testFullClassPathNonStringRaisesTypeError(self) -> None:
        """
        Assert that a non-string full_class_path raises TypeError.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(TypeError):
            Argument(
                name="x",
                resolved=True,
                module_name="builtins",
                class_name="int",
                type=int,
                full_class_path=42,  # type: ignore[arg-type]
            )

    def testTypeNoneRaisesValueError(self) -> None:
        """
        Assert that type=None raises ValueError when resolved has no default.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(ValueError):
            Argument(
                name="x",
                resolved=True,
                module_name="builtins",
                class_name="int",
                type=None,  # type: ignore[arg-type]
                full_class_path="builtins.int",
            )

    def testDefaultNoneSkipsValidation(self) -> None:
        """
        Assert that supplying a default bypasses type validation constraints.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        # Validation is skipped when default is provided, even with type=None
        arg = Argument(
            name="x",
            resolved=True,
            module_name="builtins",
            class_name="int",
            type=None,  # type: ignore[arg-type]
            full_class_path="builtins.int",
            default=0,
        )
        self.assertEqual(arg.default, 0)

# ---------------------------------------------------------------------------
# Signature entity — methods
# ---------------------------------------------------------------------------

class TestSignatureEntity(TestCase):

    def _make_arg(
        self,
        name: str,
        *,
        resolved: bool = True,
        is_keyword_only: bool = False,
        default: Any | None = None,
    ) -> Argument:
        """
        Build a minimal valid Argument for testing.

        Parameters
        ----------
        name : str
            Argument name.
        resolved : bool, optional
            Whether the argument is resolved, by default True.
        is_keyword_only : bool, optional
            Whether argument is keyword-only, by default False.
        default : Any | None, optional
            Default value, by default None.

        Returns
        -------
        Argument
            Constructed Argument instance.
        """
        return Argument(
            name=name,
            resolved=resolved,
            module_name="builtins",
            class_name="int",
            type=int,
            full_class_path="builtins.int",
            is_keyword_only=is_keyword_only,
            default=default,
        )

    def setUp(self) -> None:
        """
        Build a Signature with one resolved and one unresolved argument.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        # resolved arg: has a default, so no validation issues
        self.res_arg = self._make_arg("res", resolved=True, default=1)
        # unresolved arg: no default, resolved=False
        self.unres_arg = self._make_arg("unres", resolved=False, default=0)
        self.kw_arg = self._make_arg("kw", resolved=True, is_keyword_only=True, default=2)
        self.sig = Signature(
            resolved={"res": self.res_arg, "kw": self.kw_arg},
            unresolved={"unres": self.unres_arg},
            ordered={"res": self.res_arg, "unres": self.unres_arg, "kw": self.kw_arg},
        )

    def testNoArgumentsRequiredFalse(self) -> None:
        """
        Assert that noArgumentsRequired returns False for a non-empty ordered.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertFalse(self.sig.noArgumentsRequired())

    def testHasUnresolvedArgumentsTrue(self) -> None:
        """
        Assert that hasUnresolvedArguments returns True when unresolved exists.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertTrue(self.sig.hasUnresolvedArguments())

    def testGetResolvedReturnsResolvedDict(self) -> None:
        """
        Assert that getResolved returns the resolved dictionary.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("res", self.sig.getResolved())
        self.assertNotIn("unres", self.sig.getResolved())

    def testGetUnresolvedReturnsUnresolvedDict(self) -> None:
        """
        Assert that getUnresolved returns the unresolved dictionary.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("unres", self.sig.getUnresolved())
        self.assertNotIn("res", self.sig.getUnresolved())

    def testGetAllOrderedReturnsAllEntries(self) -> None:
        """
        Assert that getAllOrdered returns all three arguments.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        ordered = self.sig.getAllOrdered()
        self.assertEqual(len(ordered), 3)

    def testToDictReturnsDict(self) -> None:
        """
        Assert that toDict returns a dict with the expected keys.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        result = self.sig.toDict()
        self.assertIsInstance(result, dict)
        self.assertIn("res", result)

    def testResolvedToDictReturnsDict(self) -> None:
        """
        Assert that resolvedToDict returns a dict with resolved keys.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        result = self.sig.resolvedToDict()
        self.assertIsInstance(result, dict)
        self.assertIn("res", result)

    def testUnresolvedToDictReturnsDict(self) -> None:
        """
        Assert that unresolvedToDict returns a dict with unresolved keys.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        result = self.sig.unresolvedToDict()
        self.assertIsInstance(result, dict)
        self.assertIn("unres", result)

    def testGetPositionalOnly(self) -> None:
        """
        Assert that getPositionalOnly excludes keyword-only arguments.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        positional = self.sig.getPositionalOnly()
        self.assertIn("res", positional)
        self.assertNotIn("kw", positional)

    def testGetKeywordOnly(self) -> None:
        """
        Assert that getKeywordOnly contains only keyword-only arguments.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        keyword = self.sig.getKeywordOnly()
        self.assertIn("kw", keyword)
        self.assertNotIn("res", keyword)

    def testKeywordOnlyToDict(self) -> None:
        """
        Assert that keywordOnlyToDict returns a dict with keyword-only keys.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        result = self.sig.keywordOnlyToDict()
        self.assertIsInstance(result, dict)
        self.assertIn("kw", result)

    def testPositionalOnlyToDict(self) -> None:
        """
        Assert that positionalOnlyToDict excludes keyword-only arguments.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        result = self.sig.positionalOnlyToDict()
        self.assertNotIn("kw", result)
        self.assertIn("res", result)

    def testArgumentsItems(self) -> None:
        """
        Assert that arguments() returns the items view of ordered.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        items = list(self.sig.arguments())
        self.assertEqual(len(items), 3)

    def testItemsEqualsArguments(self) -> None:
        """
        Assert that items() and arguments() produce the same result.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertEqual(list(self.sig.items()), list(self.sig.arguments()))

    def testInvalidResolvedTypeRaisesTypeError(self) -> None:
        """
        Assert that a non-dict resolved value raises TypeError.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(TypeError):
            Signature(
                resolved="bad",  # type: ignore[arg-type]
                unresolved={},
                ordered={},
            )

    def testInvalidUnresolvedTypeRaisesTypeError(self) -> None:
        """
        Assert that a non-dict unresolved value raises TypeError.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(TypeError):
            Signature(
                resolved={},
                unresolved="bad",  # type: ignore[arg-type]
                ordered={},
            )

    def testInvalidOrderedTypeRaisesTypeError(self) -> None:
        """
        Assert that a non-dict ordered value raises TypeError.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(TypeError):
            Signature(
                resolved={},
                unresolved={},
                ordered="bad",  # type: ignore[arg-type]
            )

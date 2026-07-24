from __future__ import annotations
import tempfile
from pathlib import Path
from orionis.localization.contracts.loader import ITranslationLoader
from orionis.localization.contracts.manager import ILocalizationManager
from orionis.localization.contracts.repository import ITranslationRepository
from orionis.localization.contracts.translator import ITranslator
from orionis.localization.exceptions import (
    InvalidLocaleException,
    TranslationSyntaxException,
)
from orionis.localization.loader import TranslationLoader
from orionis.localization.manager import LocalizationManager
from orionis.localization.repository import TranslationRepository
from orionis.localization.translator import Translator
from orionis.test import TestCase

class _StubApp:
    """Minimal application stub exposing config and base path."""

    def __init__(self, base_path: Path, config: dict) -> None:
        """
        Initialize the stub with its base path and configuration.

        Parameters
        ----------
        base_path : Path
            Directory acting as the application base path.
        config : dict
            Mapping of dot-notated configuration keys to values.
        """
        self._base_path = base_path
        self._config = config

    @property
    def basePath(self) -> Path:
        """
        Return the application base path.

        Returns
        -------
        Path
            Base path injected at construction time.
        """
        return self._base_path

    def config(self, key: str) -> object:
        """
        Return the configuration value stored under *key*.

        Parameters
        ----------
        key : str
            Dot-notated configuration key to resolve.

        Returns
        -------
        object
            Configured value or None when absent.
        """
        return self._config.get(key)

def _writeLangFiles(root: Path) -> None:
    """
    Write the fixture translation files under *root*.

    Parameters
    ----------
    root : Path
        Directory acting as the language path.
    """
    root.mkdir(parents=True, exist_ok=True)
    (root / "es.json").write_text(
        '{"Welcome": "Bienvenido", "Hello :name": "Hola :name"}',
        encoding="utf-8",
    )
    (root / "en.json").write_text(
        '{"Welcome": "Welcome", "Hello :name": "Hello :name", '
        '"Only English": "Only English"}',
        encoding="utf-8",
    )
    grouped = root / "es"
    grouped.mkdir(exist_ok=True)
    (grouped / "validation.json").write_text(
        '{"required": "El campo es obligatorio", '
        '"nested": {"email": "Correo inválido"}}',
        encoding="utf-8",
    )

def _makeTranslator(root: Path, locale: str = "es") -> Translator:
    """
    Build a translator wired to the fixture language path.

    Parameters
    ----------
    root : Path
        Directory acting as the language path.
    locale : str
        Active locale for the translator.

    Returns
    -------
    Translator
        Translator with fallback locale ``en``.
    """
    loader = TranslationLoader(root)
    return Translator(
        locale=locale,
        fallback="en",
        loader=loader,
        repository=TranslationRepository(loader),
    )

class TestLocalizationLoader(TestCase):
    """Validate translation loading, flattening, and discovery."""

    async def testLoadsRootJsonTranslations(self) -> None:
        """Root JSON keys are exposed as literal source texts."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _writeLangFiles(root)
            loaded = TranslationLoader(root).load("es")
            self.assertEqual(loaded["Welcome"], "Bienvenido")

    async def testFlattensGroupedFilesWithDotNotation(self) -> None:
        """Grouped files are flattened as group.nested.key entries."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _writeLangFiles(root)
            loaded = TranslationLoader(root).load("es")
            self.assertEqual(
                loaded["validation.required"], "El campo es obligatorio",
            )
            self.assertEqual(
                loaded["validation.nested.email"], "Correo inválido",
            )

    async def testMissingLocaleYieldsEmptyMap(self) -> None:
        """Loading a locale without sources returns an empty mapping."""
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(TranslationLoader(Path(tmp)).load("fr"), {})

    async def testInvalidJsonRaisesSyntaxException(self) -> None:
        """Malformed JSON payloads raise TranslationSyntaxException."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "es.json").write_text("{broken", encoding="utf-8")
            with self.assertRaises(TranslationSyntaxException):
                TranslationLoader(root).load("es")

    async def testAvailableLocalesDiscoversFilesAndFolders(self) -> None:
        """Locales come from root JSON files and grouped directories."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _writeLangFiles(root)
            loader = TranslationLoader(root)
            self.assertEqual(loader.availableLocales(), ("en", "es"))
            self.assertIsInstance(loader, ITranslationLoader)

class TestLocalizationRepository(TestCase):
    """Validate the in-memory cache behavior."""

    async def testLocaleIsReadFromDiskOnlyOnce(self) -> None:
        """Subsequent lookups never re-read the source files."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _writeLangFiles(root)
            repository = TranslationRepository(TranslationLoader(root))
            first = repository.get("es")

            # Mutate the file on disk; the cache must remain untouched.
            (root / "es.json").write_text('{"Welcome": "X"}', encoding="utf-8")
            self.assertIs(repository.get("es"), first)
            self.assertEqual(repository.get("es")["Welcome"], "Bienvenido")

    async def testForgetAndFlushDiscardCachedLocales(self) -> None:
        """Forget removes one locale and flush removes all of them."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _writeLangFiles(root)
            repository = TranslationRepository(TranslationLoader(root))
            repository.get("es")
            repository.get("en")
            self.assertEqual(repository.loadedLocales(), ("es", "en"))
            self.assertTrue(repository.forget("es"))
            self.assertFalse(repository.forget("es"))
            self.assertFalse(repository.has("es"))
            repository.flush()
            self.assertEqual(repository.loadedLocales(), ())
            self.assertIsInstance(repository, ITranslationRepository)

class TestLocalizationTranslator(TestCase):
    """Validate translation resolution, plurals, and locale switching."""

    async def testGetTranslatesForActiveLocale(self) -> None:
        """Lines are resolved from the active locale map."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _writeLangFiles(root)
            translator = _makeTranslator(root)
            self.assertEqual(translator.get("Welcome"), "Bienvenido")

    async def testGetReplacesPlaceholders(self) -> None:
        """Laravel-style :name placeholders are substituted."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _writeLangFiles(root)
            translator = _makeTranslator(root)
            self.assertEqual(
                translator.get("Hello :name", name="Carlos"), "Hola Carlos",
            )

    async def testGetSupportsExplicitLocale(self) -> None:
        """An explicit locale overrides the active locale."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _writeLangFiles(root)
            translator = _makeTranslator(root)
            self.assertEqual(translator.get("Welcome", locale="en"), "Welcome")

    async def testGetFallsBackToFallbackLocale(self) -> None:
        """Missing lines are resolved from the fallback locale."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _writeLangFiles(root)
            translator = _makeTranslator(root)
            self.assertEqual(translator.get("Only English"), "Only English")

    async def testGetReturnsKeyWhenTranslationIsMissing(self) -> None:
        """Unknown keys are echoed back unchanged."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _writeLangFiles(root)
            translator = _makeTranslator(root)
            self.assertEqual(translator.get("Unknown Key"), "Unknown Key")

    async def testMissingHandlerSuppliesReplacementLine(self) -> None:
        """The missing-key handler can provide the resolved line."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _writeLangFiles(root)
            translator = _makeTranslator(root)
            translator.missing(lambda key, locale: f"[{locale}] {key}")
            self.assertEqual(translator.get("Ghost"), "[es] Ghost")
            translator.missing(None)
            self.assertEqual(translator.get("Ghost"), "Ghost")

    async def testHasChecksLocaleAndFallback(self) -> None:
        """has() honors the fallback flag."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _writeLangFiles(root)
            translator = _makeTranslator(root)
            self.assertTrue(translator.has("Welcome"))
            self.assertTrue(translator.has("Only English"))
            self.assertFalse(translator.has("Only English", fallback=False))
            self.assertFalse(translator.has("Unknown Key"))

    async def testChoiceSelectsSingularAndPlural(self) -> None:
        """Positional plural rules pick singular for one, plural otherwise."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _writeLangFiles(root)
            translator = _makeTranslator(root)
            line = "There is one apple|There are :count apples"
            self.assertEqual(translator.choice(line, 1), "There is one apple")
            self.assertEqual(translator.choice(line, 5), "There are 5 apples")

    async def testChoiceHonorsExplicitConditions(self) -> None:
        """Explicit {n} and [a,*] conditions take precedence."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _writeLangFiles(root)
            translator = _makeTranslator(root)
            line = "{0} none|{1} one|[2,*] many (:count)"
            self.assertEqual(translator.choice(line, 0), "none")
            self.assertEqual(translator.choice(line, 1), "one")
            self.assertEqual(translator.choice(line, 7), "many (7)")

    async def testSetLocaleSwitchesTranslationsAtRuntime(self) -> None:
        """Switching the locale changes translations immediately."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _writeLangFiles(root)
            translator = _makeTranslator(root)
            self.assertEqual(translator.getLocale(), "es")
            translator.setLocale("en")
            self.assertEqual(translator.getLocale(), "en")
            self.assertEqual(translator.get("Welcome"), "Welcome")

    async def testInvalidLocaleIsRejected(self) -> None:
        """Malformed locale codes raise InvalidLocaleException."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _writeLangFiles(root)
            translator = _makeTranslator(root)
            with self.assertRaises(InvalidLocaleException):
                translator.setLocale("../etc")
            with self.assertRaises(InvalidLocaleException):
                translator.get("Welcome", locale="")

    async def testReloadPicksUpFileChanges(self) -> None:
        """reload() discards the cache so files are re-read."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _writeLangFiles(root)
            translator = _makeTranslator(root)
            self.assertEqual(translator.get("Welcome"), "Bienvenido")
            (root / "es.json").write_text(
                '{"Welcome": "Hola de nuevo"}', encoding="utf-8",
            )
            translator.reload("es")
            self.assertEqual(translator.get("Welcome"), "Hola de nuevo")
            translator.flush()
            self.assertTrue(translator.forget("en") is False)
            self.assertIsInstance(translator, ITranslator)

class TestLocalizationManager(TestCase):
    """Validate translator wiring from the application configuration."""

    async def testManagerBuildsSharedTranslatorFromConfig(self) -> None:
        """The manager builds one translator from the app settings."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            _writeLangFiles(base / "resources" / "lang")
            app = _StubApp(base, {
                "app.locale": "es",
                "app.fallback_locale": "en",
                "app.language_path": "resources/lang/",
            })
            manager = LocalizationManager(app)
            translator = manager.translator()
            self.assertIs(manager.translator(), translator)
            self.assertEqual(translator.getLocale(), "es")
            self.assertEqual(translator.get("Welcome"), "Bienvenido")
            self.assertEqual(translator.availableLocales(), ("en", "es"))
            self.assertIsInstance(manager, ILocalizationManager)

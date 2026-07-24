from __future__ import annotations
from typing import ClassVar
from orionis.orm import Boolean, Integer, Model, String
from orionis.orm.metaclass import pluralize, snakeCase
from orionis.test import TestCase

class _User(Model):
    id = Integer().primary().autoIncrement()
    name = String()
    active = Boolean()

    casts: ClassVar[dict[str, str]] = {"active": "bool"}
    hidden: ClassVar[list[str]] = ["active"]

class _Category(Model):
    id = Integer().primary()

class _Box(Model):
    id = Integer().primary()

class _Account(Model):
    table = "ledger_accounts"
    id = Integer().primary()

class _CustomKey(Model):
    uuid = String().primary()
    incrementing = False

class _BaseAudit(Model):
    __abstract__ = True
    id = Integer().primary().autoIncrement()
    created_by = String().nullable()

    casts: ClassVar[dict[str, str]] = {"id": "int"}

class _Invoice(_BaseAudit):
    total = Integer()

    casts: ClassVar[dict[str, str]] = {"total": "int"}

class TestNamingHelpers(TestCase):

    def testSnakeCaseSplitsCamelWords(self) -> None:
        """
        Convert CamelCase names into snake_case.

        Validates the class-name normalization helper.
        """
        self.assertEqual(snakeCase("UserProfile"), "user_profile")
        self.assertEqual(snakeCase("User"), "user")

    def testPluralizeAppliesEnglishHeuristics(self) -> None:
        """
        Pluralize words with the conventional English rules.

        Validates the y/ies, sibilant/es, and default/s branches.
        """
        self.assertEqual(pluralize("user"), "users")
        self.assertEqual(pluralize("category"), "categories")
        self.assertEqual(pluralize("box"), "boxes")
        self.assertEqual(pluralize("day"), "days")

class TestModelMetaclass(TestCase):

    def testTableNameDerivedFromClassName(self) -> None:
        """
        Derive the table name from the pluralized class name.

        Validates the naming convention.
        """
        self.assertEqual(_User.__meta__.tableName, "users")
        self.assertEqual(_Category.__meta__.tableName, "categories")
        self.assertEqual(_Box.__meta__.tableName, "boxes")

    def testExplicitTableNameIsRespected(self) -> None:
        """
        Respect an explicitly declared table name.

        Validates the declaration override.
        """
        self.assertEqual(_Account.__meta__.tableName, "ledger_accounts")

    def testColumnsAreDiscoveredAndDetached(self) -> None:
        """
        Discover the declared columns and detach them from the class.

        Validates column discovery and namespace cleanup.
        """
        meta = _User.__meta__
        self.assertEqual(set(meta.columns), {"id", "name", "active"})
        self.assertEqual(meta.columns["id"].name, "id")
        # Class access falls through to the metaclass, not the column.
        self.assertNotIn("name", _User.__dict__)

    def testPrimaryKeyFromColumnFlag(self) -> None:
        """
        Resolve the primary key from the primary column flag.

        Validates primary key discovery.
        """
        self.assertEqual(_User.__meta__.primaryKey, "id")
        self.assertEqual(_CustomKey.__meta__.primaryKey, "uuid")
        self.assertFalse(_CustomKey.__meta__.incrementing)

    def testCastsAndHiddenArePrecomputed(self) -> None:
        """
        Precompute cast handlers and hidden attribute sets.

        Validates the metadata precomputation.
        """
        meta = _User.__meta__
        self.assertIn("active", meta.castLookup)
        self.assertEqual(meta.hidden, frozenset({"active"}))

    def testAbstractModelsDeferColumnsToChildren(self) -> None:
        """
        Inherit columns and casts from abstract parents.

        Validates the abstract model support.
        """
        self.assertIsNone(_BaseAudit.__meta__)
        meta = _Invoice.__meta__
        self.assertEqual(
            set(meta.columns),
            {"id", "created_by", "total"},
        )
        self.assertEqual(meta.primaryKey, "id")
        self.assertEqual(set(meta.casts), {"id", "total"})

    def testTimestampColumnsOnlyWhenDeclared(self) -> None:
        """
        Track timestamp columns only when they are declared.

        Validates the timestamp column detection.
        """
        self.assertIsNone(_User.__meta__.createdColumn)
        self.assertIsNone(_User.__meta__.updatedColumn)

    def testFillableRulesPrecedence(self) -> None:
        """
        Resolve mass assignment rules with whitelist precedence.

        Validates isFillable across fillable, guarded, and wildcard.
        """
        open_meta = _User.__meta__
        self.assertTrue(open_meta.isFillable("name"))

        class _WhiteListed(Model):
            id = Integer().primary()
            name = String()
            fillable: ClassVar[list[str]] = ["name"]

        meta = _WhiteListed.__meta__
        self.assertTrue(meta.isFillable("name"))
        self.assertFalse(meta.isFillable("id"))

        class _BlackListed(Model):
            id = Integer().primary()
            name = String()
            guarded: ClassVar[list[str]] = ["id"]

        meta = _BlackListed.__meta__
        self.assertTrue(meta.isFillable("name"))
        self.assertFalse(meta.isFillable("id"))

        class _Locked(Model):
            id = Integer().primary()
            name = String()
            guarded: ClassVar[list[str]] = ["*"]

        meta = _Locked.__meta__
        self.assertFalse(meta.isFillable("name"))

    def testTimestampsDisabledClearsTimestampColumns(self) -> None:
        """
        Ignore timestamp columns when timestamps are disabled.

        Validates the timestamps switch.
        """

        class _Frozen(Model):
            id = Integer().primary()
            created_at = String().nullable()
            updated_at = String().nullable()
            timestamps = False

        meta = _Frozen.__meta__
        self.assertIsNone(meta.createdColumn)
        self.assertIsNone(meta.updatedColumn)

    def testCustomTimestampColumnNames(self) -> None:
        """
        Honor overridden CREATED_AT and UPDATED_AT names.

        Validates the timestamp column overrides.
        """

        class _Renamed(Model):
            id = Integer().primary()
            createdOn = String().nullable()  # noqa: N815
            CREATED_AT: ClassVar[str] = "createdOn"

        meta = _Renamed.__meta__
        self.assertEqual(meta.createdColumn, "createdOn")
        self.assertIsNone(meta.updatedColumn)

    def testApplyCastsSkipsNoneValues(self) -> None:
        """
        Skip cast application for None values.

        Validates the hydration cast pass.
        """
        meta = _User.__meta__
        row = {"id": 1, "name": "a", "active": None}
        self.assertIsNone(meta.applyCasts(row)["active"])
        row_cast = meta.applyCasts({"id": 1, "active": 1})
        self.assertIs(row_cast["active"], True)

    def testBaseModelHasNoMetadata(self) -> None:
        """
        Keep the abstract base model without metadata.

        Validates the abstract base detection.
        """
        self.assertIsNone(Model.__meta__)

import sys
import unittest
from unittest import TestCase, makeSuite, TestSuite
from zope.interface.advice import addClassAdvisor, determineMetaclass
from zope.interface.advice import getFrameInfo

def ping(log, value):
    def pong(klass):
        log.append((value, klass))
        return [klass]

    addClassAdvisor(pong)

class ClassicClass:
    __metaclass__ = type(object)
    classLevelFrameInfo = getFrameInfo(sys._getframe())

class NewStyleClass:
    __metaclass__ = type
    classLevelFrameInfo = getFrameInfo(sys._getframe())

moduleLevelFrameInfo = getFrameInfo(sys._getframe())

class FrameInfoTest(TestCase):
    classLevelFrameInfo = getFrameInfo(sys._getframe())

    def test_checkModuleInfo(self):
        kind, module, f_locals, f_globals = moduleLevelFrameInfo
        self.assertEqual(kind, "module")
        for d in (module.__dict__, f_locals, f_globals):
            self.assertIs(d, globals())

    def test_checkClassicClassInfo(self):
        kind, module, f_locals, f_globals = ClassicClass.classLevelFrameInfo
        self.assertEqual(kind, "class")
        self.assertIs(f_locals, ClassicClass.__dict__)
        for d in (module.__dict__, f_globals):
            self.assertIs(d, globals())

    def test_checkNewStyleClassInfo(self):
        kind, module, f_locals, f_globals = NewStyleClass.classLevelFrameInfo
        self.assertEqual(kind, "class")
        for d in (module.__dict__, f_globals):
            self.assertIs(d, globals())

    def test_checkCallInfo(self):
        kind, module, f_locals, f_globals = getFrameInfo(sys._getframe())
        self.assertEqual(kind, "function call")
        self.assertIs(f_locals, locals())
        for d in (module.__dict__, f_globals):
            self.assertIs(d, globals())

class AdviceTests(TestCase):
    def test_checkOrder(self):
        log = []

        class Foo(object):
            ping(log, 1)
            ping(log, 2)
            ping(log, 3)

            # Strip the list nesting
            for i in (1, 2, 3):
                self.assertIsInstance(Foo, list)
                Foo, = Foo

            self.assertEqual(log, [(1, Foo), (2, [Foo]), (3, [[Foo]]])

    def test_checkOutside(self):
        with self.assertRaises(SyntaxError):
            ping([], 1)

    @unittest.skipIf(sys.hexversion < 0x02030000, "Duplicate bases not allowed in 2.3")
    def test_checkDoubleType(self):
        class aType(type, type):
            ping([], 1)

        aType, = aType
        self.assertIs(aType.__class__, type)

    def test_checkSingleExplicitMeta(self):
        class M(type):
            pass

        class C(M):
            __metaclass__ = M
            ping([], 1)

        C, = C
        self.assertIs(C.__class__, M)

    def test_checkMixedMetas(self):
        class M1(type):
            pass

        class M2(type):
            pass

        class B1:
            __metaclass__ = M1

        class B2:
            __metaclass__ = M2

        with self.assertRaises(TypeError):
            class C(B1, B2):
                ping([], 1)

        class M3(M1, M2):
            pass

        class C(B1, B2):
            __metaclass__ = M3
            ping([], 1)

        self.assertIsInstance(C, list)
        C, = C
        self.assertIs(C.__class__, M3)

    def test_checkMetaOfClass(self):
        class metameta(type):
            pass

        class meta(type):
            __metaclass__ = metameta

        self.assertEqual(determineMetaclass((meta, type)), metameta)

TestClasses = (AdviceTests, FrameInfoTest)

def test_suite():
    if sys.version[0] == '2':
        return TestSuite([makeSuite(t, "test_") for t in TestClasses])
    else:
        # Advise metaclasses doesn't work in Python 3
        return []

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")

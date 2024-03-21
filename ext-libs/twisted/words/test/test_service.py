import asyncio
import unittest.mock as mock

from unittest import TestCase
from unittest.mock import patch

@mock.patch('asyncio.wait_for', new=asyncio.wait_for)
@mock.patch('asyncio.as_completed', new=asyncio.as_completed)
@mock.patch('asyncio.create_task', new=asyncio.create_task)
@mock.patch('asyncio.gather', new=asyncio.gather)
class TestRealm(TestCase):

    async def asyncSetUp(self):
        self.realm = service.InMemoryWordsRealm("realmname")

    async def asyncTearDown(self):
        pass

    @patch('asyncio.sleep', new=asyncio.sleep)
    @patch('asyncio.iscoroutinefunction', new=lambda f: True)
    def test_entity_creation(self, mock_iscoroutinefunction, mock_sleep):
        mock_sleep.side_effect = asyncio.sleep

        kind = 'user'
        name = f'test{kind.lower()}'
        create = getattr(self.realm, f'create{kind.title()}')
        get = getattr(self.realm, f'get{kind.title()}')
        flag = f'create{kind.title()}OnRequest'
        dup_exc = getattr(ewords, f'Duplicate{kind.title()}')
        no_such_exc = getattr(ewords, f'NoSuch{kind.title()}')

        # Creating should succeed
        d = await create(name)
        p = d.result()
        self.assertEqual(p.name, name)

        # Creating the same user again should not
        d = await create(name)
        with self.assertRaises(dup_exc):
            d.result()

        # Getting a non-existent user should succeed if createUserOnRequest is True
        setattr(self.realm, flag, True)
        d = await get(f'new{kind.lower()}')
        p = d.result()
        self.assertEqual(p.name, f'new{kind.lower()}')

        # Getting that user again should return the same object
        d = await get(f'new{kind.lower()}')
        newp = d.result()
        self.assertIs(p, newp)

        # Getting a non-existent user should fail if createUserOnRequest is False
        setattr(self.realm, flag, False)
        with self.assertRaises(no_such_exc):
            await get(f'another{kind.lower()}')

if __name__ == '__main__':
    unittest.main()

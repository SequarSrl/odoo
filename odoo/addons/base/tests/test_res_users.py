# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.exceptions import AccessDenied
from odoo.tests.common import TransactionCase


class TestUsers(TransactionCase):

    def test_name_search(self):
        """ Check name_search on user. """
        User = self.env['res.users']

        test_user = User.create({'name': 'Flad the Impaler', 'login': 'vlad'})
        like_user = User.create({'name': 'Wlad the Impaler', 'login': 'vladi'})
        other_user = User.create({'name': 'Nothing similar', 'login': 'nothing similar'})
        all_users = test_user | like_user | other_user

        res = User.name_search('vlad', operator='ilike')
        self.assertEqual(User.browse(i[0] for i in res) & all_users, test_user)

        res = User.name_search('vlad', operator='not ilike')
        self.assertEqual(User.browse(i[0] for i in res) & all_users, all_users)

        res = User.name_search('', operator='ilike')
        self.assertEqual(User.browse(i[0] for i in res) & all_users, all_users)

        res = User.name_search('', operator='not ilike')
        self.assertEqual(User.browse(i[0] for i in res) & all_users, User)

        res = User.name_search('lad', operator='ilike')
        self.assertEqual(User.browse(i[0] for i in res) & all_users, test_user | like_user)

        res = User.name_search('lad', operator='not ilike')
        self.assertEqual(User.browse(i[0] for i in res) & all_users, other_user)

    def test_user_partner(self):
        """ Check that the user partner is well created """

        User = self.env['res.users']
        Partner = self.env['res.partner']
        Company = self.env['res.company']

        company_1 = Company.create({'name': 'company_1'})
        company_2 = Company.create({'name': 'company_2'})

        partner = Partner.create({
            'name': 'Bob Partner',
            'company_id': company_2.id
        })

        # case 1 : the user has no partner
        test_user = User.create({
            'name': 'John Smith',
            'login': 'jsmith',
            'company_ids': [company_1.id],
            'company_id': company_1.id
        })

        self.assertFalse(
            test_user.partner_id.company_id,
            "The partner_id linked to a user should be created without any company_id")

        # case 2 : the user has a partner
        test_user = User.create({
            'name': 'Bob Smith',
            'login': 'bsmith',
            'company_ids': [company_1.id],
            'company_id': company_1.id,
            'partner_id': partner.id
        })

        self.assertEqual(
            test_user.partner_id.company_id,
            company_1,
            "If the partner_id of a user has already a company, it is replaced by the user company"
        )


    def test_change_user_company(self):
        """ Check the partner company update when the user company is changed """

        User = self.env['res.users']
        Company = self.env['res.company']

        test_user = User.create({'name': 'John Smith', 'login': 'jsmith'})
        company_1 = Company.create({'name': 'company_1'})
        company_2 = Company.create({'name': 'company_2'})

        test_user.company_ids += company_1
        test_user.company_ids += company_2

        # 1: the partner has no company_id, no modification
        test_user.write({
            'company_id': company_1.id
        })

        self.assertFalse(
            test_user.partner_id.company_id,
            "On user company change, if its partner_id has no company_id,"
            "the company_id of the partner_id shall NOT be updated")

        # 2: the partner has a company_id different from the new one, update it
        test_user.partner_id.write({
            'company_id': company_1.id
        })

        test_user.write({
            'company_id': company_2.id
        })

        self.assertEqual(
            test_user.partner_id.company_id,
            company_2,
            "On user company change, if its partner_id has already a company_id,"
            "the company_id of the partner_id shall be updated"
        )

    def test_login(self):
        User = self.env['res.users']
        Company = self.env['res.company']

        company_1 = Company.create({'name': 'company_1'})

        test_user = User.create({
            'name': 'John Smith',
            'login': 'JSmith',
            'company_ids': [company_1.id],
            'company_id': company_1.id,
            'password': 'very strong password',
        })

        uid = User._perform_login('jsmith', 'very strong password')
        self.assertEqual(test_user, uid)

        with self.assertRaises(AccessDenied):
            User._perform_login('jsmith', 'wrong password')

    def test_old_uppercase_login(self):
        """ Verify historically case sensitive login are still usable """

        User = self.env['res.users']
        Company = self.env['res.company']

        company_1 = Company.create({'name': 'company_1'})

        test_user = User.create({
            'name': 'John Smith',
            'login': 'JSmith',  # is lowercased by create
            'company_ids': [company_1.id],
            'company_id': company_1.id,
            'password': 'very strong password',
        })
        test_user.login = 'JSmith'

        uid = User._perform_login('JSmith', 'very strong password')
        self.assertEqual(test_user, uid)

        with self.assertRaises(AccessDenied):
            User._perform_login('jsmith', 'very strong password')

    def test_new_lowercase_login(self):
        """ Verify new account login are lowercase """

        User = self.env['res.users']
        Company = self.env['res.company']

        company_1 = Company.create({'name': 'company_1'})

        test_user = User.create({
            'name': 'John Smith',
            'login': 'JSmith',
            'company_ids': [company_1.id],
            'company_id': company_1.id,
            'password': 'very strong password',
        })
        self.assertEqual(test_user.login, 'jsmith')

        uid = User._perform_login('jsmith', 'very strong password')
        self.assertEqual(test_user, uid)

        uid = User._perform_login('JSmith', 'very strong password')
        self.assertEqual(test_user, uid)

    def test_new_and_old_login(self):
        """
        Verify a new account login doesn't prevent an old account from
        connecting
        """

        User = self.env['res.users']
        Company = self.env['res.company']

        company_1 = Company.create({'name': 'company_1'})

        test_old_user = User.create({
            'name': 'John Smith',
            'login': 'JSmith',
            'company_ids': [company_1.id],
            'company_id': company_1.id,
            'password': 'very strong password old',
        })
        test_old_user.login = 'JSmith'

        test_new_user = User.create({
            'name': 'john smith',
            'login': 'jsmith',
            'company_ids': [company_1.id],
            'company_id': company_1.id,
            'password': 'very strong password new',
        })

        uid = User._perform_login('jsmith', 'very strong password new')
        self.assertEqual(test_new_user, uid)

        uid = User._perform_login('JSmith', 'very strong password old')
        self.assertEqual(test_old_user, uid)

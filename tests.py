from datetime import datetime, timedelta
import unittest
from app import app, db
from app.models import User, Post

class UserModelCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_password_hashing(self):
        u = User(username='amy')
        u.set_password('password')
        self.assertFalse(u.check_password('beach'))
        self.assertTrue(u.check_password('password'))

    def test_avatar(self):
        u = User(username='orla', email='orla@example.com')
        self.assertEqual(
            u.avatar(128),
            (
                'https://www.gravatar.com/avatar/'
                '587854fdb206c6315011b96a66d279aa'
                '?id=identicon&s=128'
            ))

    def test_follow(self):
        u1 = User(username='aaron')
        u2 = User(username='dougie')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertEqual(u1.followed.all(), [])
        self.assertEqual(u2.followed.all(), [])

        u1.follow(u2)
        db.session.commit()

        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 1)
        self.assertEqual(u1.followed.first().username, 'dougie')
        self.assertEqual(u2.followers.count(), 1)
        self.assertEqual(u2.followers.first().username, 'aaron')

        u1.unfollow(u2)
        db.session.commit()

    def test_follow_posts(self):
        u1 = User(username='aaron')
        u2 = User(username='amy')
        u3 = User(username='dougie')
        u4 = User(username='orla')
        db.session.add_all([u1, u2, u3, u4])

        now = datetime.utcnow()
        p1 = Post(body="post from aaron", author=u1, timestamp=now + timedelta(seconds=1))
        p2 = Post(body="post from amy", author=u2, timestamp=now + timedelta(seconds=4))
        p3 = Post(body="post from dougie", author=u3, timestamp=now + timedelta(seconds=3))
        p4 = Post(body="post from orla", author=u4, timestamp=now + timedelta(seconds=2))

        u1.follow(u2)
        u1.follow(u4)
        u2.follow(u3)
        u3.follow(u4)

        db.session.commit()

        f1 = u1.followed_posts().all()
        f2 = u2.followed_posts().all()
        f3 = u3.followed_posts().all()
        f4 = u4.followed_posts().all()

        self.assertEqual(f1, [p2, p4, p1])
        self.assertEqual(f2, [p2, p3])
        self.assertEqual(f3, [p3, p4])
        self.assertEqual(f4, [p4])

if __name__ == '__main__':
        unittest.main(verbosity=2)

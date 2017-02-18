from django.test import TestCase

from .models import Site, Avatar, User, Profile
from .serializers import UserSerializer


class WritableNestedModelSerializerTest(TestCase):
    def get_initial_data(self):
        return {
            'username': 'test',
            'profile': {
                'sites': [
                    {
                        'url': 'http://google.com',
                    },
                    {
                        'url': 'http://yahoo.com',
                    },
                ],
                'avatars': [
                    {
                        'image': 'image-1.png',
                    },
                    {
                        'image': 'image-2.png',
                    },
                ],
            },
        }

    def test_create(self):
        serializer = UserSerializer(data=self.get_initial_data())
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'test')

        profile = user.profile
        self.assertIsNotNone(profile)
        self.assertEqual(profile.sites.count(), 2)
        self.assertSetEqual(
            set(profile.sites.values_list('url', flat=True)),
            {'http://google.com', 'http://yahoo.com'}
        )
        self.assertEqual(profile.avatars.count(), 2)
        self.assertSetEqual(
            set(profile.avatars.values_list('image', flat=True)),
            {'image-1.png', 'image-2.png'}
        )

        # Check instances count
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Profile.objects.count(), 1)
        self.assertEqual(Site.objects.count(), 2)
        self.assertEqual(Avatar.objects.count(), 2)

    def test_update(self):
        serializer = UserSerializer(data=self.get_initial_data())
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Check instances count
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Profile.objects.count(), 1)
        self.assertEqual(Site.objects.count(), 2)
        self.assertEqual(Avatar.objects.count(), 2)

        # Update
        user_pk = user.pk
        profile_pk = user.profile.pk

        serializer = UserSerializer(
            instance=user,
            data={
                'pk': user_pk,
                'username': 'new',
                'profile': {
                    'pk': profile_pk,
                    'sites': [
                        {
                            'url': 'http://new-site.com',
                        },
                    ],
                    'avatars': [
                        {
                            'pk': user.profile.avatars.earliest('pk').pk,
                            'image': 'old-image-1.png',
                        },
                        {
                            'image': 'new-image-1.png',
                        },
                        {
                            'image': 'new-image-2.png',
                        },
                    ],
                },
            },
        )

        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.refresh_from_db()
        self.assertIsNotNone(user)
        self.assertEqual(user.pk, user_pk)
        self.assertEqual(user.username, 'new')

        profile = user.profile
        self.assertIsNotNone(profile)
        self.assertEqual(profile.pk, profile_pk)
        self.assertEqual(profile.sites.count(), 1)
        self.assertSetEqual(
            set(profile.sites.values_list('url', flat=True)),
            {'http://new-site.com'}
        )
        self.assertEqual(profile.avatars.count(), 3)
        self.assertSetEqual(
            set(profile.avatars.values_list('image', flat=True)),
            {'old-image-1.png', 'new-image-1.png', 'new-image-2.png'}
        )

        # Check instances count
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Profile.objects.count(), 1)
        self.assertEqual(Site.objects.count(), 1)
        self.assertEqual(Avatar.objects.count(), 3)

    def test_partial_update(self):
        serializer = UserSerializer(data=self.get_initial_data())
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Check instances count
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Profile.objects.count(), 1)
        self.assertEqual(Site.objects.count(), 2)
        self.assertEqual(Avatar.objects.count(), 2)

        # Partial update
        user_pk = user.pk
        profile_pk = user.profile.pk

        serializer = UserSerializer(
            instance=user,
            partial=True,
            data={
                'pk': user_pk,
                'username': 'new',
            }
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.refresh_from_db()
        self.assertIsNotNone(user)
        self.assertEqual(user.pk, user_pk)
        self.assertEqual(user.username, 'new')

        profile = user.profile
        self.assertIsNotNone(profile)
        self.assertEqual(profile.pk, profile_pk)
        self.assertEqual(profile.sites.count(), 2)
        self.assertSetEqual(
            set(profile.sites.values_list('url', flat=True)),
            {'http://google.com', 'http://yahoo.com'}
        )
        self.assertEqual(profile.avatars.count(), 2)
        self.assertSetEqual(
            set(profile.avatars.values_list('image', flat=True)),
            {'image-1.png', 'image-2.png'}
        )

        # Check instances count
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Profile.objects.count(), 1)
        self.assertEqual(Site.objects.count(), 2)
        self.assertEqual(Avatar.objects.count(), 2)

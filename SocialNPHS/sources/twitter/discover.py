"""
Identify other NPHS students based on their connections and geolocated tweets
"""

import random

import shapely

from SocialNPHS.data import district_bounds
from SocialNPHS.sources.twitter.auth import api
from SocialNPHS.sources.twitter import user


def discover_by_location(origin, num_users=20):
    """
    Discovers users based on profile location, not post geolocation.
    `num_users` defaults to 20 because I'm pretty sure 20 is when the ratelimit
    kicks in. It's late and I'm too lazy to check, but I think that's it.
    """
    users = random.sample(origin.following + origin.followers, num_users)
    np_users = []
    for u in users:
        if u.location is not None and 'new paltz' in u.location.lower():
            np_users.append(u.screen_name)
    return np_users


def discover_by_geolocation(origin, num_users=20, _api=api):
    """
    Discovers users based on the location posted with some of their tweets.
    """
    users = random.sample(origin.following + origin.followers, num_users)
    np_users = []
    for u in users:
        # go through this user's tweets, searching for location info
        for t in _api.user_timeline(u.id):
            if t.place is not None:
                # now we can do this the easy way...
                if 'postal_code' in t.place.attributes:
                    if t.place.attributes['postal_code'] == '12561':
                        np_users.append(u.screen_name)
                elif len(t.place.contained_within) > 0:
                    if 'name' in t.place.contained_within[0]:
                        if t.place.contained_within[0]['name'] == 'New Paltz':
                            np_users.append(u.screen_name)
                    # ...or the hard way:
                    # check if the tweet's location is in the school district
                    else:
                        districts = district_bounds.ShapeFileData()
                        npcsd = districts.get_shape_by_name(
                            'New Paltz Central School District'
                        )
                        area = shapely.geometry.Polygon(
                            t.place.contained_within[0]['bounding_box'].coordinates[0]
                        )
                        if area.intersects(npcsd):
                            np_users.append(u.screen_name)
    return np_users


def discover_by_association(origin, num_users=20, num_np_followers=5):
    """
    Discovers users based on the number of `NPUser`s that follow them.
    """
    users = random.sample(origin.following, num_users)
    np_users = []
    for u in users:
        # go through this user's followers' followers to see how popular
        # they are with np students
        followers = u.followers
        if u.followers_count > 2000:
            # nobody from new paltz would be super famous so we can skip them
            continue
        found_np_followers = 0
        for follower in followers:
            if follower.screen_name in user.students:
                found_np_followers += 1
            # if u has enough followers from New Paltz you win a new a car
            if found_np_followers >= num_np_followers:
                np_users.append(u.screen_name)
                break
    return np_users

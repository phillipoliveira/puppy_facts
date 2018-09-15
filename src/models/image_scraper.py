from instagram_scraper import InstagramScraper
from commons.database import Database
from models.images import Images
import getpass


class ImageScraper(object):

    @staticmethod
    def update_image_database(json_data, user):
        database = Database()
        database.initialize()
        timestamps = []
        images_added = 0
        existing_images = Images.find_images({"owner": user.instatag})
        if len(existing_images) == 0:
            max_timestamp = 0
        else:
            for image in existing_images:
                timestamps.append(image.ts)
            max_timestamp = max(timestamps)
        for img in json_data:
            if img['taken_at_timestamp'] > max_timestamp:
                try:
                    img['tags']
                except KeyError:
                    img['tags'] = []
                if user.hashtag is None or all([(user.hashtag is not None),
                                                (user.hashtag in [x.lower() for x in img['tags']])]):
                    for url in img['urls']:
                        image = Images(owner=user.instatag,
                                       image_url=url,
                                       associated_fact_type=user.associated_fact_type,
                                       ts=img['taken_at_timestamp'])
                        image.add_image_to_database()
                        images_added += 1
        print("Images added: {}".format(images_added))
        return

    @staticmethod
    def scrape_instagram(user):
        database = Database()
        database.initialize()
        instagram_login_object = database.find_one("instagram_login", ({}))
        if instagram_login_object is None:
            username = input("Please enter your instagram username:")
            password = getpass.getpass("Please enter your instagram password:")
            instagram_session = InstagramScraper(login_user=username, login_pass=password,
                                                 usernames=[user.instatag], media_types=['image'],
                                                 media_metadata=True, download_files=False)
            while instagram_session.login() is False:
                username = input("Login failed. Please enter your instagram username:")
                password = getpass.getpass("Please enter your instagram password:")
                instagram_session = InstagramScraper(login_user=username, login_pass=password,
                                                     usernames=[user.instatag], media_types=['image'],
                                                     media_metadata=True, download_files=False,)
            database.insert("instagram_login", ({"username": username, "password": password}))
        else:
            username = instagram_login_object['username']
            password = instagram_login_object['password']
            instagram_session = InstagramScraper(login_user=username, login_pass=password,
                                                 usernames=[user.instatag], media_types=['image'],
                                                 media_metadata=True, download_files=False)
            instagram_session.login()
        json_data = instagram_session.scrape()
        return json_data







from instagram.client import InstagramAPI


def get_pic(tag_name):
    api = InstagramAPI(client_secret='30a59cc22c4d44edb3bf14bea05825c8',
                       access_token='d082281eceb24ccb997233ceeab503f9')

    result = api.tag_recent_media(tag_name=tag_name)
    media = result[0]

    for m in media:
        print (m.images)
        print (m.user)
        print (m.tags)
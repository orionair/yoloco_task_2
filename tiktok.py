import requests
import re
from TikTokApi import TikTokApi

def get_data_by_url(url, video_count=100):

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit'
                      '/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
    except requests.exceptions.SSLError:
        result = {'data': {'error': 'SSL Error'}}
        return result

    if response.status_code == 200 and 'tiktok.com' in response.url:
        if 'video' in response.url:
            response = requests.get(response.url.split('video')[0], headers=headers)

        page = response.content.decode()

        try:
            username = re.findall(r'(@[a-zA-z0-9_.]*)', response.url)[0].replace('@', '')
            followers = re.findall(r'(?<="fans":)(\d+)(?=\,)', page)[0]
            following = re.findall(r'(?<="following":)(\d+)(?=\,)', page)[0]
            likes = int(re.findall(r'(?<="heart":")(\d+)(?=\",)', page)[0])
        except IndexError:
            data = {'error': 'Cannot parse page'}
            return data

        api = TikTokApi()

        user_data = api.getUserObject(username)

        user_id = user_data.get('id')
        full_name = user_data.get('nickname')
        bio = user_data.get('signature')
        avatar = user_data.get('avatarLarger')

        suggested_users = api.getSuggestedUsersbyID(count=30, userId=user_id)

        user_list = []

        for user in suggested_users:
            user_list += [{
                'username': user.get('subTitle'),
                'id': user.get('id'),
                'avatar': user.get('cover')
            }]

        tiktoks = api.byUsername(count=video_count, username=username)

        video_list = []

        for video in tiktoks:
            video_list += [{
                'url': video['video'].get('downloadAddr'),
                'likes': video['stats'].get('diggCount'),
                'comments': video['stats'].get('commentCount'),
                'views': video['stats'].get('playCount')
            }]

        result = {'data': {
            'username': username,
            'user_id': user_id,
            'full_name': full_name,
            'bio': bio,
            'avatar': avatar,
            'followers': followers,
            'following': following,
            'likes': likes,
            # 'suggested_users': user_list,
            # 'videos': video_list
        }}

        return result
    else:
        result = {'data': {'error': 'Unknown error'}}
        return result
        

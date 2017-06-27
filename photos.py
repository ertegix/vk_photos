#! /usr/bin/python
# -*- coding: utf-8 -*-

import sys
import json
from urllib import urlopen
from urllib import urlencode
import os
from shutil import rmtree
from time import sleep
import time


def auth(login, pwd):
    params = {}
    params['grant_type'] = 'password'
    params['client_id'] = '2274003'
    params['client_secret'] = 'hHbZxrka2uZ6jB1inYsH'
    params['username'] = login
    params['password'] = pwd
    request_str = 'https://oauth.vk.com/token?%s' % urlencode(params)
    r = urlopen(request_str).read()
    response = bytes.decode(r)
    json_data = json.loads(response)
    if 'error' in json_data:
        return {'error': 'Wrong auth data'}
    if 'access_token' in json_data:
        return json_data
    if not 'error' in json_data and not 'access_token' in json_data:
        return {'error': 'Unknown error'}


def deauth():
    try:
        os.remove('token')
        sys.exit('User deauthorized.')
    except Exception:
        sys.exit('Error. No authorized user found.')


def touch(path):
    with open(path, 'a'):
        os.utime(path, None)


def create_file(file_path):
    if not os.path.exists(file_path):
        touch(file_path)


def create_directory(private_dir_name):
    if os.path.isdir(private_dir_name):
        rmtree(private_dir_name)
        os.mkdir(private_dir_name)
    else:
        os.mkdir(private_dir_name)


def emoji_wipe(plain):
    array = bytearray(plain)
    while b'\xf0' in array:
        pos = array.find(b'\xf0')
        array = array.replace(array[pos:], array[pos + 4:])
    while b'\xe2' in array:
        pos = array.find(b'\xe2')
        array = array.replace(array[pos:], array[pos + 3:])
    return bytearray.decode(array, 'utf-8', errors='ignore')


def request(method, params, is_one):
    try:
        sleep(request_interval)
        request_str = 'https://api.vk.com/method/%s?%s' % (method, urlencode(params))
        r = urlopen(request_str).read()
        json_data = json.loads(emoji_wipe(r))
        if 'error' in json_data:
            return {'error': json_data['error']}
        if 'response' in json_data:
            json_data = json_data['response']
            json_data = list(json_data)
            if is_one == True:
                return json_data.pop()
            else:
                return json_data
        if not 'error' in json_data and not 'response' in json_data:
            return {'error': 'unknown error'}
    except Exception:
        pass


def get_photos_method(uid, token, file_name, f, photo_method, active, banned, user, group):
    params = {}
    params['access_token'] = token
    params['owner_id'] = uid
    params['count'] = 0
    active_group = check_group(uid, token)
    if (active and user):
        checking = check_user(uid, token, active, banned)
    elif (banned and user):
        checking = check_user(uid, token, active, banned)
    elif active and group:
        checking = active_group
    else:
        checking = True
    if checking:
        photos_count = request('photos.%s' % photo_method, params, is_one=True)
        path = file_name
        if photos_count:
            try:
                f = open(path, 'a')
                fave_iterations = int(photos_count / 100) + 1
                params['count'] = 100
                for i in range(0, fave_iterations, 1):
                    params['offset'] = 100 * i
                    photos_response = request('photos.%s' % photo_method, params, is_one=False)
                    photos_response = photos_response[1:]
                    for each in photos_response:
                        if 'src_xxbig' in each:
                            link = each['src_xxbig']
                        elif 'src_xbig' in each:
                            link = each['src_xbig']
                        elif 'src_xbig' in each:
                            link = each['src_xbig']
                        elif 'src_big' in each:
                            link = each['src_big']
                        elif 'src_small' in each:
                            link = each['src_small']
                        elif 'src' in each:
                            link = each['src']
                        else:
                            link = '???'
                        f.write('%s:%s\n' % (str(uid), link))
                        print('collecting %s:%s' % (str(uid), link))
                f.close()
            except Exception:
                pass
        else:
            pass
    else:
        pass


def get_photos_album(uid, token, file_name, f, album_id, active, banned, user, group):
    params = {}
    params['access_token'] = token
    params['owner_id'] = uid
    params['count'] = 1000
    params['album_id'] = str(album_id)
    path = file_name
    active_group = check_group(uid, token)
    if (active and user):
        checking = check_user(uid, token, active, banned)
    elif (banned and user):
        checking = check_user(uid, token, active, banned)
    elif active and group:
        checking = active_group
    else:
        checking = True
    if checking:
        try:
            f = open(path, 'a')
            photos_response = request('photos.get', params, is_one=False)
            for each in photos_response:
                try:
                    if 'src_xxbig' in each:
                        link = each['src_xxbig']
                    elif 'src_xbig' in each:
                        link = each['src_xbig']
                    elif 'src_xbig' in each:
                        link = each['src_xbig']
                    elif 'src_big' in each:
                        link = each['src_big']
                    elif 'src_small' in each:
                        link = each['src_small']
                    elif 'src' in each:
                        link = each['src']
                    else:
                        link = '???'
                    f.write('%s:%s\n' % (str(uid), link))
                    print('collecting %s:%s' % (str(uid), link))
                except Exception:
                    pass
            f.close()
        except Exception:
            pass
    else:
        pass


def get_photos(uid, token, directory_name, f, active, banned, user, group):
    download_methods = ['getAll']  # , 'getUserPhotos' 'getNewTags'
    album_ids = [-6, -7, -15]

    delim = '-'
    uid_list = []
    if delim not in uid:
        uid_list.append(uid)
    else:
        uids_b = uid.split(delim)
        for i in range(int(uids_b[0]), int(uids_b[1]) + 1):
            uid_list.append(i)

    for uid_line in uid_list:
        for index, d_method in enumerate(download_methods):
            get_photos_method(uid_line, token, directory_name, f, d_method, active, banned, user, group)
        for index, album_num in enumerate(album_ids):
            get_photos_album(uid_line, token, directory_name, f, album_num, active, banned, user, group)


def check_token(token):
    params = {'access_token': token}
    try:
        check = request('users.get', params, is_one=True)
    except Exception:
        return False
    if ('uid' in check) and ('first_name' in check) and ('last_name' in check):
        return True
    else:
        return False


def check_user(uid, token, active, banned):
    both = active and banned
    userparams = {}
    userparams['access_token'] = token
    userparams['user_ids'] = uid
    userparams['fields'] = 'last_seen'
    user = request('users.get', userparams, is_one=True)
    if (banned and 'deactivated' in user):
        return False
    elif (active and 'last_seen' in user):
        last_seen = user['last_seen']
        last_seen_year = time.localtime(last_seen['time'])[0]
        last_seen_month = time.localtime(last_seen['time'])[1]
        last_seen_day = time.localtime(last_seen['time'])[2]
        actual_year = time.localtime(time.time())[0]
        actual_month = time.localtime(time.time())[1]
        actual_day = time.localtime(time.time())[2]
        years_equal = actual_year == last_seen_year
        month_sub = actual_month - last_seen_month
        day_sub = last_seen_day - actual_day
        user_active = (years_equal and month_sub < 3) or (years_equal and (month_sub == 3 and day_sub > 0))
        return user_active
    else:
        return True


def check_group(uid, token):
    groupparams = {}
    groupparams['access_token'] = token
    groupparams['group_id'] = uid
    group = request('groups.getById', groupparams, is_one=True)
    if ('deactivated' in group):
        return False
    else:
        return True


def download_photo(dir_name, url):
    url_as = url[url.find(':') + 1:]
    file_name = url[:url.find(':')] + '_' + url[url.rfind('/') + 1:]
    resource = urlopen(url_as)
    out = open('%s/%s' % (dir_name, file_name), 'wb')
    out.write(resource.read())
    out.close()


def drop():
    sys.exit('Invalid commandline arguments')


def check_argv(num):
    try:
        if sys.argv[num]:
            drop()
    except Exception:
        pass


def help():
    print('\n\n *** -------------------------------------------------------- *** \n')
    print('This script allows you to dump all photos from albums of any vk user or group\n')
    print('\n List of commands examples:\n')
    print('" python photos.py help " --- Info about program and commandline arguments\n\n')
    print('" python photos.py auth login password " --- Authorizes user. Tel number must be w/o "+"')
    print('example: "python photos.py auth 79211234567 qwerty123456"\n\n')
    print('" python photos.py deauth " --- Deauthorizes current user\n\n')
    print(
        '" python photos.py collect type id " --- Takes list of all photos. Type can only be "user" or "group". Id is user identifier in vk. You cannot use users domain, id must be a number. Creates a txt file with list of photos.')
    print('example: "python photos.py collect user 1234567" or "python photos.py collect group 7654321"\n\n')
    print(
        '" python photos.py download list " --- Downloads collected list of photos. List is name of file, watch your script directory.')
    print('example: "python photos.py download user_1234567.txt" or "python photos.py download group_7654321.txt"\n\n')
    sys.exit('\n *** -------------------------------------------------------- *** \n\n')


request_interval = 0
file_with_token = 'token'

try:
    first_param = sys.argv[1]
except Exception:
    drop()

if (first_param != 'help') and (first_param != 'deauth') and (first_param != 'auth') and (
    first_param != 'collect') and (first_param != 'download'):
    drop()

if first_param == 'help':
    check_argv(2)
    help()

if first_param == 'deauth':
    check_argv(2)
    deauth()

if first_param == 'auth':
    try:
        second_param = sys.argv[2]
        third_param = sys.argv[3]
    except Exception:
        drop()
    check_argv(4)
    try:
        response = auth(second_param, third_param)
    except Exception:
        sys.exit('Auth failed')
    if 'error' in response:
        sys.exit('Error: %s' % response['error'])
    token = response['access_token']
    f = open(file_with_token, 'w')
    f.write('%s' % token)
    f.close()
    sys.exit('Auth successful')

if first_param == 'collect':
    try:
        active = sys.argv[2] == 'active'
        banned = sys.argv[2] == 'notbanned'
        both = (sys.argv[2] == 'active' and sys.argv[3] == 'notbanned') \
               or (sys.argv[3] == 'active' and sys.argv[4] == 'notbanned')
        if (both):
            second_param = sys.argv[4]
            if (second_param != 'group') and (second_param != 'user'):
                drop()
            third_param = sys.argv[5]
        elif (active or banned):
            second_param = sys.argv[3]
            if (second_param != 'group') and (second_param != 'user'):
                drop()
            third_param = sys.argv[4]
        else:
            second_param = sys.argv[2]
            if (second_param != 'group') and (second_param != 'user'):
                drop()
            third_param = sys.argv[3]
    except Exception:
        drop()
    if (both):
        check_argv(6)
    elif (active or banned):
        check_argv(5)
    else:
        check_argv(4)
    try:
        f = open(file_with_token, 'r')
        token = f.read()
        f.close()
    except Exception:
        sys.exit('Cannot read token. No user authorized.')
    try:
        verify = check_token(token)
    except Exception:
        pass
    if not verify:
        if 'access_token=' in token:
            pos = token.find('access_token=')
            pos += 13
            token = token[pos:]
            pos = token.find('&')
            token = token[:pos]
        secondary_verify = check_token(token)
        if not secondary_verify:
            sys.exit('not valid token')
    if second_param == 'user':
        uid = third_param
        file_name = 'user_%s.txt' % str(uid)
    elif second_param == 'group':
        uid = third_param
        file_name = 'group_%s.txt' % str(uid)
    else:
        drop()
    group = second_param == 'group'
    user = second_param == 'user'
    create_file(file_name)
    get_photos(uid, token, file_name, f, active, banned, user, group)

if first_param == 'download':
    try:
        second_param = sys.argv[2]
    except Exception:
        drop()
    check_argv(3)

    file_with_photos = second_param

    try:
        f = open(file_with_photos, 'r')
        photos_txt = f.read()
        f.close()
    except Exception:
        sys.exit('Cannot open file. Make sure to type correct file name.')

    directory_name = file_with_photos[:file_with_photos.rfind('.')]
    create_directory(directory_name)
    create_file('errors.txt')

    links = photos_txt.split('\n')
    links = links[:-1]
    total = len(links)

    for number, link in enumerate(links):
        print('downloading %s (%s of %s)' % (link, str(number + 1), total))
        try:
            download_photo(directory_name, link)
        except Exception:
            print('failed to download %s' % link)
            f = open('errors.txt', 'a')
            f.write('%s\n' % link)
            f.close()
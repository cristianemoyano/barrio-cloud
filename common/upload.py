import hashlib
import time

import dropbox

from django.conf import settings
from django.core.files.storage import FileSystemStorage


def upload_file_dropbox(path_file, file_name_saved):
    file = open(path_file, 'rb')
    dbx = dropbox.Dropbox(settings.DROPBOX_ACCESS_TOKEN)
    res = dbx.files_upload(
        file.read(), '/' + file_name_saved,
        dropbox.files.WriteMode.add
    )
    create_shared_link = dbx.sharing_create_shared_link(res.path_display)
    link = create_shared_link.url
    url, dl = link.split('?')
    public_url = url + '?dl=1'
    return public_url


def get_unique_file_name(user, file_name):
    timestamp = str(int(time.time())).encode('utf-8')
    f_name = file_name.replace(' ', '-')
    h = hashlib.sha256(timestamp).hexdigest()
    name = user.first_name + '-' + \
        str(user.id) + '-' + h + '-' + f_name
    return name


def save_file(name, file):
    fs = FileSystemStorage()
    fs.name = fs.save(name, file)
    return fs


def get_file_local(domain, file_name_saved):
    public_url = domain + settings.MEDIA_URL + file_name_saved
    return public_url


def upload_file(request, request_field, valid_types=None):
    valid_type = valid_types if valid_types else ['image/png', 'image/jpeg', 'application/pdf']
    public_url = {}

    if request_field not in request.FILES:
        public_url['status'] = False
        public_url['dropbox'] = ''
        public_url['local'] = ''
        public_url['path'] = ''
        public_url['name'] = ''
        return public_url
    else:
        request_file = request.FILES[request_field]
        if request_file.content_type in valid_type:
            unique_name = get_unique_file_name(request.user, request_file.name)
            domain = request.build_absolute_uri('/')[:-1]
            fs = save_file(unique_name, request_file)

            public_url['name'] = unique_name
            path_file = fs.location + '/' + fs.name
            public_url['path'] = path_file

            # local
            public_url['local'] = get_file_local(domain, fs.name)

            # dropbox
            public_url['dropbox'] = upload_file_dropbox(path_file, fs.name)
            public_url['status'] = True

            return public_url
        else:
            public_url['status'] = False
            return public_url

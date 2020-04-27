from requests import post, delete
from json import loads
from models import Video
from os import stat

CHUNK_SIZE = 5 * 1024 * 1024

class UploadSession(object):
    def __init__(self, panda, file_name, **kwargs):
        self.panda = panda
        self.file_name = file_name
        self.file_size = stat(file_name).st_size
        params = {
            "file_size": self.file_size,
            "file_name": file_name,
            "profiles": "h264"
        }
        params.update(kwargs)

        data = panda.post('/videos/upload.json', params)
        self.location = loads(data)["location"]
        self.status = "initialized"
        self.video = None
        self.error_message = None

    def _read_chunks(self, file_object):
        i = 0
        while True:
            data = file_object.read(CHUNK_SIZE)
            if not data:
                break
            yield (data, i)
            i = i+1

    def start(self, pos=0):
        if self.status == "initialized":
            self.status = "uploading"
            with open(self.file_name) as f:
                f.seek(pos)
                try:
                    for chunk, i in self._read_chunks(f):
                        index = i * CHUNK_SIZE
    
                        res = post(self.location, headers = {
                            'Content-Type': 'application/octet-stream',
                            'Cache-Control': 'no-cache',
                            'Content-Range': "bytes {0}-{1}/{2}".format(pos+index, pos+index+CHUNK_SIZE-1, self.file_size),
                            'Content-Length': str(CHUNK_SIZE)
                        }, data=chunk)
                        if res.status_code == 200:
                            self.status = "uploaded"
                            self.video = Video(self.panda, json_attr=res.json())
                        elif res.status_code != 204:
                            self.status = "error"
                            break
                except Exception as e:
                    self.status = "error"
                    self.error_message = str(e)
                    raise e
                except KeyboardInterrupt:
                    self.status = "error"
                    self.error_message = "interrupted"
        else:
            raise KeyError("Already started")

    def resume(self):
        if self.status != "uploaded":
            res = post(self.location, headers = {
                'Content-Type': 'application/octet-stream',
                'Cache-Control': 'no-cache',
                'Content-Range': "bytes */{0}".format(self.file_size),
                'Content-Length': "0"
            })
            pos = int(res.headers["Range"].split("-")[1])
            self.status = "initialized"
            self.start(pos=pos)
        else:
            raise KeyError("Already succeed")

    def abort(self):
        if self.status != "success":
            self.status = "aborted"
            self.error_message = None
            res = delete(self.location)
        else:
            raise KeyError("Already succeed")


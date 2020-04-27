import json
import logging
from functools import wraps

logger = logging.getLogger(__name__)

class PandaError(Exception):
    pass

def error_check(func):
    @wraps(func)
    def check(*args, **kwargs):
        try:
            res = func(*args, **kwargs)
            if "error" in res:
                logger.error(res["message"])
                raise PandaError(res["message"])
        except Exception as e:
            logger.error(e)
            raise
        return res
    return check

class Retriever(object):
    def __init__(self, panda, model_type, path = None):
        self.panda = panda
        self.model_type = model_type
        if path:
            self.path = path
        else:
            self.path = model_type.path

class GroupRetriever(Retriever):
    @error_check
    def _all(self, **kwargs):
        json_data = self.panda.get("{0}.json".format(self.path), kwargs)
        return json.loads(json_data)

    @error_check
    def new(self, *args, **kwargs):
        return self.model_type(self.panda, *args, **kwargs)

    @error_check
    def create(self, *args, **kwargs):
        return self.new(*args, **kwargs).create(**kwargs)

    @error_check
    def find(self, val, **kwargs):
        json_data = self.panda.get("{0}/{1}.json".format(self.path, val), **kwargs)
        return self.model_type(self.panda, **json.loads(json_data))

    def all(self, **kwargs):
        return [self.model_type(self.panda, **json_attr) for json_attr in self._all(**kwargs)]

    def where(self, pred, **kwargs):
        return [self.model_type(self.panda, **json_attr) for json_attr in self._all(**kwargs) if pred(json_attr)]

class SingleRetriever(Retriever):
    @error_check
    def get(self, **kwargs):
        json_data = self.panda.get("{0}.json".format(self.path), **kwargs)
        return self.model_type(self.panda, json.loads(json_data))

    @error_check
    def post(self, **kwargs):
        json_data = self.panda.post("{0}.json".format(self.path), **kwargs)
        return self.model_type(self.panda, json.loads(json_data))

class PandaDict(dict):
    def __init__(self, panda, *arg, **kwarg):
        self.panda = panda
        super(PandaDict, self).__init__(*arg, **kwarg)

    def to_json(self, *args, **kwargs):
        return json.dumps(self, *args, **kwargs)

class PandaModel(PandaDict):
    def dup(self):
        copy = self.copy()
        if "id" in copy:
            copy["id"]
        return copy

    def reload(self):
        json_data = self.panda.get("{0}/{1}.json".format(self.path, self["id"]))
        self.clear()
        parsed = json.loads(json_data)
        self.update(parsed)

    @error_check
    def create(self, **kwargs):
        json_data = self.panda.post("{0}.json".format(self.path), kwargs)
        return self.__class__(self.panda, json.loads(json_data))

    @error_check
    def delete(self, **kwargs):
        json_data = self.panda.delete("{0}/{1}.json".format(self.path, self["id"]), kwargs)
        return self.__class__(self.panda, json.loads(json_data))

class UpdatablePandaModel(PandaModel):
    changed_values = {}

    @error_check
    def save(self):
        put_path = "{0}/{1}.json".format(self.path, self["id"])
        ret = type(self)(self.panda, json.loads(self.panda.put(put_path, self.changed_values)))
        if "error" not in ret:
            self.changed_values = {}
        return ret

    def __setitem__(self, key, val):
        self.changed_values[key] = val
        super(UpdatablePandaModel, self).__setitem__(key, val)

    # http://stackoverflow.com/a/2588648/1542900
    def update(self, *args, **kwargs):
        if args:
            if len(args) > 1:
                raise TypeError("update expected at most 1 arguments, got %d" % len(args))
            other = dict(args[0])
            for key in other:
                self[key] = other[key]
        for key in kwargs:
            self[key] = kwargs[key]

    # http://stackoverflow.com/a/2588648/1542900
    def setdefault(self, key, value=None):
        if key not in self:
            self[key] = value
        return self[key]

class Video(PandaModel):
    path = "/videos"

    def encodings(self):
        return GroupRetriever(self.panda, Encoding, "/videos/{0}/encodings".format(self["id"])).all()

    def metadata(self):
        return SingleRetriever(self.panda, Metadata, "/videos/{0}/metadata".format(self["id"])).get()

class Cloud(UpdatablePandaModel):
    path = "/clouds"

class Encoding(PandaModel):
    path = "/encodings"

    def video(self):
        return SingleRetriever(self.panda, Video, "/videos/{0}".format(self["video_id"])).get()

    def profile(self):
        key = self["profile_name"] or self["profile_id"]
        return SingleRetriever(self.panda, Video, "/profiles/{0}".format(key)).get()

    def cancel(self):
        return SingleRetriever(self.panda, PandaDict, "/encodings/{0}/cancel.json".format(self["id"])).post()

    def retry(self):
        return SingleRetriever(self.panda, PandaDict, "/encodings/{0}/retry.json".format(self["id"])).post()

class Profile(UpdatablePandaModel):
    path = "/profiles"

class Notifications(UpdatablePandaModel):
    path = "/notifications"

    @error_check
    def save(self):
        tmp = dict(self)
        for event in tmp["events"]:
            tmp["events"][event] = str(tmp["events"][event]).lower()
        return Notifications(self.panda, json.loads(self.panda.put("/notifications.json", tmp)))

    def delete(self):
        raise AttributeError("Notification instance has no attribute 'delete'")

    def reload(self):
        json_data = self.panda.get("/notifications.json")
        self.clear()
        self.update(json.loads(json_data))

class Metadata(PandaDict):
    pass

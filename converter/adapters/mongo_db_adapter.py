import os, gridfs
from pymongo import MongoClient
from bson.objectid import ObjectId


class FSMongoDBAdapter:

    def __init__(self):
        self.mongo_db_image = MongoClient(host = os.environ.get("MONGO_IMAGES")).get_default_database()
        self.mongo_db_text = MongoClient(host = os.environ.get("MONGO_TEXTS")).get_default_database()
        self.fs_mongo_image = gridfs.GridFS(self.mongo_db_image)
        self.fs_mongo_text = gridfs.GridFS(self.mongo_db_text)

    def get_image(self, file_id):
        self.image = self.fs_mongo_image.get(ObjectId(file_id))
        return self.image

    def upload_text(self, data_text):
        text_fid = self.fs_mongo_text.put(data_text, encoding='utf-8')
        return text_fid

    def delete_text(self, fid):
        self.fs_mongo_text.delete(fid)
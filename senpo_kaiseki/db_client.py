from pymongo import MongoClient
import os
from senpo_kaiseki.code import ResultCode, SuccessCode
import urllib.parse

username = urllib.parse.quote_plus(os.environ["MONGO_USER"])
password = urllib.parse.quote_plus(os.environ["MONGO_PASS"])
CONNECT_STRING = "mongodb+srv://" + username + ":" + password + "@senpo-kaiseki.hq8wf.mongodb.net/senpo_kaiseki?"
QUERY_STRING = "authSource=admin&retryWrites=true&w=majority&replicaSet=atlas-10pfbu-shard-0&readPreference=primary&appName=SenpoKaiseki"


class MongoDatabaseClient():
    def __init__(self) -> None:
        self.client = MongoClient(CONNECT_STRING + QUERY_STRING)
        self.db = self.client.senpo_kaiseki
        self.collection = self.db.senpo_data

    def insert_data(self, data):
        res = []
        if data["win_result"] == "勝":
            win = 0
        elif data["win_result"] == "引分":
            win = 1
        else:
            win = 2

        if data[ResultCode.USER_NAME.name] is not None:
            doc = {
                "user_name": data[ResultCode.USER_NAME.name],
                "name1": data[ResultCode.BUSYO_1],
                "name2": data[ResultCode.BUSYO_2],
                "name3": data[ResultCode.BUSYO_3],
                "level1": str(data[ResultCode.LEVEL_1.name]),
                "level2": str(data[ResultCode.LEVEL_2.name]),
                "level3": str(data[ResultCode.LEVEL_3.name]),
                "senpo1_1": str(data[ResultCode.SENPO_1_1.name]),
                "senpo1_2": str(data[ResultCode.SENPO_1_2.name]),
                "senpo1_3": str(data[ResultCode.SENPO_1_3.name]),
                "senpo2_1": str(data[ResultCode.SENPO_2_1.name]),
                "senpo2_2": str(data[ResultCode.SENPO_2_2.name]),
                "senpo2_3": str(data[ResultCode.SENPO_2_3.name]),
                "senpo3_1": str(data[ResultCode.SENPO_3_1.name]),
                "senpo3_2": str(data[ResultCode.SENPO_3_2.name]),
                "senpo3_3": str(data[ResultCode.SENPO_3_3.name]),
                "win": 0,
                "draw": 0,
                "lose": 0
            }
            if win == 0:
                doc['win'] = 1
            elif win == 1:
                doc["draw"] = 1
            else:
                doc["lose"] = 1
            doc_id = self.collection.insert_one(doc).inserted_id
            print(doc_id)
            res.append(SuccessCode.INSERT)
        else:
            res.append(SuccessCode.FAILED)

        if data[ResultCode.E_USER_NAME.name] is not None:
            doc = {
                "user_name": data[ResultCode.E_USER_NAME.name],
                "name1": data[ResultCode.E_BUSYO_1],
                "name2": data[ResultCode.E_BUSYO_2],
                "name3": data[ResultCode.E_BUSYO_3],
                "level1": str(data[ResultCode.E_LEVEL_1.name]),
                "level2": str(data[ResultCode.E_LEVEL_2.name]),
                "level3": str(data[ResultCode.E_LEVEL_3.name]),
                "senpo1_1": str(data[ResultCode.E_SENPO_1_1.name]),
                "senpo1_2": str(data[ResultCode.E_SENPO_1_2.name]),
                "senpo1_3": str(data[ResultCode.E_SENPO_1_3.name]),
                "senpo2_1": str(data[ResultCode.E_SENPO_2_1.name]),
                "senpo2_2": str(data[ResultCode.E_SENPO_2_2.name]),
                "senpo2_3": str(data[ResultCode.E_SENPO_2_3.name]),
                "senpo3_1": str(data[ResultCode.E_SENPO_3_1.name]),
                "senpo3_2": str(data[ResultCode.E_SENPO_3_2.name]),
                "senpo3_3": str(data[ResultCode.E_SENPO_3_3.name]),
                "win": 0,
                "draw": 0,
                "lose": 0
            }
            if win == 0:
                doc['win'] = 1
            elif win == 1:
                doc["draw"] = 1
            else:
                doc["lose"] = 1
            doc_id = self.collection.insert_one(doc).inserted_id
            print(doc_id)
            res.append(SuccessCode.INSERT)
        else:
            res.append(SuccessCode.FAILED)

        return res

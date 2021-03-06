from time import sleep
import requests
from app import time
from app.config import *
from app.service.database import MessageProducer, MongoDriver


def scan_task_worker():
    pass


def scan_task(network_mask: str) -> str:
    """
    Запуск задачи сканирвоания
    :param network_mask:
    :return:
    """
    requests.post(f"http://127.0.0.1:9101/api/v1/scanner/start", json={"host": network_mask})
    return "success"


def record_db_task(result: str, host: str):
    """
    Запись в БД
    :param result:
    :param host:
    :return:
    """
    data = {
        "uuid": result,
        "name": "Scanner",
        "host": host,
        "time": time()
    }
    message_mongo = MessageProducer(MongoDriver(host=MONGO_HOST, port=MONGO_PORT,
                                                base="scanner", collection="task"))
    message_mongo.insert_message(data)


def host_discovery_task(host: str):
    """
    Запуск задачи по обнаружению хостов в сети
    Используется микросервис
    :param host:
    :return:
    """
    try:
        requests.post(f"{HOST_DISCOVERY}/get", json={"host": host})
    except Exception as e:
        print(e)


def delete_data_host_discovery(host: str):
    """

    """
    try:
        message_mongo_host_discovery = MessageProducer(MongoDriver(host=MONGO_HOST, port=MONGO_PORT,
                                                                   base="HostDiscovery", collection="result"))
        message_mongo_scanner_result = MessageProducer(MongoDriver(host=MONGO_HOST, port=MONGO_PORT,
                                                                   base="scanner", collection="result"))
        message_mongo_scanner_task = MessageProducer(MongoDriver(host=MONGO_HOST, port=MONGO_PORT,
                                                                 base="scanner", collection="task"))
        message_mongo_host_discovery.delete_message({"ip": host})
        message_mongo_scanner_result.delete_message({"host": host})
        message_mongo_scanner_task.delete_message({"host": host})
    except Exception as e:
        print(e)

from time import sleep
from app import time
from app.config import *
from app.service.scanner.scanner import Scanner
import requests
from app.service.database import MessageProducer, MongoDriver


def scan_task(network_mask: str) -> str:
    """
    Запуск задачи сканирвоания
    :param network_mask:
    :return:
    """
    scanner = Scanner(network_mask)
    task_id = requests.post(f"{HOST_DISCOVERY}/get", json={"host": network_mask})
    task = task_id.json()
    while True:
        sleep(3)
        result_discovery = requests.get(f"{HOST_DISCOVERY}/results/{task['job']}")
        if result_discovery.status_code == 200:
            break
    ret = eval(result_discovery.content.decode())
    for host in ret['result']:
        scanner.scanner_task(host)
    return "success"


def scan_db_task(result: str, host: str):
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
    message_mongo = MessageProducer(MongoDriver(host='localhost', port=27017,
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
        message_mongo_host_discovery = MessageProducer(MongoDriver(host='localhost', port=27017,
                                                                   base="host_discovery", collection="result"))
        message_mongo_scanner_result = MessageProducer(MongoDriver(host='localhost', port=27017,
                                                                   base="scanner", collection="result"))
        message_mongo_scanner_task = MessageProducer(MongoDriver(host='localhost', port=27017,
                                                                 base="scanner", collection="task"))
        message_mongo_host_discovery.delete_message({"ip": host})
        message_mongo_scanner_result.delete_message({"host": host})
        message_mongo_scanner_task.delete_message({"host": host})
    except Exception as e:
        print(e)

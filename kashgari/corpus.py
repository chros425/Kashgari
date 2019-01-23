# encoding: utf-8
"""
@author: BrikerMan
@contact: eliyar917@gmail.com
@blog: https://eliyar.biz

@version: 1.0
@license: Apache Licence
@file: corpus
@time: 2019-01-20

"""
import logging
import os
import re
from typing import Tuple, List

import pandas as pd

from kashgari.utils import downloader
from kashgari.utils import helper

DATA_TRAIN = 'train'
DATA_VALIDATE = 'validate'
DATA_TEST = 'test'


class Corpus(object):
    __corpus_name__ = ''
    __zip_file__name = ''

    __desc__ = ''

    @classmethod
    def get_classification_data(cls,
                                is_test: bool = False,
                                shuffle: bool = True,
                                max_count: int = 0) -> Tuple[List[str], List[str]]:
        raise NotImplementedError()

    @classmethod
    def get_info(cls):
        raise NotImplementedError()


class TencentDingdangSLUCorpus(Corpus):

    __corpus_name__ = 'task-slu-tencent.dingdang-v1.1'
    __zip_file__name = 'task-slu-tencent.dingdang-v1.1.tar.gz'

    __desc__ = """    Download from NLPCC 2018 Task4 dataset
    details: http://tcci.ccf.org.cn/conference/2018/taskdata.php
    The dataset adopted by this task is a sample of the real query log from a commercial
    task-oriented dialog system. The data is all in Chinese. The evaluation includes three
    domains, namely music, navigation and phone call. Within the dataset, an additional
    domain label ‘OTHERS’ is used to annotate the data not covered by the three domains. To
    simplify the task, we keep only the intents and the slots of high-frequency while ignoring
    others although they appear in the original data. The entire data can be seen as a stream
    of user queries ordered by time stamp. The stream is further split into a series of segments
    according to the gaps of time stamps between queries and each segment is denoted as a
    ‘session’. The contexts within a session are taken into consideration when a query within
    the session was annotated. Below are two example sessions with annotations.
    
    sample
    ```
    1 打电话 phone_call.make_a_phone_call 打电话
    1 我想听美观 music.play 我想听<song>美观</song>
    1 我想听什话 music.play 我想听<song>什话||神话</song>
    1 神话 music.play <song>神话</song>
    
    2 播放调频广播 OTHERS 播放调频广播
    2 给我唱一首一晃就老了 music.play 给我唱一首<song>一晃就老了</song>
    ```
    """

    @classmethod
    def get_info(cls):
        folder_path = downloader.download_if_not_existed('corpus/' + cls.__corpus_name__,
                                                         'corpus/' + cls.__zip_file__name, )
        logging.info("""{} info\n    dataset path: {}\n{}""".format(cls.__corpus_name__,
                                                                    folder_path,
                                                                    cls.__desc__))

    @classmethod
    def get_classification_data(cls,
                                data_type: str = DATA_TRAIN,
                                shuffle: bool = True,
                                cutter: str = 'char',
                                max_count: int = 0) -> Tuple[List[List[str]], List[List[str]]]:
        """

        :param data_type: {train, validate, test}
        :param shuffle: shuffle or not
        :param cutter:
        :param max_count:
        :return:
        """
        folder_path = downloader.download_if_not_existed('corpus/' + cls.__corpus_name__,
                                                         'corpus/' + cls.__zip_file__name)
        if data_type not in [DATA_TRAIN, DATA_VALIDATE, DATA_TEST]:
            raise ValueError('data_type error, please use one onf the {}'.format([DATA_TRAIN,
                                                                                  DATA_VALIDATE,
                                                                                  DATA_TEST]))
        if cutter not in ['char', 'jieba', 'none']:
            raise ValueError('data_type error, please use one onf the {}'.format([DATA_TRAIN,
                                                                                  DATA_VALIDATE,
                                                                                  DATA_TEST]))

        file_path = os.path.join(folder_path, '{}.csv'.format(data_type))
        df = pd.read_csv(file_path)
        x_data = df['text'].values
        y_data = df['domain'].values
        if shuffle:
            x_data, y_data = helper.unison_shuffled_copies(x_data, y_data)

        if max_count != 0:
            x_data = x_data[:max_count]
            y_data = y_data[:max_count]

        if cutter == 'jieba':
            try:
                import jieba
            except ModuleNotFoundError:
                raise ModuleNotFoundError("please install jieba, `$ pip install jieba`")
            x_data = [list(jieba.cut(item)) for item in x_data]
        elif 'char':
            x_data = [list(item) for item in x_data]
        return x_data, y_data

    @staticmethod
    def parse_ner_str(text: str) -> Tuple[str, str]:
        pattern = '<(?P<entity>\\w*)>(?P<value>[^<>]*)<\\/\\w*>'
        x_list = []
        tag_list = []
        last_index = 0
        for m in re.finditer(pattern, text):
            x_list += text[last_index:m.start()]
            tag_list += ['O'] * (m.start() - last_index)
            last_index = m.end()
            dic = m.groupdict()
            value = dic['value'].split('||')[0]
            entity = dic['entity']
            x_list += list(value)
            tag_list += ['P-' + entity] + ['I-' + entity] * (len(value) - 1)
        if last_index < len(text):
            x_list += list(text[last_index:])
            tag_list += len(text[last_index:]) * ['O']
        return ' '.join(x_list), ' '.join(tag_list)

    @classmethod
    def get_sequence_tagging_data(cls,
                                  is_test: bool = False,
                                  shuffle: bool = True,
                                  max_count: int = 0) -> Tuple[List[str], List[str]]:
        folder_path = downloader.download_if_not_existed('corpus/' + cls.__corpus_name__,
                                                         'corpus/' + cls.__zip_file__name, )

        if is_test:
            file_path = os.path.join(folder_path, 'test.csv')
        else:
            file_path = os.path.join(folder_path, 'train.csv')

        df = pd.read_csv(file_path)
        x_data = []
        y_data = []

        for tagging_text in df['tagging']:
            x_item, y_item = cls.parse_ner_str(tagging_text)
            x_data.append(x_item)
            y_data.append(y_item)
        if shuffle:
            x_data, y_data = helper.unison_shuffled_copies(x_data, y_data)
        if max_count != 0:
            x_data = x_data[:max_count]
            y_data = y_data[:max_count]
        return x_data, y_data


class ChinaPeoplesDailyNerCorpus(object):
    __corpus_name__ = 'china-people-daily-ner-corpus'
    __zip_file__name = 'china-people-daily-ner-corpus.tar.gz'

    __desc__ = """    Download from NLPCC 2018 Task4 dataset
        """

    @classmethod
    def get_sequence_tagging_data(cls,
                                  data_type: str = DATA_TRAIN,
                                  shuffle: bool = True,
                                  max_count: int = 0) -> Tuple[List[List[str]], List[List[str]]]:
        folder_path = downloader.download_if_not_existed('corpus/' + cls.__corpus_name__,
                                                         'corpus/' + cls.__zip_file__name)

        if data_type == DATA_TRAIN:
            file_path = os.path.join(folder_path, 'example.train')
        elif data_type == DATA_TEST:
            file_path = os.path.join(folder_path, 'example.test')
        else:
            file_path = os.path.join(folder_path, 'example.dev')

        data_x, data_y = [], []

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.read().splitlines()
            x, y = [], []
            for line in lines:
                rows = line.split(' ')
                if len(rows) == 1:
                    data_x.append(x)
                    data_y.append(y)
                    x = []
                    y = []
                else:
                    x.append(rows[0])
                    y.append(rows[1])
        return data_x, data_y


class SMP2017ECDTClassificationData(Corpus):
    __corpus_name__ = 'smp2017ecdt-data-task1'
    __zip_file__name = 'smp2017ecdt-data-task1.tar.gz'

    __desc__ = """
    http://ir.hit.edu.cn/smp2017ecdt-data
    """

    @classmethod
    def get_classification_data(cls,
                                data_type: str = DATA_TRAIN,
                                shuffle: bool = True,
                                cutter: str = 'char',
                                max_count: int = 0) -> Tuple[List[List[str]], List[List[str]]]:
        """

        :param data_type: {train, validate, test}
        :param shuffle: shuffle or not
        :param cutter:
        :param max_count:
        :return:
        """
        folder_path = downloader.download_if_not_existed('corpus/' + cls.__corpus_name__,
                                                         'corpus/' + cls.__zip_file__name)
        if data_type not in [DATA_TRAIN, DATA_VALIDATE, DATA_TEST]:
            raise ValueError('data_type error, please use one onf the {}'.format([DATA_TRAIN,
                                                                                  DATA_VALIDATE,
                                                                                  DATA_TEST]))
        if cutter not in ['char', 'jieba', 'none']:
            raise ValueError('data_type error, please use one onf the {}'.format([DATA_TRAIN,
                                                                                  DATA_VALIDATE,
                                                                                  DATA_TEST]))

        file_path = os.path.join(folder_path, '{}.csv'.format(data_type))
        df = pd.read_csv(file_path)
        x_data = df['text'].values
        y_data = df['domain'].values
        if shuffle:
            x_data, y_data = helper.unison_shuffled_copies(x_data, y_data)

        if max_count != 0:
            x_data = x_data[:max_count]
            y_data = y_data[:max_count]

        if cutter == 'jieba':
            try:
                import jieba
            except ModuleNotFoundError:
                raise ModuleNotFoundError("please install jieba, `$ pip install jieba`")
            x_data = [list(jieba.cut(item)) for item in x_data]
        elif 'char':
            x_data = [list(item) for item in x_data]
        return x_data, y_data


if __name__ == '__main__':

    # init_logger()
    x, y = SMP2017ECDTClassificationData.get_classification_data()
    for i in range(5):
        print('{} -> {}'.format(x[i], y[i]))

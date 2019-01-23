# encoding: utf-8
"""
@author: BrikerMan
@contact: eliyar917@gmail.com
@blog: https://eliyar.biz

@version: 1.0
@license: Apache Licence
@file: cnn_lstm_model_test.py
@time: 2019-01-23 16:59

"""
import logging
import unittest

from kashgari.embeddings import WordEmbeddings, BERTEmbedding
from kashgari.tasks.classification import CNNLSTMModel


class CNNBLSTMModelTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(CNNBLSTMModelTest, self).__init__(*args, **kwargs)
        self.model = CNNLSTMModel()
        logging.info('init test')
        self.x_data = [
            list('语言学（英语：linguistics）是一门关于人类语言的科学研究'),
            list('语言学（英语：linguistics）是一门关于人类语言的科学研究'),
            list('语言学（英语：linguistics）是一门关于人类语言的科学研究'),
            list('语言学包含了几种分支领域。'),
            list('在语言结构（语法）研究与意义（语义与语用）研究之间存在一个重要的主题划分'),
        ]
        self.y_data = ['a', 'a', 'a', 'b', 'c']

        self.x_eval = [
            list('语言学是一门关于人类语言的科学研究。'),
            list('语言学包含了几种分支领域。'),
            list('在语言结构研究与意义研究之间存在一个重要的主题划分。'),
            list('语法中包含了词法，句法以及语音。'),
            list('语音学是语言学的一个相关分支，它涉及到语音与非语音声音的实际属性，以及它们是如何发出与被接收到的。'),
            list('与学习语言不同，语言学是研究所有人类语文发展有关的一门学术科目。'),
        ]

        self.y_eval = ['a', 'a', 'a', 'b', 'c', 'a']

    def test_build(self):
        self.model.fit(self.x_data, self.y_data)
        self.assertEqual(len(self.model.label2idx), 4)
        self.assertGreater(len(self.model.token2idx), 4)
        logging.info(self.model.embedding.token2idx)

    def test_fit(self):
        self.model.fit(self.x_data, self.y_data, x_validate=self.x_eval, y_validate=self.y_eval)

    def test_label_token_convert(self):
        self.test_fit()
        self.assertTrue(isinstance(self.model.label_to_token('a'), int))
        self.assertTrue(isinstance(self.model.token_to_label(1), str))

        self.assertTrue(all(isinstance(i, int) for i in self.model.label_to_token(['a'])))
        self.assertTrue(all(isinstance(i, str) for i in self.model.token_to_label([1, 2])))
        sentence = list('在语言结构（语法）研究与意义（语义与语用）研究之间存在一个重要的主题划分')
        tokens = self.model.embedding.tokenize(sentence)
        self.assertEqual(len(sentence)+2, len(tokens))

    def test_predict(self):
        self.test_fit()
        sentence = list('语言学包含了几种分支领域。')
        self.assertTrue(isinstance(self.model.predict(sentence), str))
        self.assertTrue(isinstance(self.model.predict([sentence]), list))
        logging.info('test predict: {} -> {}'.format(sentence, self.model.predict(sentence)))

    def test_eval(self):
        self.test_fit()
        self.model.evaluate(self.x_data, self.y_data)

    def test_bert(self):
        embedding = BERTEmbedding('chinese_L-12_H-768_A-12', sequence_length=30)
        embed_model = CNNLSTMModel(embedding=embedding)
        embed_model.fit(self.x_data, self.y_data)
        sentence = list('语言学包含了几种分支领域。')
        logging.info(embed_model.embedding.tokenize(sentence))
        logging.info(embed_model.predict(sentence))
        self.assertTrue(isinstance(embed_model.predict(sentence), str))
        self.assertTrue(isinstance(embed_model.predict([sentence]), list))

    def test_word2vec_embedding(self):
        embedding = WordEmbeddings('sgns.weibo.bigram', sequence_length=30, limit=5000)
        embed_model = CNNLSTMModel(embedding=embedding)
        embed_model.fit(self.x_data, self.y_data)
        sentence = list('语言学包含了几种分支领域。')
        logging.info(embed_model.embedding.tokenize(sentence))
        logging.info(embed_model.predict(sentence))
        self.assertTrue(isinstance(embed_model.predict(sentence), str))
        self.assertTrue(isinstance(embed_model.predict([sentence]), list))


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/python
from database import *

if __name__ == '__main__':
	print 'Creating Bootstrap Database Tables'
	question_types1 = QuestionType(key='fill-in',name='Fill in Question',answer_class='fill-in-ans')
	question_types1.save()
	question_types2 = QuestionType(key='key-no',name='Yes/No Questions',answer_class='yes-no-q')
	question_types2.save()
	question_types3 = QuestionType(key='musik',name='Musick Questions',answer_class='musik-q')
	question_types3.save()
	print 'Done!'

from mongoengine import *
import datetime, re, random

connect('notalicous_dev')

class Person(Document):
	fbid = IntField(unique=True)
	name = StringField(max_length=100)
	code = StringField()


class QuestionType(Document):
	key = StringField(max_length=10, required=True, unique=True, primary_key=True)
	name = StringField(max_length=30, required=True)
	answer_class = StringField(max_length=30)

class QuestionGroup(EmbeddedDocument):
	header = StringField(max_length=100)
	qtype = ReferenceField(QuestionType) 
	#qtypev
	questions = SortedListField(StringField(max_length=200))

class Note(Document):
	name = StringField(max_length=200, required=True)
	date_created = DateTimeField(default=datetime.datetime.now)
	permalink = StringField(max_length=50, unique=True)
	question_groups = ListField(EmbeddedDocumentField(QuestionGroup))
	creator = ReferenceField(Person)
	taken = IntField(default=0)
	meta = {
		'ordering': ['-date_created']
	}

def loadUser(token, fb):
	user, created = Person.objects(fbid=int(fb['id'])).get_or_create(defaults={'fbid':int(fb['id']),'code':token, 'name':fb['name']})
	if not created:
		user.code = token
		user.name = fb['name']
		user.save()
	return user

def createNote(json, person_id):
	person = Person.objects.with_id(person_id)
	groups = []
	def linkify(text):
		return re.sub(r'[^A-Za-z- ]','',text).replace(' ','-').lower()
	for section in json['sections']:
		if section['type'] in [q.key for q in QuestionType.objects.all()]: next
		groups.append(QuestionGroup(header=section['text'],qtype=section['type'],questions=section['questions']))
	link = linkify(json['name'])
	try:
		Note.objects.get(permalink=link)
		link = ('%s-%i' % (linkify(json['name']), random.randint(1,100)))
	except Note.DoesNotExist:
		pass	
	note = Note(name=json['name'],permalink=link,creator=person)
	note.question_groups=groups
	note.save(validate=False)
	return note
  

#class YesNoGroup(QuestionGroup):
#	questions = ListField(EmbeddedDocumentField(YesNoQuestion))
#class FieldGroup(QuestionGroup):
#questions = ListField(EmbeddedDocumentField(FieldQuestion))
#class MusikGroup(QuestionGroup):
#	questions = ListField(EmbeddedDocumentField(MusikQuestion))



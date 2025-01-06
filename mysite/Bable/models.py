# Copyright Aden Handasyde 2019

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User, UserManager, AbstractBaseUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import os
from django.urls import reverse
from django import forms
from mptt.models import MPTTModel, TreeForeignKey
from webpreview import web_preview

from django.conf import settings

import PIL.Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys

from datetime import timedelta
from random import choice
# from resizeimage import resizeimage

#from videofield.models import VideoField
# Create your models here.
def get_image_path(instance, filename):
    return settings.MEDIA_ROOT + str(instance.id) + '{}'.format(filename)
#Repeat of Words with OVERTOPVISION

# '/media/' for heroku
# settings.MEDIA_ROOT for local
class File(models.Model):
	file = models.FileField(upload_to='files', null=True)
	url2 = models.URLField(max_length=2000)
	filename = models.CharField(max_length=200, default='')
	public = models.BooleanField(default=False)
	creation_date = models.DateTimeField(default=timezone.now)

# Many to many fields create a A = .m2m(B), into a A_B hidden table. ie. it's backwards compatable with .m2m(B, through='AB')

class Notification(models.Model):
	text = models.CharField(max_length=200)
	link = models.URLField(max_length=2000, default='')
	username = models.CharField(max_length=150, default='', unique=True)
	sent = models.BooleanField(default=False)
	new = models.BooleanField(default=True)
	creation_date = models.DateTimeField(default=timezone.now)
	read_date = models.DateTimeField(default=timezone.now)
	click_date = models.DateTimeField(default=timezone.now)


# trying to save every change within the new saves, but not need a mirage of every other class.
class ChangeDate(models.Model):
	def __init__(self, charfield=None, textfield=None, **kwargs):
		if charfield:
			self.charfield = models.CharField(max_length=200, default='', unique=True)
		if textfield:
			self.textfield = models.TextField(max_length=1000, default='')
	each = models.DateTimeField(default=timezone.now)

class Requested_Agent(models.Model):
	user_agent = models.CharField(max_length=200, default='')
	datetime = models.DateTimeField(default=timezone.now)
	page = models.CharField(max_length=200, default='')
	if_username = models.CharField(max_length=200, default='')
	if_loggedin = models.BooleanField(default=False)


class Invoice(models.Model):
	amount = models.IntegerField(default=0)
	price_id = models.CharField(max_length=200, default='')
	item_name = models.CharField(max_length=200, default='')
	author = models.CharField(max_length=200, default='')
	success = models.BooleanField(default=False)
	submit_date = models.DateTimeField(default=timezone.now)

class Author(models.Model):
	username = models.CharField(max_length=150, default='', unique=True)
	spent_invoices = models.ManyToManyField(Invoice, default=None, related_name='spentinvoices')
	earnt_invoices = models.ManyToManyField(Invoice, default=None, related_name='earntinvoices')

	def to_anon(self):
		if Anon.objects.filter(username__username=self.username[0:149]).count():
			if not User.objects.filter(username=self.username[0:149]).count():
				user = User.objects.create(username=self.username[0:149], password="Password-2")
			else:
				user = User.objects.get(username=self.username[0:149])
			anon = Anon.objects.get(username=user)
			author, created = Author.objects.get_or_create(username=self.username[0:149])
			anons_posts = Post.objects.filter(author=author)
			for post in anons_posts:
				if post not in anon.posts.all():
					anon.posts.add(post)
			anon.save()
			return anon
		else:
			if not User.objects.filter(username=self.username[0:149]).count():
				user = User.objects.create(username=self.username[0:149], password="Password-2")
			else:
				user = User.objects.get(username=self.username[0:149])
			
			if Anon.objects.filter(username=user).count():
				anon = Anon.objects.get(username=user)
				anons_posts = Post.objects.filter(author=Author.objects.get(username=self.username[0:149]))
				for post in anons_posts:
					if post not in anon.posts.all():
						anon.posts.add(post)
				anon.save()
				return anon
			else:
				anon, created = Anon.objects.create(username=user)
				anons_posts = Post.objects.all().filter(author=Author.objects.get(username=self.username[0:149]))
				for post in anons_posts:
					if post not in anon.posts.all():
						anon.posts.add(post)
				anon.save()
				return anon


class Word_Source(models.Model):
	the_word_itself = models.CharField(max_length=200, default='')
	home_dictionary = models.CharField(max_length=200, default='')
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)

	word_id = models.CharField(max_length=256, default='')

	def to_full(self):
		return Word.objects.get(author=self.author, home_dictionary__the_dictionary_itself=self.home_dictionary, the_word_itself=self.the_word_itself)


class Searches(models.Model):
	the_search_itself = models.CharField(max_length=200, default='')
	creation_date = models.DateTimeField(default=timezone.now)


class Dictionary_Source(models.Model):
	the_dictionary_itself = models.CharField(max_length=200, default='')
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)
	words = models.ManyToManyField(Word_Source, default=None)
	purchasers = models.ManyToManyField(Author, default=None, related_name='dspurchasers')
	public = models.BooleanField(default=False)

	dictionary_id = models.CharField(max_length=256, default='')


	def __unicode__(self):
   		return self.the_dictionary_itself
	
	def to_full(self):
		return Dictionary.objects.get(author=self.author, the_dictionary_itself=self.the_dictionary_itself)

	def get_purchasers(self):
		self.to_full.get_allowed
		for purchaser in self.to_full.allowed_to_view_authors.all():
			self.purchasers.add(purchaser)


class Votes_Source(models.Model):
	the_vote_style = models.ManyToManyField(Word_Source, related_name='votestyle', default=None)
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)
	votes = models.IntegerField(default=0)
	the_vote_name = models.ForeignKey(Word_Source, on_delete=models.CASCADE, related_name='votename', default=None)

	def to_full(self):
		return Votes.objects.get(author=self.author, the_vote_name=self.the_vote_name__the_word_itself)

class Comment_Source(MPTTModel):
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)
	dictionaries = models.ManyToManyField(Dictionary_Source, default=None)
	sum_dictionaries = models.IntegerField(default=0)
	words = models.ManyToManyField(Word_Source, default=None)
	sum_words = models.IntegerField(default=0)
	body = models.TextField(max_length=144000, default='')
	votes = models.ManyToManyField(Votes_Source, default=None)
	votes_count = models.IntegerField(default=0)
	original = models.CharField(max_length=200, default='')
	parent = TreeForeignKey('self', on_delete=models.CASCADE, default=None, null=True, blank=True, related_name='children', db_index=True)

	def __str__(self):
		return self.body

	def __unicode__(self):
   		return unicode(self.body) or u''

	def children(self):
		return Comment_Sources.objects.filter(parent=self)

	@property
	def is_parent(self):
		if self.parent is not None:
			return False
		return True

	def to_original(self):
		return Comment.objects.get(id=self.original)

	class MPTTMeta:
		order_insertion_by = ['votes_count']



class SpaceSource(models.Model):
	the_space_itself = models.ForeignKey(Word_Source, on_delete=models.CASCADE, default=None)
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None, related_name='space_source_author')
	dictionary = models.ForeignKey(Dictionary_Source, on_delete=models.CASCADE, default=None)
	allowed_to_view_authors = models.ManyToManyField(Author, default=None, related_name='space_source_allowed')
	votessource = models.ManyToManyField(Votes_Source, default=None)

	def to_full(self):
		return Space.objects.get(author=self.author, the_space_itself=self.the_space_itself.to_full())




class Sponsor(models.Model):
	the_sponsorship_phrase = models.CharField(max_length=200, default='')
	latest_change_date = models.DateTimeField(default=timezone.now)
	img = models.URLField(max_length=2000)
	url2 = models.URLField(max_length=2000)
	clicks = models.IntegerField(default=0)
	active = models.BooleanField(default=True)
	payperview = models.BooleanField(default=False)
	price_limit = models.IntegerField(default=0)
	allowable_expenditure = models.IntegerField(default=0)
	amount_spent = models.IntegerField(default=0)
	trickles = models.IntegerField(default=0)
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)
	sponsored_on_word = models.CharField(max_length=140, default='')
	sponsored_on_dictionary = models.CharField(max_length=140, default='')
	sponsored_on_space = models.CharField(max_length=140, default='')
	sponsored_on_definition = models.CharField(max_length=140, default='')
	sponsored_on_price = models.CharField(max_length=140, default='')
	sponsored_on_searchurl = models.CharField(max_length=140, default='')
	sponsored_on_viewvariable = models.CharField(max_length=140, default='')
	sponsored_on_jobapp = models.CharField(max_length=140, default='')
	sponsored_on_job = models.CharField(max_length=140, default='')
	sponsored_on_anon = models.CharField(max_length=140, default='')
	sponsored_on_angelnumber = models.CharField(max_length=140, default='')
	sponsored_on_comment = models.CharField(max_length=140, default='')
	sponsored_on_barcode = models.CharField(max_length=140, default='')
	sponsored_on_post = models.CharField(max_length=140, default='')
	votes = models.ManyToManyField(Votes_Source, default=None)
	votes_count = models.IntegerField(default=0)
	has_voted = models.ManyToManyField(Author, related_name="spo_has_voted", default=None)
	views = models.IntegerField(default=0)
	requested_agents = models.ManyToManyField(Requested_Agent, default=None)

	
class Advertising(models.Model):
	email = models.EmailField(max_length=144, default='', null=True)
	allowable_expenditure = models.IntegerField(default=0)
	price_limit = models.IntegerField(default=0)
	words_to_sponsor = models.CharField(max_length=2000, default='')
	the_sponsorship_phrase = models.CharField(max_length=200, default='')
	latest_change_date = models.DateTimeField(default=timezone.now)
	img = models.URLField(max_length=2000)
	url2 = models.URLField(max_length=2000)
	clicks = models.IntegerField(default=0)
	payperview = models.BooleanField(default=False)
	trickles = models.IntegerField(default=0)
	name = models.CharField(max_length=2000, default='')
	views = models.IntegerField(default=0)
	requested_agents = models.ManyToManyField(Requested_Agent, default=None)


class Definition(models.Model):
	the_definition_itself = models.TextField(max_length=1000, default='')
	latest_change_date = models.DateTimeField(default=timezone.now)
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)
	votes = models.ManyToManyField(Votes_Source, default=None)
	votes_count = models.IntegerField(default=0)
	has_voted = models.ManyToManyField(Author, related_name="def_has_voted", default=None)
	views = models.IntegerField(default=0)
	comment_sources = models.ManyToManyField(Comment_Source, related_name="def_com", default=None)
	sponsors = models.ManyToManyField(Sponsor, default=None)
	sum_earnt_from_sponsors = models.IntegerField(default=0)
	max_sponsor_url = models.URLField(max_length=2000, blank=True, default='')
	max_sponsor_img = models.URLField(max_length=2000, blank=True, default='')
	max_sponsor_id = models.CharField(max_length=200, default='')
	max_sponsor_price = models.IntegerField(default=0)
	

	

#Repeat of Words with OVERTOPVISION-onedictionary_to_rule_them_all
class Translation(models.Model):
	the_translation_before = models.TextField(max_length=1000, default='')
	the_translation_after = models.TextField(max_length=1000, default='')
	latest_change_date = models.DateTimeField(default=timezone.now)
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)
	votes = models.ManyToManyField(Votes_Source, default=None)

	votes_count = models.IntegerField(default=0)
	has_voted = models.ManyToManyField(Author, related_name="tra_has_voted", default=None)
	views = models.IntegerField(default=0)
	comment_sources = models.ManyToManyField(Comment_Source, related_name="tra_com", default=None)

#Repeat of Words with OVERTOPVISION
class Connexion(models.Model):
	the_connexion_itself = models.CharField(max_length=200, default='')
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None, null=True)
	latest_change_date = models.DateTimeField(default=timezone.now)
	votes = models.ManyToManyField(Votes_Source, default=None)
	votes_count = models.IntegerField(default=0)
	has_voted = models.ManyToManyField(Author, related_name="con_has_voted", default=None)
	views = models.IntegerField(default=0)
	comment_sources = models.ManyToManyField(Comment_Source, related_name="con_com", default=None)

# ie. Metaphor, Spelling
class Simulacrum(models.Model):
	the_simulacrum_itself = models.CharField(max_length=200, default='')
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)
	latest_change_date = models.DateTimeField(default=timezone.now)
	connexia = models.ManyToManyField(Connexion, default=None)
	comment_sources = models.ManyToManyField(Comment_Source, related_name="sim_com", default=None)
	votes = models.ManyToManyField(Votes_Source, default=None)
	votes_count = models.IntegerField(default=0)
	has_voted = models.ManyToManyField(Author, related_name="sim_has_voted", default=None)
	views = models.IntegerField(default=0)

class Synonym(models.Model):
	the_synonym_itself = models.CharField(max_length=200, default='')
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)
	latest_change_date = models.DateTimeField(default=timezone.now)
	comment_sources = models.ManyToManyField(Comment_Source, related_name="syn_com", default=None)
	votes = models.ManyToManyField(Votes_Source, default=None)
	votes_count = models.IntegerField(default=0)
	has_voted = models.ManyToManyField(Author, related_name="syn_has_voted", default=None)
	views = models.IntegerField(default=0)

class Antonym(models.Model):
	the_antonym_itself = models.CharField(max_length=200, default='')
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)
	latest_change_date = models.DateTimeField(default=timezone.now)
	comment_sources = models.ManyToManyField(Comment_Source, related_name="ant_com", default=None)
	votes = models.ManyToManyField(Votes_Source, default=None)
	votes_count = models.IntegerField(default=0)
	has_voted = models.ManyToManyField(Author, related_name="ant_has_voted", default=None)
	views = models.IntegerField(default=0)

class Homonym(models.Model):
	the_homonym_itself = models.CharField(max_length=200, default='')
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)
	latest_change_date = models.DateTimeField(default=timezone.now)
	comment_sources = models.ManyToManyField(Comment_Source, related_name="hom_com", default=None)
	votes = models.ManyToManyField(Votes_Source, default=None)
	votes_count = models.IntegerField(default=0)
	has_voted = models.ManyToManyField(Author, related_name="hom_has_voted", default=None)
	views = models.IntegerField(default=0)

class Attribute(models.Model):
	the_attribute_itself = models.CharField(max_length=200, default='')
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None, null=True)
	views = models.IntegerField(default=0)
	latest_change_date = models.DateTimeField(default=timezone.now)
	creation_date = models.DateTimeField(default=timezone.now)
	definitions = models.ManyToManyField(Definition, default=None)
	definition_count = models.IntegerField(default=0)
	synonyms = models.ManyToManyField(Synonym, default=None)
	synonym_count = models.IntegerField(default=0)
	antonyms = models.ManyToManyField(Antonym, default=None)
	antonym_count = models.IntegerField(default=0)
	homonyms = models.ManyToManyField(Homonym, default=None)
	homonym_count = models.IntegerField(default=0)
	
ATTRIBUTE_SORT_CHOICES_CHAR = (
	("the_attribute_itself", "Alphabetical"),
	("-the_attribute_itself", "Anti Alphabetical"),
	("-views", "Most Viewed"),
	("views", "Least Viewed"),
	("-defintion_count", "Most Definitions"),
	("defintion_count", "Least Definitions"),
	("-synonym_count", "Most Synonyms"),
	("synonym_count", "Least Synonyms"),
	("-antonym_count", "Most Antonyms"),
	("antonym_count", "Least Antonyms"),
	("-homonym_count", "Most Homonyms"),
	("homonym_count", "Least Homonyms"),
	("-latest_change_date", "Most Recently Changed"),
	("latest_change_date", "Least Recently Changed"),
	("-creation_date", "Most Recently Created"),
	("creation_date", "Least Recently Created"),
)


# Change it so that the IPA characters is user definable, oh, they already are.
class IPA_pronunciation(models.Model):
	the_IPA_itself = models.CharField(max_length=200, default='')
	homophones = models.TextField(max_length=1000, default='')
	latest_change_date = models.DateTimeField(default=timezone.now)
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)
	votes = models.ManyToManyField(Votes_Source, default=None)
	votes_count = models.IntegerField(default=0)
	has_voted = models.ManyToManyField(Author, related_name="pro_has_voted", default=None)
	views = models.IntegerField(default=0)

class Example(models.Model):
	the_example_itself = models.TextField(max_length=1000, default='')
	words = models.ManyToManyField(Word_Source, default=None)
	word_count = models.IntegerField(default=0)
	dictionaries = models.ManyToManyField(Dictionary_Source, default=None)
	dictionary_count = models.IntegerField(default=0)
	latest_change_date = models.DateTimeField(default=timezone.now)
	comment_sources = models.ManyToManyField(Comment_Source, related_name="exa_com", default=None)
	comment_count = models.IntegerField(default=0)
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None, null=True)
	votes = models.ManyToManyField(Votes_Source, default=None)
	votes_count = models.IntegerField(default=0)
	has_voted = models.ManyToManyField(Author, related_name="exa_has_voted", default=None)
	views = models.IntegerField(default=0)

	

	def max_sponsor(self):
		max_price = 0
		pks = Sponsor.objects.values_list('pk', flat=True)
		random_pk = choice(pks)
		random_obj = Sponsor.objects.get(pk=random_pk)
		max_sponsor = random_obj
		for word in self.words.all():
			for sponsor in word.to_full().sponsors.all().filter(payperview=False):
				if sponsor.allowable_expenditure >= sponsor.price_limit:
					if sponsor.price_limit >= max_price:
						max_price = sponsor.price_limit
						max_sponsor = sponsor
		return max_sponsor

EXAMPLE_SORT_CHOICES = (
	(0, "freshest"),
	(1, "oldest"),
	(2, "precision"),
	(3, "votes"),
	(4, "unseen"),
	(5, "views"),
	

)


EXAMPLE_SORT_CHOICES_CHAR = (
	("the_example_itself", "Alphabetical"),
	("-the_example_itself", "Backwards Alpha"),
	("word_count", "Most Words"),
	("-word_count", "Least Words"),
	("dictionary_count", "Most Dics"),
	("-dictionary_count", "Least Dics"),
	("comment_count", "Most Comments"),
	("-comment_count", "Least Comments"),
	("views", "Most Viewed"),
	("-views", "Most Viewed"),
	

)



class Story(models.Model):
	the_story_itself = models.TextField(max_length=4000, default='')
	latest_change_date = models.DateTimeField(default=timezone.now)
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)
	votes = models.ManyToManyField(Votes_Source, default=None)
	votes_count = models.IntegerField(default=0)
	has_voted = models.ManyToManyField(Author, related_name="sto_has_voted", default=None)
	views = models.IntegerField(default=0)
	comment_sources = models.ManyToManyField(Comment_Source, related_name="sto_com", default=None)

class Relation(models.Model):
	the_relation_itself = models.CharField(max_length=200, default='')
	latest_change_date = models.DateTimeField(default=timezone.now)
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)
	votes = models.ManyToManyField(Votes_Source, default=None)
	votes_count = models.IntegerField(default=0)
	has_voted = models.ManyToManyField(Author, related_name="rel_has_voted", default=None)
	views = models.IntegerField(default=0)
	comment_sources = models.ManyToManyField(Comment_Source, related_name="rel_com", default=None)


SPONSOR_SORT_CHOICES = (
	(0, "alphabetical"),
	(1, "-alphabetical"),
	(2, "latest"),
	(3, "oldest"),
	(4, "lowtohigh"),
	(5, "hightolow"),
	(6, "low allowable"),
	(7, "high allowable"),
	(8, "votes"),
	(9, "-votes"),
	(10, "views"),
	(11, "-views"),
)

SPONSOR_SORT_CHOICES_CHAR = (
	("the_sponsorship_phrase", "Alphabetical"),
	("-the_sponsorship_phrase", "Reverse Alphabetical"),
	("latest_change_date", "Least Recent Change"),
	("-latest_change_date", "Most Recent Change"),
	("price_limit", "Price Limit"),
	("-price_limit", "Affordability Limit"),
	("allowable_expenditure", "Most Expenditure"),
	("-allowable_expenditure", "Least Expenditure"),
	("votes_count", "Most Votes"),
	("-votes_count", "Least Votes"),
	("views", "Most Views"),
	("-views", "Least Views"),
)


class Fontstyle(models.Model):
	css_encoding = models.URLField(max_length=20000, blank=True, default='')
	order = models.IntegerField(default=0)
	duration = models.IntegerField(default=100)
	

from numpy.random import choice

class Word(models.Model):
	the_word_itself	= models.CharField(max_length=200, default='')
	home_dictionary = models.ForeignKey(Dictionary_Source, on_delete=models.CASCADE, default=None, null=True)
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None, related_name='word_author', null=True)
	latest_change_date = models.DateTimeField(default=timezone.now)
	creation_date = models.DateTimeField(default=timezone.now)
	pronunciations = models.ManyToManyField(IPA_pronunciation, default=None)
	pronunciation_count = models.IntegerField(default=0)
	attributes = models.ManyToManyField(Attribute, default=None)
	attribute_count = models.IntegerField(default=0)
	similarities = models.ManyToManyField(Simulacrum, default=None)
	similarity = models.IntegerField(default=0)
	translations = models.ManyToManyField(Translation, default=None)
	translation_count = models.IntegerField(default=0)
	examples = models.ManyToManyField(Example, default=None)
	example_count = models.IntegerField(default=0)
	stories = models.ManyToManyField(Story, default=None)
	story_count = models.IntegerField(default=0)
	relations = models.ManyToManyField(Relation, default=None)
	relation_count = models.IntegerField(default=0)
	sponsors = models.ManyToManyField(Sponsor, default=None)
	sponsor_count = models.IntegerField(default=0)
	sum_earnt_from_sponsors = models.IntegerField(default=0)
	max_sponsor_url = models.URLField(max_length=2000, blank=True, default='')
	max_sponsor_img = models.URLField(max_length=2000, blank=True, default='')
	max_sponsor_id = models.CharField(max_length=200, default='')
	max_sponsor_price = models.IntegerField(default=0)
	
	price_limit = models.IntegerField(default=0) # NEED TO MAKE IT LEGIT
	viewcount = models.IntegerField(default=0)
	spaces = models.ManyToManyField(SpaceSource, default=None)
	space_count = models.IntegerField(default=0)
	votes = models.ManyToManyField(Votes_Source, default=None)
	vote_count = models.IntegerField(default=0)
	ap_voters = models.ManyToManyField(Author, default=None, related_name="ap_voters")
	ap_voter_count = models.IntegerField(default=0)
	fontstyling = models.ManyToManyField(Fontstyle, default=None)
	fontstyle_repeat = models.BooleanField(default=True)
	fontsize = models.CharField(max_length=3, blank=True, default='')
	fontype = models.TextField(max_length=14400, default='')

	word_source = models.CharField(max_length=400, default='')

	word_wallet = models.IntegerField(default=0)
	
	class Meta:
		unique_together = (('home_dictionary', 'the_word_itself'),)


	def to_source(self):
		return Word_Source.objects.filter(author=self.author, the_word_itself=self.the_word_itself, home_dictionary=self.home_dictionary.the_dictionary_itself).first()

	def get_approved(self):
		self.home_dictionary.get_purchasers
		for purchaser in self.home_dictionary.purchasers.all():
			self.ap_voters.add(purchaser)


	def random_sponsor(self):
		if self.sponsors.count():
			return self.sponsors.all().order_by('?').first()
		else:
			return Sponsor.objects.get(id=1)
		



	# for every word in the sponsorship phrase, look for dictionaries owned by the owner of the word, and if those dictionaries contain that word in the sponsorship phrase 
	# then the spaces with that word, every post and comment in that space, and the space itself are also sponsored so you if like someone's "style" of content you can benefit every member of their tribe.'
	def trickle(self):
		for sponsor in self.sponsors.all():
			if sponsor.trickles>0:
				words = sponsor.the_sponsorship_phrase.split(" ")
				trickle = {}
				for word in words:
					for dic in self.Author.to_anon().dictionaries.all():
						for dics_word in dic.words.all():
							if word in dics_word.the_word_itself:
								for space in dics_word.spaces.all():
									trickle.append(space)
									space.sponsors.add(sponsor)
				for space in trickle:
					for post in space.posts.all():
						post.sponsors.add(sponsor)
						for dic in post.dictionaries.all():
							for word in dic.words.all():
								word.sponsors.add(sponsor)
						for com in post.comments.all():
							com.sponsors.add(sponsor)
							for dic in com.dictionaries.all():
								for word in dic.words.all():
									word.sponsors.add(sponsor)
				sponsor.trickle_down -= 1

	def update_sponsors(self):
		for sponsor in self.sponsors.all():
			if (sponsor.allowable_expenditure == 0 and sponsor.price_limit != 0) or (sponsor.author.to_anon().false_wallet < sponsor.price_limit):
				self.sponsors.remove(sponsor)
				sponsor.delete()

	def max_sponsor(self):
		max_sponsor = self.sponsors.all().order_by('-price_limit').first()
		self.max_sponsor_id = max_sponsor.id
		self.max_sponsor_url = max_sponsor.url
		self.max_sponsor_price = max_sponsor.price
		self.max_sponsor_img = max_sponsor.img
		self.save()
		return max_sponsor


WORD_SORT_CHOICES = (
	(0, "alphabetical"),
	(1, "latest"),
	(2, "definitions"),
	(3, "pronunciations"),
	(4, "attributes"),
	(5, "similarities"),
	(6, "translations"),
	(7, "examples"),
	(8, "relations"),
	(9, "sponsor"),
	(10, "viewcount"),
	(11, "-viewcount"),
	(12, "price"),
	(13, "-price"),
	(14, "spaces"),
	(15, "stories"),
	(16, "votes"),
	(17, "-votes"),
)

WORD_SORT_CHOICES_CHAR = (
	("the_word_itself", "Alphabetical"),
	("-the_word_itself", "Anti Alphabetical"),
	("-latest_change_date", "Most Recent Change"),
	("latest_change_date", "Least Recent Change"),
	("-creation_date", "Most Recently Created"),
	("creation_date", "Least Recently Created"),
	("-pronunciation_count", "Most Pronunciations"),
	("pronunciation_count", "Least Pronunciations"),
	("-attribute_count", "Most Attributes"),
	("attribute_count", "Least Attributes"),
	("-similarity_count", "Most Similarities"),
	("similarity_count", "Least Similarities"),
	("-translation_count", "Most Translations"),
	("translation_count", "Least Translations"),
	("-example_count", "Most Examples"),
	("example_count", "Least Examples"),
	("-relation_count", "Most Relations"),
	("relation_count", "Least Relations"),

	("-sponsor_count", "Most Sponsors"),
	("sponsor_count", "Least Sponsors"),
	("-viewcount", "Most Viewed"),
	("viewcount", "Least Viewed"),
	("-price_limit", "Most Expensive"),
	("price_limit", "Least Expensive"),
	("-space_count", "Most Spaces"),
	("space_count", "Least Spaces"),
	("-story_count", "Most Stories"),
	("story_count", "Least Stories"),
	("-vote_count", "Most Votes"),
	("vote_count", "Least Votes"),
)

class Votes(models.Model):
	the_vote_name = models.CharField(max_length=200, default='', unique=True)
	url2 = models.URLField(max_length=2000, blank=True, default='')
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)
	the_vote_style = models.ForeignKey(SpaceSource, on_delete=models.CASCADE, related_name='votename', default=1)
	votes = models.IntegerField(default=0)
	voters = models.ManyToManyField(Author, related_name="votestyle_voters", default=None)
	voters_count = models.IntegerField(default=0)
	
	creation_date = models.DateTimeField(default=timezone.now)

	def to_source(self):
		return Votes_Source.objects.get(author=author, the_vote_name__the_word_itself=the_vote_name)


class Votings(models.Model):
	votes = models.ManyToManyField(Votes, default=None)
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)
	sponsors = models.ManyToManyField(Sponsor, default=None)
	sum_earnt_from_sponsors = models.IntegerField(default=0)
	max_sponsor_url = models.URLField(max_length=2000, blank=True, default='')
	max_sponsor_img = models.URLField(max_length=2000, blank=True, default='')
	max_sponsor_id = models.CharField(max_length=200, default='')
	max_sponsor_price = models.IntegerField(default=0)
	
	
	ip = models.CharField(max_length=15, default="")
	creation_date = models.DateTimeField(default=timezone.now)


DATE_CHOICES_CHAR = (
	("0,0,0,0","0 Minutes"),
	("15,0,0,0","15 Minutes"),
	("30,0,0,0","30 Minutes"),
	("45,0,0,0","45 Minutes"),
	("0,1,0,0","Hourly"),
	("0,2,0,0","2 Hourly"),
	("0,4,0,0","4 Hourly"),
	("0,6,0,0","6 Hourly"),
	("0,8,0,0","8 Hourly"),
	("0,10,0,0","10 Hourly"),
	("0,12,0,0","12 Hourly"),
	("0,16,0,0","16 Hourly"),
	("0,18,0,0","18 Hourly"),
	("0,20,0,0","20 Hourly"),
	("0,0,1,0","1 Daily"),
	("0,36,0,0","1.5 Daily"),
	("0,0,2,0","2 Daily"),
	("0,0,3,0","3 Daily"),
	("0,0,4,0","4 Daily"),
	("0,0,5,0","5 Daily"),
	("0,0,0,1","Weekly"),
	("0,0,0,2","2 Weekly"),
	("0,0,0,4","4 Weekly"),
	("0,0,0,8","8 Weekly"),
	("0,0,0,12","12 Weekly"),
	("0,0,0,16","16 Weekly"),
	("0,0,0,26","26 Weekly"),
	("0,0,0,39","39 Weekly"),
	("0,0,0,52","52 Weekly"),
	("0,0,0,78","78 Weekly"),
	("0,0,0,104","104 Weekly"),
	("0,0,0,156","156 Weekly"),
	("0,0,0,208","208 Weekly"),
	("0,0,0,260","260 Weekly"),
	("0,0,0,10000","All Time"),
)


# of difference
class Analysis(models.Model):
	the_critique_itself = models.ManyToManyField(Word, default=None)
	latest_change_date = models.DateTimeField(default=timezone.now)
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)
	votes = models.ManyToManyField(Votes, default=None)
	vote_count = models.IntegerField(default=0)
	the_owner = models.CharField(max_length=200, default='')
	viewcount = models.IntegerField(default=0)


class Rendition(models.Model):
	the_rendition_itself = models.ManyToManyField(Word, default=None)
	latest_change_date = models.DateTimeField(default=timezone.now)
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)
	votes = models.ManyToManyField(Votes, default=None)
	vote_count = models.IntegerField(default=0)
	the_owner = models.CharField(max_length=200, default='')
	views = models.IntegerField(default=0)

class Sentence(models.Model):
	the_sentence_itself = models.ManyToManyField(Word, default=None)
	renditions = models.ManyToManyField(Rendition, default=None)
	latest_change_date = models.DateTimeField(default=timezone.now)
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)
	votes = models.ManyToManyField(Votes, default=None)
	vote_count = models.IntegerField(default=0)
	the_owner = models.CharField(max_length=200, default='')
	views = models.IntegerField(default=0)

class True_Translation(models.Model):
	the_translation_before = models.ManyToManyField(Word, default=None, related_name="translation_from_words")
	the_translation_after = models.ManyToManyField(Word, default=None, related_name="translation_to_words")
	latest_change_date = models.DateTimeField(default=timezone.now)
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)
	votes = models.ManyToManyField(Votes, default=None)
	vote_count = models.IntegerField(default=0)
	views = models.IntegerField(default=0)
ATTRIBUTE_SORT_CHOICES = (
	(0, "latest"),
	(1, "definitions"),
	(2, "votes"),
	(3, "-votes"),
	(4, "views"),
	(5, "-views"),
)



class Wordgroup_Source(models.Model):
	grouping = models.CharField(max_length=200)
	words = models.ManyToManyField(Word, default=None)
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)

class Wordgroup(models.Model):
	grouping = models.CharField(max_length=200)
	words = models.ManyToManyField(Wordgroup_Source, default=None)
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)

class Purchase_Order(models.Model):
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)
	last_paid = models.DateTimeField(default=timezone.now)


REPAYMENT_RATES = (
	("hourly", "Hourly"),
	("daily", "Daily"),
	("weekly", "Weekly"),
	("monthly", "Monthly"),
	("yearly", "Yearly"),
)

class Word_Loan(models.Model):
	amount_total = models.IntegerField(default=0)
	amount_owing = models.IntegerField(default=0)
	repayment_term = models.DateTimeField(default=timezone.now)
	pro_rata = models.FloatField(default=0.08)
	repayment_rates = models.CharField(default="hourly", choices=REPAYMENT_RATES, max_length=144)
	total_repayments_remaining = models.IntegerField(default=1)
	total_repayments = models.IntegerField(default=1)
	words = models.ManyToManyField(Word, default=None)


PRODUCT_CHOICES = (

	("unspecified", "Unspecified"),
	("package_post", "Posted Package"),
	("package_courier", "Courier Routes Package"),
	("package_direct", "Choose A Courier"),
	("package_pick_up", "Pick Up Yourself (with a pick-up)"),
	("package_collect", "Collect Yourself (by hand)"),
	("link", "Collect Links"),
	("poem", "Just Words"),
	("tickets", "Event Tickets"),
	("classes", "Classes"),
	("class_material", "Class Material"),
	("other", "Other Deal"),
)

class TimeAndRangePrices(models.Model):
	from_time_starting = models.DateTimeField(timezone.now)
	to_times_ending = models.DateTimeField(timezone.now)
	south_corner = models.DecimalField(max_digits=9, decimal_places=6)
	north_corner = models.DecimalField(max_digits=9, decimal_places=6)
	east_corner = models.DecimalField(max_digits=9, decimal_places=6)
	west_corner = models.DecimalField(max_digits=9, decimal_places=6)

	south_to_north_distance = models.IntegerField(default=0)
	south_to_north_midpoint = models.DecimalField(max_digits=9, decimal_places=6)
	south_to_east_distance = models.IntegerField(default=0)
	south_to_west_distance = models.IntegerField(default=0)
	north_to_east_distance = models.IntegerField(default=0)
	north_to_west_distance = models.IntegerField(default=0)
	east_to_west_distance = models.IntegerField(default=0)
	east_to_west_midpoint = models.DecimalField(max_digits=9, decimal_places=6)
	willing_for_price_per_kilometre = models.IntegerField(default=0)
	willing_for_price_per_kilogram = models.IntegerField(default=0)
	max_kilometre = models.IntegerField(default=0)
	max_kilogram = models.IntegerField(default=0)
	
	max_room_length = models.IntegerField(default=0)
	max_room_height = models.IntegerField(default=0)
	max_room_width = models.IntegerField(default=0)
	creation_date = models.DateTimeField(timezone.now)


TIME_AND_RANGE_PRICES_SORT_CHOICES_CHAR = (
	("-from_time_starting", "Latest Time Starting"),
	("from_time_starting", "Earliest Time Starting"),
	("-to_times_ending", "Latest Time Ending"),
	("to_times_ending", "Earliest Time Ending"),
	("south_corner", "Southernmost South Boundary"),
	("-south_corner", "Northernmost South Boundary"),
	("north_corner", "Southernmost North Boundary"),
	("-north_corner", "Northernmost North Boundary"),
	("east_corner", "Easternmost East Boundary"),
	("-east_corner", "Westernmost East Boundary"),
	("west_corner", "Easternmost West Boundary"),
	("-west_corner", "Westernmost West Boundary"),
	("willing_for_price_per_kilometre", "Lowest Cost Per Km"),
	("-willing_for_price_per_kilometre", "Highest Cost Per Km"),
	("willing_for_price_per_kilogram", "Lowest Cost Per Kg"),
	("-willing_for_price_per_kilogram", "Highest Cost Per Kg"),
	("max_kilometre", "Lowest Allowed Km"),
	("-max_kilometre", "Highest Allowed Km"),
	("max_kilogram", "Lowest Allowed Kg"),
	("-max_kilogram", "Highest Allowed Kg"),
	("max_room_width", "Lowest Allowed Width"),
	("-max_room_width", "Highest Allowed Width"),
	("max_room_height", "Lowest Allowed Height"),
	("-max_room_height", "Highest Allowed Height"),
	("max_room_length", "Lowest Allowed Length"),
	("-max_room_length", "Highest Allowed Length"),
	("creation_date", "Earliest Creation"),
	("-creation_date", "Latest Creation"),
	
	
)


class Courier(models.Model):
	from_location = models.CharField(max_length=1440, default="")
	from_name = models.CharField(max_length=1440, default="")
	product_name = models.CharField(max_length=1440, default="")
	product_description = models.CharField(max_length=1440, default="")
	product_img = models.URLField(max_length=20000, default="")
	to_country = models.CharField(max_length=1440, default="")
	to_state = models.CharField(max_length=1440, default="")
	to_city = models.CharField(max_length=1440, default="")
	to_address = models.CharField(max_length=1440, default="")
	to_name = models.CharField(max_length=1440, default="")
	update = models.CharField(max_length=1440, default="")
	creation_date = models.DateTimeField(timezone.now)
	leave_from_time = models.DateTimeField(timezone.now)
	estimated_arrival_time = models.DateTimeField(timezone.now)
	driver = models.CharField(max_length=140, default='') # USERNAME
	order = models.IntegerField(default=0)
	fees = models.IntegerField(default=0)
	deliver_to_instructions = models.CharField(max_length=1440, default="Leave By Postbox")
	

class Deliverer(models.Model):
	username = models.CharField(max_length=140, default='')
	
	previous_open_offers = models.ManyToManyField(TimeAndRangePrices, default=None, related_name="previous_open_offers")
	open_offers = models.ManyToManyField(TimeAndRangePrices, default=None, related_name="open_offers")
	completed_offers = models.ManyToManyField(Courier, default=None, related_name="completed_offers")
	completed_offers_count = models.IntegerField(default=0)
	planned_offers = models.ManyToManyField(Courier, default=None, related_name="planned_offers")
	planned_offers_count = models.IntegerField(default=0)
	money_earnt = models.IntegerField(default=0)
	kilograms_transported = models.IntegerField(default=0)
	kilograms_transporting = models.IntegerField(default=0)
	kilometres_travelled = models.IntegerField(default=0)
	kilometres_travelling = models.IntegerField(default=0)
	people_delivered_from_count = models.IntegerField(default=0)
	people_delivered_to_count = models.IntegerField(default=0)



DELIVERER_SORT_CHOICES_CHAR = (
	("username", "Alphabetic Name"),
	("-username", "Reverse Alphabetic Name"),
	("-completed_offers_count", "Most Deliveries Completed"),
	("completed_offers_count", "Least Deliveries Completed"),
	("-planned_offers_count", "Most Deliveries Planned"),
	("planned_offers_count", "Least Deliveries Planned"),
	("-money_earnt", "Most Money Earnt"),
	("money_earnt", "Least Money Earnt"),
	("-kilograms_transported", "Most Kilograms Transported"),
	("kilograms_transported", "Least Kilograms Transported"),
	("-kilograms_transporting", "Most Kilograms Transporting"),
	("kilograms_transporting", "Least Kilograms Transporting"),
	("-kilometres_travelled", "Most Kilometres Travelled"),
	("kilometres_travelled", "Least Kilometres Travelled"),
	("-kilometres_travelled", "Most Kilometres Travelling"),
	("kilometres_travelled", "Least Kilometres Travelling"),
)
 


class Sale(models.Model):
	user = models.OneToOneField(Author, default=None, on_delete=models.PROTECT)
	price_id = models.CharField(max_length=200, default="")
	courier_routing = models.ManyToManyField(Courier, default=None)
	

	def get_price_price(self):
		return Price.objects.get(id=self.price_id).price
	

class Price(models.Model):
    name = models.CharField(max_length=200, default='')
    anon_user_id = models.CharField(max_length=256, default='')
    url2purchase = models.URLField(max_length=2000, blank=True, default='')
    description2purchase = models.TextField(max_length=144000, default='')
    description2helpsell = models.TextField(max_length=144000, default='')
    img = models.URLField(max_length=2000, blank=True, default='')
    stripe_price_id = models.CharField(max_length=100, default='')
    stripe_product_id = models.CharField(max_length=100, default='')
    price = models.IntegerField(default=0)  # cents
    latest_change_date = models.DateTimeField(default=timezone.now)

    monthly = models.BooleanField(default=False)
    comments = models.ManyToManyField(Comment_Source, default=None)
    sum_comments = models.IntegerField(default=0)
    invoices = models.ManyToManyField(Invoice, default=None)
    sum_invoices = models.IntegerField(default=0)

    sponsors = models.ManyToManyField(Sponsor, default=None)
    sum_earnt_from_sponsors = models.IntegerField(default=0)
    sum_sponsors = models.IntegerField(default=0)
    max_sponsor_url = models.URLField(max_length=2000, blank=True, default='')
    max_sponsor_img = models.URLField(max_length=2000, blank=True, default='')
    max_sponsor_id = models.CharField(max_length=200, default='')
    max_sponsor_price = models.IntegerField(default=0)
	

    views = models.IntegerField(default=0)

    #location_of_product = models.CharField(max_length=200, default='Remote')
    point_of_sale = models.ManyToManyField(Sale, default=None)

    #product_type = models.CharField(choices=PRODUCT_CHOICES, max_length=200, default='unspecified')
    
    def author(self):
    	return Author.objects.get(username=Anon.objects.get(id=anon_user_id).username.username)

    def get_display_price(self):
        return "{0:.2f}".format(self.price / 100)

    def max_sponsor(self):
    	return self.sponsors.all().order_by('-price_limit').first() or Sponsor.all().order_by('-price_limit').first()


PRODUCT_SORT_CHOICES_CHAR = (
	("name", "Name Alphabetical"),
	("-name", "Name Reverse Alphabetical"),
	("price", "Most Expensive"),
	("-price", "Least Expensive"),
	("latest_change_date", "Most Recently Changed"),
	("-latest_change_date", "Least Recently Changed"),
	("sum_comments", "Most Commented"),
	("-sum_comments", "Least Commented"),
	("sum_invoices", "Most Purchased"),
	("-sum_invoices", "Least Purchased"),
	("sponsor_count", "Most Sponsors"),
	("-sponsor_count", "Least Sponsors"),
	("views", "Most Views"),
	("-views", "Least Views"),
)



class Storefront(models.Model):
	author = models.OneToOneField(Author, default=None, on_delete=models.PROTECT)
	logo = models.OneToOneField(Word, default=None, on_delete=models.PROTECT)
	title = models.TextField(max_length=144, default="")
	preview_text = models.TextField(max_length=1440, default="")
	disclaimer = models.TextField(max_length=1440, default="")
	image_1 = models.URLField(max_length=2000, default="")
	image_2 = models.URLField(max_length=2000, default="")
	image_3 = models.URLField(max_length=2000, default="")
	image_4 = models.URLField(max_length=2000, default="")
	image_5 = models.URLField(max_length=2000, default="")
	template_section_size_title_left = models.IntegerField(default=0)
	template_section_size_title_right = models.IntegerField(default=0)
	template_section_size_title_height = models.IntegerField(default=100)
	template_section_size_preview_left = models.IntegerField(default=0)
	template_section_size_preview_right = models.IntegerField(default=0)
	template_section_size_preview_height = models.IntegerField(default=100)
	template_section_size_disclaimer_left = models.IntegerField(default=0)
	template_section_size_disclaimer_right = models.IntegerField(default=0)
	template_section_size_disclaimer_height = models.IntegerField(default=100)
	textblock_1  = models.TextField(max_length=14400, default="")
	textblock_2  = models.TextField(max_length=14400, default="")
	textblock_3  = models.TextField(max_length=14400, default="")
	textblock_4  = models.TextField(max_length=14400, default="")
	products = models.ManyToManyField(Price, default=None)
	products_count = models.IntegerField(default=0)
	sales = models.ManyToManyField(Sale, default=None)
	sales_count = models.IntegerField(default=0)
	business_admin = models.ManyToManyField(Author, default=None, related_name="business_admin")
	business_admins_count = models.IntegerField(default=0)

	views = models.IntegerField(default=0)

	latest_change_date = models.DateTimeField(default=timezone.now)

	def total_product_value(self):
		tally = 0
		for product in self.products.all():
			tally += product.price
		return tally

	def total_sales_made(self):
		tally = 0
		for sale in self.sales.all():

			tally += sale.get_price_price()
		return tally
	

STOREFRONT_SORT_CHOICES_CHAR = (
	("author__username", "Author Alphabetical"),
	("-author__username", "Author Reverse Alphabetical"),
	("logo__the_word_itself", "Logo Alphabetical"),
	("-logo__the_word_itself", "Logo Reverse Alphabetical"),
	("logo__home_dictionary__the_dictionary_itself", "Logo Home Dic Alpha"),
	("-logo__home_dictionary__the_dictionary_itself", "Logo Home Dic Reverse Alpha"),
	("logo__author__username", "Logo Author Alpha"),
	("-logo__author__username", "Logo Author Reverse Alpha"),
	("title", "Title Alphabetical"),
	("-title", "Title Reverse Alphabetical"),
	("products_count", "Most Products"),
	("-products_count", "Least Products"),
	("sales_count", "Most Sales"),
	("-sales_count", "Least Sales"),
	("business_admins_count", "Most Business Partners"),
	("-business_admins_count", "Least Business Partners"),
	("latest_change_date", "Most Recent Change"),
	("-latest_change_date", "Least Recent Change"),
	("views", "Most Viewed"),
	("-views", "Least Viewed"),
)

LOCATION_CHOICES_CHAR = (
	("on_site","On-site"),
	("remote","Remote"),
	("hybrid","Hybrid"),
)


class JobApplication(models.Model):
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)
	public = models.BooleanField(default=False)


	job_id = models.CharField(max_length=2000, default="")

	invite_only = models.BooleanField(default=False)
	invite_active = models.BooleanField(default=False)
	invite_code = models.CharField(max_length=200, default='')

	sponsors = models.ManyToManyField(Sponsor, default=None)
	sum_earnt_from_sponsors = models.IntegerField(default=0)
	sum_sponsors = models.IntegerField(default=0)
	max_sponsor_url = models.URLField(max_length=2000, blank=True, default='')
	max_sponsor_img = models.URLField(max_length=2000, blank=True, default='')
	max_sponsor_id = models.CharField(max_length=200, default='')
	max_sponsor_price = models.IntegerField(default=0)
	

	views = models.IntegerField(default=0)
	latest_change_date = models.DateTimeField(default=timezone.now)
	creation_date = models.DateTimeField(default=timezone.now)

	location_type = models.CharField(choices=LOCATION_CHOICES_CHAR, default="on_site", max_length=180)
	location = models.CharField(max_length=200, default='')

	company_name = models.CharField(max_length=200, default='')
	reference_link = models.URLField(max_length=20000, default='')

	character_description = models.TextField(max_length=1400, default="Character Description: ")
	character_values = models.TextField(max_length=1400, default="Character Values: ")
	personal_vision = models.TextField(max_length=1400, default="Personal Vision: ")
	personal_mission = models.TextField(max_length=1400, default="Personal Mission: ")
	impact_desires = models.TextField(max_length=1400, default="Impact Desires: ")
	related_job_description = models.TextField(max_length=1400, default="Related Job Description: ")
	related_position_summary = models.TextField(max_length=1400, default="Related Position Summary: ")
	related_qualifications = models.TextField(max_length=1400, default="Related Qualifications: ")
	related_knowledge = models.TextField(max_length=1400, default="Related Knowledge: ")
	related_skills = models.TextField(max_length=1400, default="Related Skills: ")
	related_experience = models.TextField(max_length=1400, default="Related Experience: ")
	desired_compensation = models.TextField(max_length=1400, default="Desired Compensation: ")
	additional_information = models.TextField(max_length=1400, default="Additional Information: ")

	


class Job(models.Model):
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)
	public = models.BooleanField(default=False)

	invite_only = models.BooleanField(default=False)
	invite_active = models.BooleanField(default=False)
	invite_code = models.CharField(max_length=200, default='')

	expires_by = models.DateTimeField(default=timezone.now)

	sponsors = models.ManyToManyField(Sponsor, default=None)
	sum_earnt_from_sponsors = models.IntegerField(default=0)
	sum_sponsors = models.IntegerField(default=0)
	max_sponsor_url = models.URLField(max_length=2000, blank=True, default='')
	max_sponsor_img = models.URLField(max_length=2000, blank=True, default='')
	max_sponsor_id = models.CharField(max_length=200, default='')
	max_sponsor_price = models.IntegerField(default=0)
	

	views = models.IntegerField(default=0)
	latest_change_date = models.DateTimeField(default=timezone.now)
	creation_date = models.DateTimeField(default=timezone.now)

	location_type = models.CharField(choices=LOCATION_CHOICES_CHAR, default="on_site", max_length=180)
	location = models.CharField(max_length=200, default='')

	company_name = models.CharField(max_length=200, default='')
	reference_link = models.URLField(max_length=20000, default='')

	company_description = models.TextField(max_length=1400, default="Company Description: ")
	company_values = models.TextField(max_length=1400, default="Company Values: ")
	company_vision = models.TextField(max_length=1400, default="Company Vision: ")
	company_mission = models.TextField(max_length=1400, default="Company Mission: ")
	impact_report = models.TextField(max_length=1400, default="Impact Report: ")
	job_description = models.TextField(max_length=1400, default="Job Description: ")
	position_summary = models.TextField(max_length=1400, default="Position Summary: ")
	qualifications = models.TextField(max_length=1400, default="Qualifications: ")
	knowledge_required = models.TextField(max_length=1400, default="Knowledge Required: ")
	skills_required = models.TextField(max_length=1400, default="Skills Required: ")
	experience_required = models.TextField(max_length=1400, default="Experience Required: ")
	compensation = models.TextField(max_length=1400, default="Compensation: ")
	additional_information = models.TextField(max_length=1400, default="Additional Information: ")

	job_applications = models.ManyToManyField(JobApplication, default=None, related_name="job_applications")
	interviewing_applications = models.ManyToManyField(JobApplication, default=None, related_name="interviewing_applications")
	successful_applications = models.ManyToManyField(JobApplication, default=None, related_name="successful_applications")







class JobSearch(models.Model):
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)
	creation_date = models.DateTimeField(default=timezone.now)
	keyword = models.CharField(max_length=200, default='')
	location = models.CharField(max_length=200, default='')
	ip = models.CharField(max_length=200, default='')

	on_site = models.BooleanField(default=False)
	remote = models.BooleanField(default=False)
	hybrid = models.BooleanField(default=False)

	free_intern = models.BooleanField(default=False)
	entry_level = models.BooleanField(default=False)
	junior = models.BooleanField(default=False)
	mid_level = models.BooleanField(default=False)
	senior = models.BooleanField(default=False)
	manager = models.BooleanField(default=False)
	executive = models.BooleanField(default=False)

	full_time = models.BooleanField(default=False)
	full_time_contract = models.BooleanField(default=False)
	part_time = models.BooleanField(default=False)
	contract_to_hire = models.BooleanField(default=False)

	company_name = models.CharField(max_length=200, default='')

	company_description = models.CharField(max_length=140, default="")
	company_values = models.CharField(max_length=140, default="")
	company_vision = models.CharField(max_length=140, default="")
	company_mission = models.CharField(max_length=140, default="")
	impact_report = models.CharField(max_length=140, default="")
	job_description = models.CharField(max_length=140, default="")
	position_summary = models.CharField(max_length=140, default="")
	qualifications = models.CharField(max_length=140, default="")
	knowledge_required = models.CharField(max_length=140, default="")
	skills_required = models.CharField(max_length=140, default="")
	experience_required = models.CharField(max_length=140, default="")
	compensation = models.CharField(max_length=140, default="")
	additional_information = models.CharField(max_length=140, default="")

	returns = models.ManyToManyField(Job, default=None)

	
	



class Dictionary(models.Model):
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None, related_name='dicauthor')
	public = models.BooleanField(default=False)
	for_sale = models.BooleanField(default=False)
	invite_only = models.BooleanField(default=False)
	invite_active = models.BooleanField(default=False)
	invite_code = models.CharField(max_length=200, default='') # Make a URL for inviting to dictionaries
	views = models.IntegerField(default=0)
	the_dictionary_itself = models.CharField(max_length=200, default='dictionary_name')
	latest_change_date = models.DateTimeField(default=timezone.now)
	creation_date = models.DateTimeField(default=timezone.now)
	traded_date = models.DateTimeField(default=timezone.now)
	purchase_orders = models.ManyToManyField(Purchase_Order, default=None, related_name='purchase_orders') # put purchaser with author when created
	allowed_to_view_authors = models.ManyToManyField(Author, default=None, related_name='dic_allowed')
	allowed_count = models.IntegerField(default=0)
	words = models.ManyToManyField(Word, default=None)
	word_count = models.IntegerField(default=0)
	wordgroups = models.ManyToManyField(Wordgroup, default=None)
	votes = models.ManyToManyField(Votes, default=None)
	votes_count = models.IntegerField(default=0)
	true_translations = models.ManyToManyField(True_Translation, default=None)
	viewcount = models.IntegerField(default=0)
	sentences = models.ManyToManyField(Sentence, default=None)
	sentence_count = models.IntegerField(default=0)
	analyses = models.ManyToManyField(Analysis, default=None)
	analysis_count = models.IntegerField(default=0)
	renditions = models.ManyToManyField(Rendition, default=None)
	rendition_count = models.IntegerField(default=0)
	revoked_authors = models.ManyToManyField(Author, default=None, related_name='dic_unallowed')
	revoked_authors_count = models.IntegerField(default=0)
	
	prerequisite_dics = models.ManyToManyField(Dictionary_Source, default=None)
	prerequisite_dics_count = models.IntegerField(default=0)
	
	entry_fee = models.IntegerField(default=0)
	continuation_fee = models.IntegerField(default=0)

	sponsors = models.ManyToManyField(Sponsor, default=None)
	sum_sponsors = models.IntegerField(default=0)
	sum_earnt_from_sponsors = models.IntegerField(default=0)
	max_sponsor_url = models.URLField(max_length=2000, blank=True, default='')
	max_sponsor_img = models.URLField(max_length=2000, blank=True, default='')
	max_sponsor_id = models.CharField(max_length=200, default='')
	max_sponsor_price = models.IntegerField(default=0)
	

	spaces = models.ManyToManyField(SpaceSource, default=None, related_name="dictionary_spaces")
	spaces_count = models.IntegerField(default=0)
	sum_earnt_from_spaces = models.IntegerField(default=0)


	invoices = models.ManyToManyField(Invoice, default=None)
	sum_invoices = models.IntegerField(default=0)


	dictionary_source = models.CharField(max_length=400, default='')

	word_loans = models.ManyToManyField(Word_Loan, default=None)
	storefronts = models.ManyToManyField(Storefront, default=None)
	dictionary_wallet = models.IntegerField(default=0)
	
	class Meta:
		unique_together = (('author', 'the_dictionary_itself'),)

	def get_allowed(self):
		for anon in Anon.objects.all():
			for dic in anon.purchased_dictionaries.all():
				if self.dictionary_name == dic.dictionary_name:
					self.allowed_to_view_authors.add(Author.objects.get(username=anon.username.username))
	# can be applied to everything with votes.
	

	def screen_votes(self, the_user):
		self.returning_vote_styles = ''
		for vote in self.votes.all():
			if vote in the_user.applied_votestyles:
				self.returning_vote_styles.append(vote)
		# must request the dictionary.returning_vote_styles.votes or the_vote_name
	def to_source(self):
		if Dictionary_Source.objects.filter(author=self.author, the_dictionary_itself=self.the_dictionary_itself):
			return Dictionary_Source.objects.get(author=self.author, the_dictionary_itself=self.the_dictionary_itself)
		else:
			Dictionary_Source.objects.create(author=self.author, the_dictionary_itself=self.the_dictionary_itself)
			return Dictionary_Source.objects.get(author=self.author, the_dictionary_itself=self.the_dictionary_itself)

	def sponsors_count(self):
		count = 0
		for word in self.words.all():
			count += word.sponsors.all().count()
		return count

	def max_sponsor(self):
		for word in self.words.all():
			word.max_sponsor()
		max_word = self.words.order_by('-max_sponsor_price').first()
		self.max_sponsor_id = max_word.max_sponsor_id
		self.max_sponsor_url = max_word.max_sponsor_url
		self.max_sponsor_img = max_word.max_sponsor_img
		self.max_sponsor_price = max_word.max_sponsor_price
		self.save()
		return max_word.max_sponsor()


	def prereq_ef_cost(self):
		pr_c_ef_cost = 0
		for dic in self.prerequisite_dics.all():
			pr_c_ef_cost += dic.entry_fee
		return pr_c_ef_cost

	def prereq_ct_cost(self):
		pr_c_ct_cost = 0
		for dic in self.prerequisite_dics.all():
			pr_c_ct_cost += dic.continuation_fee
		return pr_c_ct_cost

	def update_purchases(self):
		for purchase in self.purchase_orders.all():
			time_between = timezone.now() - purchase.last_paid
			if time_between.days > 30:
				if Anon.objects.get(username=User.objects.get(username=purchase.author.username)).false_wallet >= self.continuation_fee:
					Anon.objects.get(username=User.objects.get(username=purchase.author.username)).false_wallet -= self.continuation_fee
					Anon.objects.get(username=User.objects.get(username=self.author.username)).false_wallet += self.continuation_fee
				else:
					self.purchase_orders.remove(purchase)
					Anon.objects.get(username=User.objects.get(username=purchase.author.username)).purchased_dictionaries.remove(self)





# needs alphabetical
DICTIONARY_SORT_CHOICES = (
	(0, "freshest"),
	(1, "stalest"),
	(2, "common"),
	(3, "prized"),
	(4, "oldest"),
	(5, "newest"),
	(6, "dispersed"),
	(7, "origin"),
	(8, "words"),
	(9, "votes"),
	(10, "translations"),
	(11, "sentences"),
	(12, "renditions"),
	(13, "analyses"),
	(14, "viewcount"),
)

DICTIONARY_SORT_CHOICES_CHAR = (
	("-latest_change_date", "Most Recent Change"),
	("latest_change_date", "Least Recent Change"),
	("-views", "Most Viewed"),
	("views", "Least Viewed"),
	("-price", "Most Expensive"),
	("price", "Least Expensive"),
	("-creation_date", "Oldest"),
	("creation_date", "Newest"),
	("-traded_date", "Most Recent Trade"),
	("traded_date", "Least Recent Trade"),
	("-word_count", "Most Words"),
	("word_count", "Least Words"),
	("-votes_count", "Most Votes"),
	("votes_count", "Least Votes"),
	("-rendition_count", "Most Renditions"),
	("rendition_count", "Least Renditions"),
	("-analysis_count", "Most Analyses"),
	("analysis_count", "Least Analyses"),

)
	

#class Video(models.Model):
#	the_video_itself = VideoField(default='')

#class Playlist(models.Model):
#	videos = models.ManyToManyField(Video)
class Task(models.Model):
	the_owner = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)
	the_task_itself = models.TextField(max_length=200, default='')
	priority = models.IntegerField(default=0)

'''
class Anon(AbstractBaseUser):
	dictionaries = models.ManyToManyField(Dictionary, default=None)
	examples = models.ManyToManyField(Example, default=None) # saved comments
	tasks = models.ManyToManyField(Task, default=None)
	latest_change_date = models.DateTimeField(default=timezone.now)
	#playlists = models.ManyToManyField(Playlist)
	spaces = models.ManyToManyField(SpaceSource, default=None)
	username = models.CharField(max_length=40, unique=True)
	USERNAME_FIELD = 'username'
	objects = UserManager()
'''

#class CommentManager(models.Manager):
#	def filter_by_instance(self, instance):


class Attribution(models.Model):
	author = models.OneToOneField(Author, on_delete=models.PROTECT, default=None)
	variable = models.FloatField(default=0)
	words = models.TextField(max_length=50, default="I think this is Working") #search for sponsorship_phrase


class AngelNumber(models.Model):
	digits = models.IntegerField(default=1)
	numbers = models.IntegerField(default=0)
	description = models.TextField(max_length=1440)
	sponsors = models.ManyToManyField(Sponsor, default=None)
	sum_earnt_from_sponsors = models.IntegerField(default=0)
	sum_sponsors = models.IntegerField(default=0)
	max_sponsor_url = models.URLField(max_length=2000, blank=True, default='')
	max_sponsor_img = models.URLField(max_length=2000, blank=True, default='')
	max_sponsor_id = models.CharField(max_length=200, default='')
	max_sponsor_price = models.IntegerField(default=0)
	
	attributions = models.ManyToManyField(Attribution, default=None)


class Comment(MPTTModel):
	angel_numbers = models.ManyToManyField(AngelNumber, default=None)
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)
	dictionaries = models.ManyToManyField(Dictionary, default=None)
	sum_dictionaries = models.IntegerField(default=0)
	allowed_to_view_authors = models.ManyToManyField(Author, default=None, related_name='comment_allowed')
	words = models.ManyToManyField(Word, default=None)
	sum_dictionaries = models.IntegerField(default=0)
	body = models.TextField(max_length=1440, default='')
	sponsors = models.ManyToManyField(Sponsor, default=None)
	sum_earnt_from_sponsors = models.IntegerField(default=0)
	sum_sponsors = models.IntegerField(default=0)
	max_sponsor_url = models.URLField(max_length=2000, blank=True, default='')
	max_sponsor_img = models.URLField(max_length=2000, blank=True, default='')
	max_sponsor_id = models.CharField(max_length=200, default='')
	max_sponsor_price = models.IntegerField(default=0)
	
	top_price = models.IntegerField(default=0)
	votes = models.ManyToManyField(Votes, default=None)
	votes_count = models.IntegerField(default=0)
	viewcount = models.IntegerField(default=0)
	latest_change_date = models.DateTimeField(default=timezone.now)
	has_commented = models.ManyToManyField(Author, default=None, related_name='comments_has_commented')
	sum_has_commented = models.IntegerField(default=0)
	has_viewed = models.ManyToManyField(Author, default=author, related_name='comments_has_viewed')
	sum_has_viewed = models.IntegerField(default=0)
	has_voted = models.ManyToManyField(Author, default=None, related_name='comment_has_voted')
	sum_has_voted = models.IntegerField(default=0)
	parent = TreeForeignKey('self', on_delete=models.CASCADE, default=None, null=True, blank=True, related_name='children', db_index=True)
	children_count = models.IntegerField(default=0)

	max_sponsor_url = models.URLField(max_length=2000, blank=True, default='')
	max_sponsor_img = models.URLField(max_length=2000, blank=True, default='')
	max_sponsor_id = models.CharField(max_length=200, default='')
	max_sponsor_price = models.IntegerField(default=0)


	def __str__(self):
		return self.body

	def __unicode__(self):
   		return unicode(self.body) or u''

	def children(self):
		return Comments.objects.filter(parent=self)

	@property
	def is_parent(self):
		if self.parent is not None:
			return False
		return True

	class MPTTMeta:
		order_insertion_by = ['votes_count', 'children_count']

	

	def max_sponsor(self):
		for dic in self.dictionaries.all():
			max_sponsor = dic.max_sponsor()
		if not max_sponsor:
			max_sponsor = self.sponsors.order_by('-price_limit').first()
		if not max_sponsor:
			max_sponsor = Sponsor.objects.all().order_by('-price_limit').first()
		self.max_sponsor_id = max_sponsor.id
		self.max_sponsor_img = max_sponsor.img
		self.max_sponsor_url = max_sponsor.url2
		self.max_sponsor_price = max_sponsor.price_limit
		return max_sponsor

COMMENT_SORT_CHOICES = (
	(0, "dictionaries"),
	(1, "-dictionaries"),
	(2, "words"),
	(3, "-words"),
	(4, "sponsors"),
	(5, "-sponsors"),
	(6, "uniques"),
	(7, "-uniques"),
	(8, "viewcount"),
	(9, "unseen"),
	(10, "latest"),
	(11, "definition"),
	(12, "discussed"),
	(13, "final"),
	(14, "voters"),
)

COMMENT_SORT_CHOICES_CHAR = (
	("sum_dictionaries", "Generalist"),
	("-sum_dictionaries", "Broadness"),
	("sum_words", "Less Complex"),
	("-sum_words", "More Intelligent"),
	("sum_sponsors", "Encouraged"),
	("-sum_sponsors", "Discouraged"),
	("votes_uniques", "Less Uniques"),
	("-votes_uniques", "More Uniques"),
	("-viewcount", "Viewcount"),
	("viewcount", "Unseen"),
	("-latest_change_date", "Latest"),
	("latest_change_date", "Unchanged"),
	("-sum_has_commented", "Discussed"),
	("sum_has_commented", "Unspoken"),
)

class PostSource(models.Model):
	post_id = models.CharField(max_length=256, default='')

	def to_full():
		return Post.objects.get(id=int(post_id))
	
class Edit(models.Model):
	body = models.TextField(max_length=144000, default='')
	author = models.ForeignKey(Author, on_delete=models.PROTECT, default=None)
	latest_change_date = models.DateTimeField(default=timezone.now)
	post_source = models.ForeignKey(PostSource, on_delete=models.PROTECT, default=None)





class CommentLocations(models.Model):
	comments = models.ManyToManyField(Comment, default=None)

	from_top = models.IntegerField(default=0)
	from_left = models.IntegerField(default=0)



class SearchURL(models.Model):
	name = models.CharField(max_length=400, default='')
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None, null=True)
	url = models.URLField(max_length=2000)
	comment_locations = models.ManyToManyField(CommentLocations, default=None)
	comment_height = models.IntegerField(default=0)
	comment_width = models.IntegerField(default=0)
	sum_comments = models.IntegerField(default=0)
	sponsors = models.ManyToManyField(Sponsor, default=None)
	sum_sponsors = models.IntegerField(default=0)
	sum_earnt_from_sponsors = models.IntegerField(default=0)
	max_sponsor_url = models.URLField(max_length=2000, blank=True, default='')
	max_sponsor_img = models.URLField(max_length=2000, blank=True, default='')
	max_sponsor_id = models.CharField(max_length=200, default='')
	max_sponsor_price = models.IntegerField(default=0)
	
	viewcount = models.IntegerField(default=0)
	change_count = models.IntegerField(default=0)
	latest_change_date = models.DateTimeField(default=timezone.now)
	pub_date = models.DateTimeField(default=timezone.now)
	public = models.BooleanField(default=1)
	allowed_to_view_authors = models.ManyToManyField(Author, default=None, related_name='search_allowed')
	votes = models.ManyToManyField(Votes, default=None)
	votes_count = models.IntegerField(default=0)
	has_voted = models.ManyToManyField(Author, related_name="search_has_voted", default=None)
	views = models.IntegerField(default=0)
	post_allowed = models.ManyToManyField(Author, default=None, related_name='search_allowed_authors')
	cc = models.CharField(max_length=400, default='')
	img = models.URLField(max_length=2000, blank=True, default='')
	stripe_price_id = models.CharField(max_length=100, default='')
	stripe_product_id = models.CharField(max_length=100, default='')
	price = models.IntegerField(default=0)  # cents

	monthly = models.BooleanField(default=False)


    
class Barcode(models.Model):
	barcode_value = models.IntegerField(default=0)
	barcode_meaning = models.TextField(default='', max_length=144)
	barcode_definition = models.TextField(default='', max_length=1440)
	barcode_story = models.TextField(default='', max_length=14400)
	has_commented = models.ManyToManyField(Author, default=None, related_name='barcode_has_commented')
	sum_has_commented = models.IntegerField(default=0)
	has_viewed = models.ManyToManyField(Author, default=None, related_name='barcode_has_viewed')
	sum_has_viewed = models.IntegerField(default=0)
	has_voted = models.ManyToManyField(Author, default=None, related_name='barcode_has_voted')
	sum_has_voted = models.IntegerField(default=0)
	votes_uniques = models.IntegerField(default=0)
	comments = models.ManyToManyField(Comment, default=None)
	sum_comments = models.IntegerField(default=0)
	sponsors = models.ManyToManyField(Sponsor, default=None)
	sum_sponsors = models.IntegerField(default=0)
	sum_earnt_from_sponsors = models.IntegerField(default=0)
	max_sponsor_url = models.URLField(max_length=2000, blank=True, default='')
	max_sponsor_img = models.URLField(max_length=2000, blank=True, default='')
	max_sponsor_id = models.CharField(max_length=200, default='')
	max_sponsor_price = models.IntegerField(default=0)
	
	viewcount = models.IntegerField(default=0)
	change_count = models.IntegerField(default=0)
	latest_change_date = models.DateTimeField(default=timezone.now)
	
	
	
	

class Post(models.Model):
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None, null=True)
	angel_numbers = models.ManyToManyField(AngelNumber, default=None)
	barcodes = models.ManyToManyField(Barcode, default=None)
	edits = models.ManyToManyField(Edit, default=None)
	products = models.ManyToManyField(Price, default=None)
	title = models.CharField(max_length=200, default='')
	url2 = models.URLField(max_length=2000, blank=True, default='')
	img = models.URLField(max_length=2000, blank=True, default='')
	has_commented = models.ManyToManyField(Author, default=None, related_name='post_has_commented')
	sum_has_commented = models.IntegerField(default=0)
	has_viewed = models.ManyToManyField(Author, default=None, related_name='post_has_viewed')
	sum_has_viewed = models.IntegerField(default=0)
	has_voted = models.ManyToManyField(Author, default=None, related_name='post_has_voted')
	sum_has_voted = models.IntegerField(default=0)
	votes_uniques = models.IntegerField(default=0)
	under_talked = models.FloatField(default=0)
	dictionaries = models.ManyToManyField(Dictionary, default=None)
	sum_dictionaries = models.IntegerField(default=0)
	words = models.ManyToManyField(Word, default=None)
	sum_words = models.IntegerField(default=0)
	body = models.TextField(max_length=1440, default='')
	comments = models.ManyToManyField(Comment, default=None)
	sum_comments = models.IntegerField(default=0)
	sponsors = models.ManyToManyField(Sponsor, default=None)
	max_sponsor_url = models.URLField(max_length=2000, blank=True, default='')
	max_sponsor_img = models.URLField(max_length=2000, blank=True, default='')
	max_sponsor_id = models.CharField(max_length=200, default='')
	max_sponsor_price = models.IntegerField(default=0)
	sum_sponsors = models.IntegerField(default=0)
	sum_earnt_from_sponsors = models.IntegerField(default=0)
	
	viewcount = models.IntegerField(default=0)
	change_count = models.IntegerField(default=0)
	latest_change_date = models.DateTimeField(default=timezone.now)
	pub_date = models.DateTimeField(default=timezone.now)
	public = models.BooleanField(default=1)
	spaces = models.ManyToManyField(SpaceSource, default=None)
	sum_spaces = models.IntegerField(default=0)
	allowed_to_view_authors = models.ManyToManyField(Author, default=None, related_name='post_allowed')
	votes = models.ManyToManyField(Votes, default=None)
	votes_count = models.IntegerField(default=0)
	post_allowed = models.ManyToManyField(Author, default=None, related_name='post_allowed_authors')
	post_source = models.CharField(max_length=400, default='')
	cc = models.CharField(max_length=400, default='')
	search_urls = models.ManyToManyField(SearchURL, default=None)

	shuffle = models.IntegerField(default=0)
	attention = models.IntegerField(default=99999999)
	sales = models.ManyToManyField(Sale, default=None)

	def __str__(self):
		return self.title

	def __eq__(self, other):
		return self.id == other.id

	def __hash__(self):
		return hash(('id', self.id))
	
	def __unicode__(self):
   		return unicode(self.title) or u''


	def screen_votes(self, the_user):
		for vote in self.votes.all():
			if vote in the_user.applied_votestyles:
				self.returning_vote_styles.append(vote)


	def attention_save(self, loggedinanon):
		densities = loggedinanon.home_page_density.order_by('?')[0:25]
		for density in densities:
			denseness = []
			for densitivity in density.density.all():
				densensess.append(densitivity.dense)
			posts = []
			for post_id in density.post_ids.all():
				posts.append(Post.objects.get(id=post_id.the_posts_id))

	
	def shuffle_save(self, loggedinanon, count):
		posts = Post.objects.order_by('?')[count: count+25]
		i = 0
		for post in posts:
			post.shuffle = i
			post.save()
			i+=1

	def max_sponsor(self):
		max_sponsor = self.sponsors.all().order_by('-price_limit').first()
		if not max_sponsor:
			max_sponsor = Sponsor.objects.all().order_by('-price_limit').first()
		self.max_sponsor_id = max_sponsor.id
		self.max_sponsor_img = max_sponsor.img
		self.max_sponsor_url = max_sponsor.url2
		self.max_sponsor_price = max_sponsor.price_limit
		return max_sponsor

	def max_url(self):
		max_sponsor = self.sponsors.all().order_by('-price_limit').first()
		if not max_sponsor:
			return Sponsor.objects.all().order_by('-price_limit').first().url2
		url = max_sponsor.url2
		return url

	def max_img(self):
		max_sponsor = self.sponsors.all().order_by('-price_limit').first()
		if not max_sponsor:
			return Sponsor.objects.all().order_by('-price_limit').first().img
		img = max_sponsor.img
		return img

	def max_id(self):
		max_sponsor = self.sponsors.all().order_by('-price_limit').first()
		if not max_sponsor:
			max_sponsor = Sponsor.objects.all().order_by('-price_limit').first()
		__id = max_sponsor.id
		return __id

	def max_img_id(self):
		max_sponsor = self.sponsors.all().order_by('-price_limit').first()
		if not max_sponsor:
			max_sponsor = Sponsor.objects.all().order_by('-price_limit').first()
		__id = max_sponsor.id
		return max_sponsor.img, __id


	def max(self):
		max_sponsor = self.sponsors.order_by('-price_limit').first()
		if not max_sponsor:
			return Sponsor.objects.all().order_by('-price_limit').first()
		return max_sponsor

	def first_sorted_comment(self, anon):
		# takes each comment and the anon's sort preference to auto select 1 comment for duo-displays.
		return 0

	def preview(self):
		if len(self.url):
			# title, description, image = web_preview(self.url, timeout=5)
			title, description, image = None, None, None
		else:
			image = None
		return image

	def name_sort_dics(self):
		
		return self.dictionaries.all().order_by("the_dictionary_itself")

	def date_sort_dics(self):
		
		return self.dictionaries.all().order_by("creation_date")

	def count_sort_votes(self):
		return self.votes.all().order_by("votes")


POST_SORT_CHOICES = (
	(0, "viral"),
	(1, "early"),
	(2, "freshest"),
	(3, "eldest"),
	#(4, "uniques"),
	#(5, "voters"),
	#(6, "broadness"),
	#(7, "intricacy"),
	#(8, "talkative"),
	#(9, "homes"),
	#(10, "encouraged"),
	(11, "votes"),
	(12, "unvoted"),
	
)

POST_SORT_CHOICES_CHAR = (
	("-viewcount", "Viral"),
	("viewcount", "Early"),
	("-latest_change_date", "Freshest"),
	("latest_change_date", "Eldest"),
	("-sum_has_viewed", "Uniques"),
	("-sum_has_voted", "Voters"),
	("-sum_dictionaries", "Broadness"),
	("-sum_words", "Intricacy"),
	("-sum_comments", "Talkative"),
	("sum_comments", "Silencio"),
	("-under_talked", "Under Commented"),
	("under_talked", "Over Commented"),
	("-sum_spaces", "Homes"),
	("-sum_sponsors", "Encouraged"),
	("-votes_count", "Votes"),
	("votes_count", "Unvoted"),
	("-shuffle", "Shuffle"),
	("shuffle", "Counter-Shuffle"),
	("-attention", "Attention Span Up"),
	("attention", "Scroll Past"),

)

class Dictionary_Loan(models.Model):
	amount_total = models.IntegerField(default=0)
	amount_owing = models.IntegerField(default=0)
	repayment_term = models.DateTimeField(default=timezone.now)
	pro_rata = models.FloatField(default=0.08)
	repayment_rates = models.CharField(default="Hourly", choices=REPAYMENT_RATES, max_length=144)
	total_repayments_remaining = models.IntegerField(default=1)
	total_repayments = models.IntegerField(default=1)
	dictionaries = models.ManyToManyField(Dictionary, default=None)

class ConditionEdit(models.Model):
	conditions = models.TextField(max_length=1666000, default="Pay Attention 3000 Pounds of Flesh")
	votes = models.ManyToManyField(Author, default=None)


class ConditionalVote(models.Model):
	votee = models.OneToOneField(Author, default=None, on_delete=models.PROTECT, related_name='conditional_votee')
	votes = models.ManyToManyField(Author, default=None, related_name='conditional_votes')

class Terms(models.Model):
	chapter = models.CharField(max_length=160, default='')
	conditionees_select_primate = models.BooleanField(default=False)
	conditioners_select_external = models.BooleanField(default=False)
	conditionees = models.ManyToManyField(Author, default=None, related_name="conditionees") # must stake primation fee to accept, under certain conditions, votes on edits to chapters, chosen by precessive council members
	conditionee_votes = models.ManyToManyField(ConditionalVote, default=None, related_name="conditionee_votes")
	conditioners = models.ManyToManyField(Author, default=None, related_name="conditioners") # votes on edits to conditions, includes precessive council members
	conditioner_votes = models.ManyToManyField(ConditionalVote, default=None, related_name="conditioner_votes")
	conditions = models.TextField(max_length=1666000, default="Pay Attention 3000 Pounds of Flesh") # changed by conditioners, judged by primation reference, written by precessive council members
	condition_edits = models.ManyToManyField(ConditionEdit, default=None) # changed by conditioners, judged by primation reference, written by precessive council members
	accostings = models.TextField(max_length=6660000, default="You've been accounted for as for the following") # written by terms council members
	primation_fee = models.IntegerField(default=1000) # price up for grabs if you violate certain conditions as punishment (how much you have to keep in your account to pay if you lose your job)
	
	delete = models.BooleanField(default=False)
	primation_reference = models.ManyToManyField(Author, default=None, related_name="reference") # who judges the paying of the primation fee, who you have to impress to keep your balance / job. # I'll put 10k on the line to prove to you that I can sell his product. Etc.

class Chapters(models.Model):
	title = models.CharField(max_length=220, default="Chapter X")
	verses = models.TextField(max_length=14400, default="In the beginning")
	side_notes = models.TextField(max_length=144000, default="About this text") # by legislative
	external_commentary = models.TextField(max_length=144000, default="You've heard about this text") # by administrative
	execution_prose = models.TextField(max_length=144000, default="You hear this text better when we say") # by executive
	judiciary_feedback = models.TextField(max_length=144000, default="You said this last time") # by executive


MEMBER_VOTE_TYPE_CHAR = (
	("legislative", "Legislative"),
	("administrative", "Administrative"),
	("executive", "Executive"),
	("judiciary", "Judiciary"),
)

class MemberVotes(models.Model):
	voter = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="voter")
	space = models.ForeignKey(SpaceSource, on_delete=models.CASCADE)
	vote_type = models.CharField(max_length=144, choices=MEMBER_VOTE_TYPE_CHAR, default="legislative")
	vote_member = models.OneToOneField(Author, on_delete=models.PROTECT, default=None, related_name="vote_member")

class TaxIncentive(models.Model):
	words = models.ManyToManyField(Word, default=None)
	tax = models.IntegerField(default=0)
	bounty = models.IntegerField(default=0)
	voters = models.ManyToManyField(Author, default=None, related_name="voters")
	initiators = models.ManyToManyField(Author, default=None, related_name="initiators")
	passers = models.ManyToManyField(Author, default=None, related_name="passers") # passes pass whether the bounty is due
	bounty_description = models.TextField(max_length=14400, default="")



class ServerUser(models.Model):
	username = models.CharField(max_length=140, default='')
	player_id = models.CharField(max_length=140, default="0")

class ServerHistory(models.Model):
	server_name = models.CharField(max_length=140, default='')
	server_log_in_date = models.DateTimeField(default=timezone.now)
	server_users = models.ManyToManyField(ServerUser, default=None)

class Player(models.Model):
	player_name = models.CharField(max_length=140, default='')
	last_logged_in = models.DateTimeField(default=timezone.now)
	server_history = models.ManyToManyField(ServerHistory, default=None)


class PlayerCount(models.Model):
	count = models.IntegerField(default=0)
	max_size_of_server = models.IntegerField(default=12)
	players = models.ManyToManyField(Player, default=None)
	current_log_date = models.DateTimeField(default=timezone.now)


class GameMode(models.Model):
	game_mode_name = models.CharField(default='', max_length=140)

class MinecraftServer(models.Model):
	version = models.FloatField(default=0)
	domain = models.TextField(max_length=140, default='')
	port = models.IntegerField(default=1234)
	player_count = models.ManyToManyField(PlayerCount, default=None)
	online = models.BooleanField(default=False)
	location = models.CharField(max_length=140, default='')
	tags = models.ManyToManyField(Word, default=None)
	registered_by = models.CharField(max_length=140, default='')
	registered_since = models.DateTimeField(default=timezone.now)
	last_update = models.DateTimeField(default=timezone.now)
	theme = models.ManyToManyField(SpaceSource, default=None)
	about = models.TextField(default='', max_length=4000)
	website = models.URLField(default='', max_length=400)
	game_models = models.ManyToManyField(GameMode, default=None)
	sponsor = models.ManyToManyField(Sponsor, default=None)




class Space(models.Model):
	tax_incentives = models.ManyToManyField(TaxIncentive, default=None)
	the_space_itself = models.ForeignKey(Word, on_delete=models.CASCADE, default=00000) # check pre-requisite dictionary acquired
	angel_numbers = models.ManyToManyField(AngelNumber, default=None)
	latest_change_date = models.DateTimeField(default=timezone.now)
	sidebar = models.TextField(max_length=1000, default='')
	values = models.TextField(max_length=1000, default='Values')
	vision = models.TextField(max_length=1000, default='Vision')
	mission = models.TextField(max_length=1000, default='Mission')
	minecraft_servers = models.ManyToManyField(MinecraftServer, default=None)

	author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='author', default=None)
	viewcount = models.IntegerField(default=0)
	posts_viewcount = models.IntegerField(default=0)
	posts = models.ManyToManyField(Post, default=None)
	postcount = models.IntegerField(default=0)
	votes = models.ManyToManyField(Votes, default=None)
	votes_count = models.IntegerField(default=0)
	sponsors = models.ManyToManyField(Sponsor, default=None)
	sum_sponsors = models.IntegerField(default=0)
	sum_earnt_from_sponsors = models.IntegerField(default=0)
	max_sponsor_url = models.URLField(max_length=2000, blank=True, default='')
	max_sponsor_img = models.URLField(max_length=2000, blank=True, default='')
	max_sponsor_id = models.CharField(max_length=200, default='')
	max_sponsor_price = models.IntegerField(default=0)
	
	
	approved_voters = models.ManyToManyField(Author, related_name='approved_voters', default=None)
	approved_voter_count = models.IntegerField(default=0)
	public = models.BooleanField(default=False)
	for_sale = models.BooleanField(default=False)
	free_sponsorships = models.BooleanField(default=False)
	anyone_can_edit = models.BooleanField(default=False)
	elected_sponsorships = models.BooleanField(default=False)

	entry_fee = models.IntegerField(default=1)
	continuation_fee = models.IntegerField(default=1)

	space_wallet = models.IntegerField(default=0)

	invite_only = models.BooleanField(default=False)
	invite_active = models.BooleanField(default=False)
	invite_code = models.CharField(max_length=200, default='')

	dictionary_loans = models.ManyToManyField(Dictionary_Loan, default=None)

	elected_legislative = models.BooleanField(default=False) # writes the rule book for the space
	elected_administrative = models.BooleanField(default=False) # decides how to interpret the rules for a given breach
	elected_executive = models.BooleanField(default=False) # apprehends publicly
	elected_judiciary = models.BooleanField(default=False) # designates appropriate punishment

	successive = models.BooleanField(default=False) # each higher level of government can kick the lower levels
	progressive = models.BooleanField(default=False) # each lower level of government can vote to elevate to higher levels

	legislative_members = models.ManyToManyField(Author, default=None, related_name="legislative_members")
	legislative_level = models.IntegerField(default=0) # designates how many members there are to be max.
	legislative_votes = models.ManyToManyField(MemberVotes, default=None, related_name="legislative_votes") #who's been voted to be included in this group
	legislative_blind = models.BooleanField(default=False)
	legislative_conditionees_select_primate = models.BooleanField(default=False)
	legislative_conditioners_select_external = models.BooleanField(default=False)
	administrative_members = models.ManyToManyField(Author, default=None, related_name="administrative_members")
	administrative_level = models.IntegerField(default=0)
	administrative_votes = models.ManyToManyField(MemberVotes, default=None, related_name="administrative_votes")
	administrative_blind = models.BooleanField(default=False)
	administrative_conditionees_select_primate = models.BooleanField(default=False)
	administrative_conditioners_select_external = models.BooleanField(default=False)
	executive_members = models.ManyToManyField(Author, default=None, related_name="executive_members")
	executive_level = models.IntegerField(default=0)
	executive_votes = models.ManyToManyField(MemberVotes, default=None, related_name="executive_votes")
	executive_blind = models.BooleanField(default=False)
	executive_conditionees_select_primate = models.BooleanField(default=False)
	executive_conditioners_select_external = models.BooleanField(default=False)
	judiciary_members = models.ManyToManyField(Author, default=None, related_name="judiciary_members")
	judiciary_level = models.IntegerField(default=0)
	judiciary_votes = models.ManyToManyField(MemberVotes, default=None, related_name="judiciary_votes")
	judiciary_blind = models.BooleanField(default=False)
	judiciary_conditionees_select_primate = models.BooleanField(default=False)
	judiciary_conditioners_select_external = models.BooleanField(default=False)
	
	legislation = models.ManyToManyField(Chapters, default=None, related_name="legislation")
	legislating_terms = models.ManyToManyField(Terms, default=None, related_name="legislating")
	administration = models.ManyToManyField(Chapters, default=None, related_name="administration")
	administrating_terms = models.ManyToManyField(Terms, default=None, related_name="administrating")
	execution = models.ManyToManyField(Chapters, default=None, related_name="execution")
	executing_terms = models.ManyToManyField(Terms, default=None, related_name="executing")
	adjudication = models.ManyToManyField(Chapters, default=None, related_name="adjudication")
	adjudicating_terms = models.ManyToManyField(Terms, default=None, related_name="adjudicating")

	storefronts = models.ManyToManyField(Storefront, default=None)
	

	class Meta:
		unique_together = (('author', 'the_space_itself'),)

	def __str__(self):
		return self.the_space_itself.the_word_itself

	def get_absolute_url(self):
		return reverse("Bable:space", kwargs={"id": self.id})

	def __unicode__(self):
		return unicode(self.the_space_itself) or u''

	@property
	def count_posts(self):
		return self.posts.all().count()

	@property
	def count_votes(self):
		return self.votes.all().count()

	@property
	def count_sponsors(self):
		return self.sponsors.all().count()

	@property
	def count_approved_voters(self):
		return self.approved_voters.all().count()

	def to_source(self):
		return SpaceSource.objects.all().filter(author=self.author, the_space_itself=self.the_space_itself.to_source()).first()

	def max_sponsor(self):
		max_price = 0
		pks = Sponsor.objects.values_list('pk', flat=True)
		if not pks:
			Sponsor.objects.get(id=1).delete()
			new_spon = Sponsor.objects.create(img="https://www.predictionary.us/B/static/bullseye_3.jpeg", url2="https://www.predictionary.us", author=Author.object.get(username='test'))
			pks = [new_spon.id]
		random_pk = choice(pks)
		random_obj = Sponsor.objects.get(pk=random_pk)
		max_sponsor = random_obj
		for sponsor in self.sponsors.all().filter(payperview=False):
			if sponsor.allowable_expenditure >= sponsor.price_limit:
				if sponsor.price_limit >= max_price:
					max_price = sponsor.price_limit
					max_sponsor = sponsor
		return max_sponsor

SPACE_SORT_CHOICES = (
	(0, "viral"),
	(1, "early"),
	(2, "freshest"),
	(3, "eldest"),
	(4, "starter"),
	(5, "useful"),
	(6, "encourage"),
	(7, "synched"),
)

SPACE_SORT_CHOICES_CHAR = (
	("-viewcount", "Most Viewed"),
	("viewcount", "Least Viewed"),
	("-latest_change_date", "Recent Change"),
	("latest_change_date", "Distant Change"),
	("-posts_viewcount", "Most Post Views"),
	("posts_viewcount", "Least Post Views"),
	("-votes_count", "Most Votes"),
	("votes_count", "Least Votes"),
	("-sponsor_count", "Most Sponsored"),
	("sponsor_count", "Least Sponsored"),
	("-approved_voter_count", "Most Approved Voters"),
	("approved_voter_count", "Least Approved Voters"),
)

ANON_SORT_CHOICES = (
	(0, "dictionaries"),
	(1, "saved_dictionaries"),
	(2, "examples"),
	(3, "tasks"),
	(4, "latest"),
	(5, "posted_comments"),
	(6, "saved_comments"),
	(7, "posts"),
	(8, "spaces"),
	(9, "saved_spaces"),
)


import gpg_lite as gpg
import os
if os.name =="nt":
	class Message(models.Model):
		sender = models.OneToOneField(Author, on_delete=models.CASCADE, related_name='author_sender')
		receiver = models.OneToOneField(Author, on_delete=models.CASCADE, related_name='author_receiver')
		encrypted_message = models.TextField(max_length=10000, default='')
		key_fingerprint = models.CharField(max_length=1000, default='')

		

		def encrypt_message(message):
			self.encrypted_message = message
			return message

		def decrypt_message():
			return self.encrypted_message
			
else:
	gpg_store = gpg.GPGStore()
	class Message(models.Model):
		sender = models.OneToOneField(Author, on_delete=models.CASCADE, related_name='author_sender')
		receiver = models.OneToOneField(Author, on_delete=models.CASCADE, related_name='author_receiver')
		encrypted_message = models.TextField(max_length=10000, default='')
		key_fingerprint = models.CharField(max_length=1000, default='')

		def set_fingerprint():
			self.key_fingerprint = str(gpg_store.gen_key(key_type='RSA', key_length=4096, full_name=self.sender.username, email=self.sender.to_anon().email, passphrase=self.sender.to_anon().password))

		def encrypt_message(message):
			encrypted_file = '/gpg/'+self.key_fingerprint
			with open(encrypted_file, "w") as f:
				gpg_store.encrypt(
					source=message,
					recipients=[self.receiver.to_anon().email],
					output=f,
					sign=self.sender.to_anon().email,
					passphrase=self.sender.to_anon().password)
			with open(encrypted_file, "rb") as f:
				message = f.read()
				self.encrypted_message = message
				return self.encrypted_message

		def decrypt_message():
			encrypted_file = '/gpg/'+self.key_fingerprint
			decrypted_file = '/gpg/'+self.receiver.username
			with open(encrypted_file, "rb") as f, open(decrypted_file, "w") as f_out:
				gpg_store.decrypt(
					source=f,
					output=f_out,
					passphrase=self.receiver.to_anon().password)
				return f_out.read()


ANON_SORT_CHOICES_CHAR = (
	("-sum_dictionaries", "Most Dictionaries"),
	("sum_dictionaries", "Least Dictionaries"),
	("-sum_purchased_dictionaries", "Most Purchased Dictionaries"),
	("sum_purchased_dictionaries", "Least Purchased Dictionaries"),
	("-sum_excluded_authors", "Most Authors Blocked"),
	("sum_excluded_authors", "Least Authors Blocked"),
	("-sum_examples", "Most Examples"),
	("sum_examlpes", "Least Examples"),
	("-sum_tasks", "Most Tasks"),
	("sum_tasks", "Least Tasks"),
	("-sum_posts", "Most Posts"),
	("sum_posts", "Least Posts"),
	("-sum_posted_comments", "Most Posted Comments"),
	("sum_posted_comments", "Least Posted Comments"),
	("-sum_saved_comments", "Most Saved Comments"),
	("sum_saved_comments", "Least Saved Comments"),
	("-sum_purchased_spaces", "Most Purchased Spaces"),
	("sum_purchased_spaces", "Least Purchased Spaces"),
	("-sum_created_votestyles", "Most Created Votestyles"),
	("sum_created_votestyles", "Least Created Votestyles"),
	("-latest_change_date", "Most Recent Update"),
	("latest_change_date", "Least Recent Update"),
	("-creation_date", "Newest Account Creation"),
	("creation_date", "Oldest Account Creation"),
)
class Densitivity(models.Model):
	dense = models.IntegerField(default=0)

class Post_id(models.Model):
	the_posts_id = models.IntegerField(default=0)


class Page_Density(models.Model):
	ip = models.CharField(max_length=15, default="")
	time_spent = models.IntegerField(default=0)
	density = models.ManyToManyField(Densitivity, default=None)
	post_ids = models.ManyToManyField(Post_id, default=None)
	scroll_height = models.IntegerField(default=0)
	scroll_type = models.CharField(choices=POST_SORT_CHOICES_CHAR, default="latest_change_date", max_length=180)
	client_height = models.IntegerField(default=0)
	duration = models.IntegerField(default=2)


class Loan(models.Model):
	amount_total = models.IntegerField(default=0)
	amount_owing = models.IntegerField(default=0)
	repayment_term = models.DateTimeField(default=timezone.now)
	pro_rata = models.FloatField(default=0.08)
	repayment_rates = models.CharField(default="hourly", choices=REPAYMENT_RATES, max_length=144)
	total_repayments_remaining = models.IntegerField(default=1)
	total_repayments = models.IntegerField(default=1)

	spaces = models.ManyToManyField(Space, default=None)



class RQAnswers(models.Model):
	answer = models.TextField(max_length=140)


class RequestQuestion(models.Model):
	question = models.TextField(max_length=140)
	answers = models.ManyToManyField(RQAnswers, default=None)



class Availability(models.Model):
	concerning = models.TextField(max_length=140, default="All")
	location = models.TextField(max_length=140, default="Zoom/Meets/Messenger/WhatsApp/Instagram/Discord")
	request_questions = models.ManyToManyField(RequestQuestion, default=None, related_name="request_questions")
	post_request_questions = models.ManyToManyField(RequestQuestion, default=None, related_name="post_request_questions")
	words = models.ManyToManyField(Word, default=None) # for styling the block on the calendar
	start_time = models.DateTimeField(timezone.now)
	end_time = models.DateTimeField(timezone.now)
	available = models.BooleanField(default=False) #mark either when you're availabilities are, or your unavailabilities are. "I can do any time from X" vs "I can't do these times"




class MoveTo(models.Model):
	x = models.IntegerField(default=0)
	y = models.IntegerField(default=0)
	#context.moveTo(x, y)

class LineTo(models.Model):
	x = models.IntegerField(default=0)
	y = models.IntegerField(default=0)
	#context.lineTo(x, y)

class QuadraticCurveTo(models.Model):
	x = models.IntegerField(default=0)
	y = models.IntegerField(default=0)
	p1 = models.IntegerField(default=0)
	p2 = models.IntegerField(default=0)
	#context.quadraticCurveTo(x, y, p1, p2)
#circle
class ArcTo(models.Model):
	x = models.IntegerField(default=0)
	y = models.IntegerField(default=0)
	radius = models.IntegerField(default=0)
	start_angle = models.IntegerField(default=0) #0
	end_angle = models.IntegerField(default=0) # Math.PI
	counter_clockwise = models.BooleanField(default=False) # false
	# context.arc(x, y, radius, start_angle, end_angle, counter_clockwise)

class BezierCurveTo(models.Model):
	x1 = models.IntegerField(default=0)
	y1 = models.IntegerField(default=0)
	x2 = models.IntegerField(default=0)
	y2 = models.IntegerField(default=0)
	x3 = models.IntegerField(default=0)
	y3 = models.IntegerField(default=0)
	#context.bezierCurveTo(x1, y1, x2, y2, x3, y3)



class Movement(models.Model):
	move_to = models.OneToOneField(MoveTo, default=None, on_delete=models.CASCADE)
	line_to = models.OneToOneField(LineTo, default=None, on_delete=models.CASCADE)
	quadratic_curve_to = models.OneToOneField(QuadraticCurveTo, default=None, on_delete=models.CASCADE)
	arc_to = models.OneToOneField(ArcTo, default=None, on_delete=models.CASCADE)
	line_width = models.FloatField(default=5.0)
	stroke_style = models.TextField(max_length=2000, default="black")
	stroke = models.BooleanField(default=False)
	fill_style = models.TextField(max_length=2000, default="black")
	fill = models.BooleanField(default=False)
	order = models.IntegerField(default=0)

class Path(models.Model):
	movements = models.ManyToManyField(Movement, default=None)

class Triangle(models.Model):
	a = models.IntegerField(default=0)
	b = models.IntegerField(default=0)
	c = models.IntegerField(default=0)
	x = models.IntegerField(default=0)
	y = models.IntegerField(default=0)
	theta = models.FloatField(default=0)
	fill_style = models.CharField(default='blue', max_length=14)

#var ctx = canvas.getContext('2d');
#ctx.beginPath();
#ctx.moveTo(50, 100);
#ctx.lineTo(100, 50);
#ctx.lineTo(150, 100);
#ctx.lineTo(50, 100);
#ctx.fillStyle = "blue";
#ctx.fill()


class Star(models.Model):
	x = models.IntegerField(default=0)
	y = models.IntegerField(default=0)
	r = models.IntegerField(default=0)
	n = models.IntegerField(default=5)


	'''function star(R, X, Y, N) {
            ctx.beginPath();
            ctx.moveTo(X + R, Y);
            for (var i = 1; i <= N * 2; i++) {
               if (i % 2 == 0) {
                  var theta = i * (Math.PI * 2) / (N * 2);
                  var x = X + (R * Math.cos(theta));
                  var y = Y + (R * Math.sin(theta));
               } else {
                  var theta = i * (Math.PI * 2) / (N * 2);
                  var x = X + ((R / 2) * Math.cos(theta));
                  var y = Y + ((R / 2) * Math.sin(theta));
               }
               ctx.lineTo(x, y);
            }
            ctx.closePath();
            ctx.fillStyle = "yellow";
            ctx.fill();
            ctx.fillStyle = "green";
            ctx.stroke();
         }
'''


class Rectangle(models.Model):
	x = models.IntegerField(default=0)
	y = models.IntegerField(default=0)
	width = models.IntegerField(default=0)
	height = models.IntegerField(default=0)
	paste = models.TextField(max_length=150, default="var x = 150;var y = 50;var width = 200;var height = 250;context.strokeRect(x, y, width, height);")
	filled = models.BooleanField(default=False)#canvas.fillRect(150, 50, 200, 250);
	clear = models.BooleanField(default=False)#canvas.clearRect(150, 50, 200, 250);

class Drawing(models.Model):
	name = models.CharField(max_length=140, default="Builder Owners Project")
	author = models.OneToOneField(Author, default=None, on_delete=models.PROTECT)
	created_date = models.DateTimeField(timezone.now)
	latest_change_date = models.DateTimeField(timezone.now)
	rectangles = models.ManyToManyField(Rectangle, default=None)
	init = models.TextField(max_length=20000, default="<script>function rectangle() {var canvas = document.getElementById('canvas');var context = canvas.getContext('2d');}</script>")


class Affinity(models.Model):
	host_author = models.OneToOneField(Author, default=None, on_delete=models.PROTECT, related_name="affinity_host_author")
	mutual = models.OneToOneField(Author, default=None, on_delete=models.PROTECT, related_name="affinity_mutual")
	mutual_friend = models.OneToOneField(Author, default=None, on_delete=models.PROTECT, related_name="affinity_mutual_friend")
	relationship_factor = models.FloatField(default=0.0) # whether they'll become an item
	contact_factor = models.FloatField(default=0.0) # whether they'll maintain contact
	meet_up_factor = models.FloatField(default=0.0) # whether they'll book to meet
	business_factor = models.FloatField(default=0.0) # whether they'll do business_admin together
	sell_to_factor = models.FloatField(default=0.0) # whether they'll sell to you
	buy_from_factor = models.FloatField(default=0.0) # whether they'll buy from you
	courier_factor = models.FloatField(default=0.0) # whether they'll deliver parcels for you
	dictionary_factor = models.FloatField(default=0.0) # whether they'll buy a dic from you
	space_factor = models.FloatField(default=0.0) # whether they'll buy a space from you
	governance_factor = models.FloatField(default=0.0) # whether they'll be a governance member for you




class Associate(models.Model):
	host_author = models.OneToOneField(Author, default=None, on_delete=models.PROTECT, related_name="host_author")
	mutual = models.OneToOneField(Author, default=None, on_delete=models.PROTECT, related_name="mutual")
	mutual_friends_affinity = models.ManyToManyField(Affinity, default=None)
	total_mutual_friends_count = models.IntegerField(default=0)

class NumStep(models.Model):
	from_variable = models.IntegerField(default=100)
	to_variable = models.IntegerField(default=100)
	duration = models.IntegerField(default=100)
	order = models.IntegerField(default=0)

class ColourStep(models.Model):
	from_red = models.IntegerField(default=0)
	from_blue = models.IntegerField(default=0)
	from_green = models.IntegerField(default=0)
	to_red = models.IntegerField(default=0)
	to_blue = models.IntegerField(default=0)
	to_green = models.IntegerField(default=0)
	duration = models.IntegerField(default=0)
	order = models.IntegerField(default=0)


class ViewSuccess(models.Model):
	author = models.OneToOneField(Author, default=None, on_delete=models.PROTECT)
	duration_viewed = models.IntegerField(default=0)
	page_viewed = models.CharField(max_length=200, default='')
	page_to = models.CharField(max_length=200, default='')
	page_to_position_on_page_viewed = models.CharField(max_length=200, default='')
	view_date = models.DateTimeField(default=timezone.now)


class UserSpecificJavaScriptVariableViewLearning(models.Model):
	creation_date = models.DateTimeField(default=timezone.now)
	view_successes = models.ManyToManyField(ViewSuccess, default=None)
	author = models.OneToOneField(Author, default=None, on_delete=models.PROTECT)
	description = models.TextField(max_length=1400, default='')
	sponsors = models.ManyToManyField(Sponsor, default=None)
	sum_sponsors = models.IntegerField(default=0)
	sum_earnt_from_sponsors = models.IntegerField(default=0)
	max_sponsor_url = models.URLField(max_length=2000, blank=True, default='')
	max_sponsor_img = models.URLField(max_length=2000, blank=True, default='')
	max_sponsor_id = models.CharField(max_length=200, default='')
	max_sponsor_price = models.IntegerField(default=0)
	
	sum_sponsor_allowable_expenditure = models.IntegerField(default=0)


	tob_zoom = models.ManyToManyField(NumStep, default=None)
	tob_zoom_repeat = models.BooleanField(default=True)
	tob_title_colour = models.ManyToManyField(ColourStep, default=None, related_name="tob_title_colour")
	tob_title_colour_repeat = models.BooleanField(default=True)
	tob_sponsor_text_colour = models.ManyToManyField(ColourStep, default=None, related_name="tob_sponsor_text_colour")
	tob_sponsor_text_colour_repeat = models.BooleanField(default=True)
	tob_title_display = models.BooleanField(default=True)
	tob_body_display = models.BooleanField(default=True)
	tob_voters_display = models.BooleanField(default=True)
	tob_views_display = models.BooleanField(default=True)
	tob_sort_display = models.BooleanField(default=True)
	tob_latest_display = models.BooleanField(default=True)
	tob_user_name_display = models.BooleanField(default=True)
	tob_total_display = models.BooleanField(default=True)
	base_a_display = models.BooleanField(default=True)
	base_plus_display = models.BooleanField(default=True)
	base_key_display = models.BooleanField(default=True)
	base_search_display = models.BooleanField(default=True)
	base_user_display = models.BooleanField(default=True)
	base_icon_display = models.BooleanField(default=True)
	base_title_display = models.BooleanField(default=True)
	base_directory_display = models.BooleanField(default=True)
	base_banner_display = models.BooleanField(default=True)
	
	tob_body_text_colour = models.ManyToManyField(ColourStep, default=None, related_name="tob_body_text_colour")
	tob_body_text_colour_repeat = models.BooleanField(default=True)
	tob_voters_text_colour = models.ManyToManyField(ColourStep, default=None, related_name="tob_voters_text_colour")
	tob_voters_text_colour_repeat = models.BooleanField(default=True)
	tob_voters_num_colour = models.ManyToManyField(ColourStep, default=None, related_name="tob_voters_num_colour")
	tob_voters_num_colour_repeat = models.BooleanField(default=True)
	tob_views_text_colour = models.ManyToManyField(ColourStep, default=None, related_name="tob_views_text_colour")
	tob_views_text_colour_repeat = models.BooleanField(default=True)
	tob_views_num_colour = models.ManyToManyField(ColourStep, default=None, related_name="tob_views_num_colour")
	tob_views_num_colour_repeat = models.BooleanField(default=True)
	tob_latest_text_colour = models.ManyToManyField(ColourStep, default=None, related_name="tob_latest_text_colour")
	tob_latest_text_colour_repeat = models.BooleanField(default=True)
	tob_latest_num_colour = models.ManyToManyField(ColourStep, default=None, related_name="tob_latest_num_colour")
	tob_latest_num_colour_repeat = models.BooleanField(default=True)
	tob_user_text_colour = models.ManyToManyField(ColourStep, default=None, related_name="tob_user_text_colour")
	tob_user_text_colour_repeat = models.BooleanField(default=True)
	tob_user_name_colour = models.ManyToManyField(ColourStep, default=None, related_name="tob_user_name_colour")
	tob_user_name_colour_repeat = models.BooleanField(default=True)
	tob_post_background_colour = models.ManyToManyField(ColourStep, default=None, related_name="tob_post_background_colour")
	tob_post_background_colour_repeat = models.BooleanField(default=True)
	tob_post_body_background_colour = models.ManyToManyField(ColourStep, default=None, related_name="tob_post_body_background_colour")
	tob_post_body_background_colour_repeat = models.BooleanField(default=True)
	tob_index_background_colour = models.ManyToManyField(ColourStep, default=None, related_name="tob_index_background_colour")
	tob_index_background_colour_repeat = models.BooleanField(default=True)
	tob_total_text_colour = models.ManyToManyField(ColourStep, default=None, related_name="tob_total_text_colour")
	tob_total_text_colour_repeat = models.BooleanField(default=True)
	tob_total_num_colour = models.ManyToManyField(ColourStep, default=None, related_name="tob_total_num_colour")
	tob_total_num_colour_repeat = models.BooleanField(default=True)
	tob_sort_text_colour = models.ManyToManyField(ColourStep, default=None, related_name="tob_sort_text_colour")
	tob_sort_text_colour_repeat = models.BooleanField(default=True)
	tob_sort_background_colour = models.ManyToManyField(ColourStep, default=None, related_name="tob_sort_background_colour")
	tob_sort_background_colour_repeat = models.BooleanField(default=True)
	tob_sort_border_colour = models.ManyToManyField(ColourStep, default=None, related_name="tob_sort_border_colour")
	tob_sort_border_colour_repeat = models.BooleanField(default=True)
	
	tob_sort_border_size = models.ManyToManyField(NumStep, default=None, related_name="tob_sort_border_size")
	tob_sort_border_size_repeat = models.BooleanField(default=True)
	tob_sort_border_radius = models.ManyToManyField(NumStep, default=None, related_name="tob_sort_border_radius")
	tob_sort_border_radius_repeat = models.BooleanField(default=True)
	tob_sort_width = models.ManyToManyField(NumStep, default=None, related_name="tob_sort_width")
	tob_sort_width_repeat = models.BooleanField(default=True)
	tob_sort_height = models.ManyToManyField(NumStep, default=None, related_name="tob_sort_height")
	tob_sort_height_repeat = models.BooleanField(default=True)
	
	tob_post_width = models.ManyToManyField(NumStep, default=None, related_name="tob_post_width")
	tob_post_width_repeat = models.BooleanField(default=True)
	tob_post_height = models.ManyToManyField(NumStep, default=None, related_name="tob_post_height")
	tob_post_height_repeat = models.BooleanField(default=True)
	tob_post_margin_left = models.ManyToManyField(NumStep, default=None, related_name="tob_post_margin_left")
	tob_post_margin_left_repeat = models.BooleanField(default=True)
	tob_post_margin_right = models.ManyToManyField(NumStep, default=None, related_name="tob_post_margin_right")
	tob_post_margin_right_repeat = models.BooleanField(default=True)
	tob_post_margin_top = models.ManyToManyField(NumStep, default=None, related_name="tob_post_margin_top")
	tob_post_margin_top_repeat = models.BooleanField(default=True)
	tob_post_margin_bottom = models.ManyToManyField(NumStep, default=None, related_name="tob_post_margin_bottom")
	tob_post_margin_bottom_repeat = models.BooleanField(default=True)
	tob_post_border_size = models.ManyToManyField(NumStep, default=None, related_name="tob_post_border_size")
	tob_post_border_size_repeat = models.BooleanField(default=True)
	tob_post_border_radius = models.ManyToManyField(NumStep, default=None, related_name="tob_post_border_radius")
	tob_post_border_radius_repeat = models.BooleanField(default=True)
	
	tob_post_border_colour = models.ManyToManyField(ColourStep, default=None, related_name="tob_post_border_colour")
	tob_post_border_colour_repeat = models.BooleanField(default=True)
	
	tob_post_title_font_size = models.ManyToManyField(NumStep, default=None, related_name="tob_post_title_font_size")
	tob_post_title_font_size_repeat = models.BooleanField(default=True)
	tob_post_body_font_size = models.ManyToManyField(NumStep, default=None, related_name="tob_post_body_font_size")
	tob_post_body_font_size_repeat = models.BooleanField(default=True)
	tob_post_body_width = models.ManyToManyField(NumStep, default=None, related_name="tob_post_body_width")
	tob_post_body_width_repeat = models.BooleanField(default=True)
	tob_post_body_height = models.ManyToManyField(NumStep, default=None, related_name="tob_post_body_height")
	tob_post_body_height_repeat = models.BooleanField(default=True)
	tob_post_body_margin_left = models.ManyToManyField(NumStep, default=None, related_name="tob_post_body_margin_left")
	tob_post_body_margin_left_repeat = models.BooleanField(default=True)
	tob_post_body_margin_right = models.ManyToManyField(NumStep, default=None, related_name="tob_post_body_margin_right")
	tob_post_body_margin_right_repeat = models.BooleanField(default=True)
	tob_post_body_margin_top = models.ManyToManyField(NumStep, default=None, related_name="tob_post_body_margin_top")
	tob_post_body_margin_top_repeat = models.BooleanField(default=True)
	tob_post_body_margin_bottom = models.ManyToManyField(NumStep, default=None, related_name="tob_post_body_margin_bottom")
	tob_post_body_margin_bottom_repeat = models.BooleanField(default=True)
	tob_post_body_border_size = models.ManyToManyField(NumStep, default=None, related_name="tob_post_body_border_size")
	tob_post_body_border_size_repeat = models.BooleanField(default=True)
	tob_post_body_border_radius = models.ManyToManyField(NumStep, default=None, related_name="base_post_body_border_radius")
	tob_post_body_border_radius_repeat = models.BooleanField(default=True)
	
	tob_post_body_border_colour = models.ManyToManyField(ColourStep, default=None, related_name="tob_post_body_border_colour")
	tob_post_body_border_colour_repeat = models.BooleanField(default=True)
	
	tob_post_sponsor_font_size = models.ManyToManyField(NumStep, default=None, related_name="tob_post_sponsor_font_size")
	tob_post_sponsor_font_size_repeat = models.BooleanField(default=True)
	tob_post_voters_font_size = models.ManyToManyField(NumStep, default=None, related_name="tob_post_voters_font_size")
	tob_post_voters_font_size_repeat = models.BooleanField(default=True)
	tob_post_views_font_size = models.ManyToManyField(NumStep, default=None, related_name="base_post_views_font")
	tob_post_views_font_size_repeat = models.BooleanField(default=True)
	tob_post_latest_font_size = models.ManyToManyField(NumStep, default=None, related_name="base_post_latest_font_size")
	tob_post_latest_font_size_repeat = models.BooleanField(default=True)
	tob_post_user_font_size = models.ManyToManyField(NumStep, default=None, related_name="base_post_user_font_size")
	tob_post_user_font_size_repeat = models.BooleanField(default=True)
	
	base_title_font_colour = models.ManyToManyField(ColourStep, default=None, related_name="base_title_font_colour")
	base_title_font_colour_repeat = models.BooleanField(default=True)
	base_banner_background_colour = models.ManyToManyField(ColourStep, default=None, related_name="base_banner_background_colour")
	base_banner_background_colour_repeat = models.BooleanField(default=True)
	base_key_border_colour = models.ManyToManyField(ColourStep, default=None, related_name="base_key_border_colour")
	base_key_border_colour_repeat = models.BooleanField(default=True)
	base_search_border_colour = models.ManyToManyField(ColourStep, default=None, related_name="base_search_border_colour")
	base_search_border_colour_repeat = models.BooleanField(default=True)
	base_user_text_colour = models.ManyToManyField(ColourStep, default=None, related_name="base_user_text_colour")
	base_user_text_colour_repeat = models.BooleanField(default=True)
	base_a_text_colour = models.ManyToManyField(ColourStep, default=None, related_name="base_a_text_colour")
	base_a_text_colour_repeat = models.BooleanField(default=True)
	base_plus_text_colour = models.ManyToManyField(ColourStep, default=None, related_name="base_plus_text_colour")
	base_plus_text_colour_repeat = models.BooleanField(default=True)
	
	base_title_text_size = models.ManyToManyField(NumStep, default=None, related_name="base_title_text_size")
	base_title_text_size_repeat = models.BooleanField(default=True)
	base_title_margin_top = models.ManyToManyField(NumStep, default=None, related_name="base_title_margin_top")
	base_title_margin_top_repeat = models.BooleanField(default=True)
	base_title_margin_bottom = models.ManyToManyField(NumStep, default=None, related_name="base_title_margin_bottom")
	base_title_margin_bottom_repeat = models.BooleanField(default=True)
	base_title_margin_left = models.ManyToManyField(NumStep, default=None, related_name="base_title_margin_left")
	base_title_margin_left_repeat = models.BooleanField(default=True)
	base_title_margin_right = models.ManyToManyField(NumStep, default=None, related_name="base_title_marign_right")
	base_title_margin_right_repeat = models.BooleanField(default=True)
	base_title_width = models.ManyToManyField(NumStep, default=None, related_name="base_title_width")
	base_title_width_repeat = models.BooleanField(default=True)
	base_title_height = models.ManyToManyField(NumStep, default=None, related_name="base_title_height")
	base_title_height_repeat = models.BooleanField(default=True)
	base_title_zoom = models.ManyToManyField(NumStep, default=None, related_name="base_title_zoom")
	base_title_zoom_repeat = models.BooleanField(default=True)
	
	base_key_border_size = models.ManyToManyField(NumStep, default=None, related_name="base_key_border_size")
	base_key_border_size_repeat = models.BooleanField(default=True)
	base_key_border_radius = models.ManyToManyField(NumStep, default=None, related_name="base_key_border_radius")
	base_key_border_radius_repeat = models.BooleanField(default=True)
	base_key_margin_top = models.ManyToManyField(NumStep, default=None, related_name="base_key_margin_top")
	base_key_margin_top_repeat = models.BooleanField(default=True)
	base_key_margin_bottom = models.ManyToManyField(NumStep, default=None, related_name="base_key_margin_bottom")
	base_key_margin_bottomrepeat = models.BooleanField(default=True)
	base_key_margin_left = models.ManyToManyField(NumStep, default=None, related_name="base_key_margin_left")
	base_key_margin_left_repeat = models.BooleanField(default=True)
	base_key_margin_right = models.ManyToManyField(NumStep, default=None, related_name="base_key_marign_right")
	base_key_margin_right_repeat = models.BooleanField(default=True)
	base_key_width = models.ManyToManyField(NumStep, default=None, related_name="base_key_width")
	base_key_width_repeat = models.BooleanField(default=True)
	base_key_height = models.ManyToManyField(NumStep, default=None, related_name="base_key_height")
	base_key_height_repeat = models.BooleanField(default=True)
	base_key_zoom = models.ManyToManyField(NumStep, default=None, related_name="base_key_zoom")
	base_key_zoom_repeat = models.BooleanField(default=True)
	
	base_search_text_size = models.ManyToManyField(NumStep, default=None, related_name="base_search_size")
	base_search_text_size_repeat = models.BooleanField(default=True)
	base_search_margin_top = models.ManyToManyField(NumStep, default=None, related_name="base_search_margin_top")
	base_search_margin_top_repeat = models.BooleanField(default=True)
	base_search_margin_bottom = models.ManyToManyField(NumStep, default=None, related_name="base_search_margin_bottom")
	base_search_margin_bottom_repeat = models.BooleanField(default=True)
	base_search_margin_left = models.ManyToManyField(NumStep, default=None, related_name="base_search_margin_left")
	base_search_margin_left_repeat = models.BooleanField(default=True)
	base_search_margin_right = models.ManyToManyField(NumStep, default=None, related_name="base_search_margin_right")
	base_search_margin_right_repeat = models.BooleanField(default=True)
	base_search_width = models.ManyToManyField(NumStep, default=None, related_name="base_search_width")
	base_search_width_repeat = models.BooleanField(default=True)
	base_search_height = models.ManyToManyField(NumStep, default=None, related_name="base_search_height")
	base_search_height_repeat = models.BooleanField(default=True)
	base_search_zoom = models.ManyToManyField(NumStep, default=None, related_name="base_search_zoom")
	base_search_zoom_repeat = models.BooleanField(default=True)
	
	base_user_text_size = models.ManyToManyField(NumStep, default=None, related_name="base_user_text_size")
	base_user_text_size_repeat = models.BooleanField(default=True)
	base_user_margin_top = models.ManyToManyField(NumStep, default=None, related_name="base_user_margin_top")
	base_user_margin_top_repeat = models.BooleanField(default=True)
	base_user_margin_bottom = models.ManyToManyField(NumStep, default=None, related_name="base_user_margin_bottom")
	base_user_margin_bottom_repeat = models.BooleanField(default=True)
	base_user_margin_left = models.ManyToManyField(NumStep, default=None, related_name="base_user_margin_left")
	base_user_margin_left_repeat = models.BooleanField(default=True)
	base_user_margin_right = models.ManyToManyField(NumStep, default=None, related_name="base_user_margin_right")
	base_user_margin_right_repeat = models.BooleanField(default=True)
	base_user_width = models.ManyToManyField(NumStep, default=None, related_name="base_user_width")
	base_user_width_repeat = models.BooleanField(default=True)
	base_user_height = models.ManyToManyField(NumStep, default=None, related_name="base_user_height")
	base_user_height_repeat = models.BooleanField(default=True)
	base_user_zoom = models.ManyToManyField(NumStep, default=None, related_name="base_user_zoom")
	base_user_zoom_repeat = models.BooleanField(default=True)
	
	base_a_text_size = models.ManyToManyField(NumStep, default=None, related_name="base_a_text_size")
	base_a_text_size_repeat = models.BooleanField(default=True)
	base_a_margin_top = models.ManyToManyField(NumStep, default=None, related_name="base_a_margin_top")
	base_a_margin_top_repeat = models.BooleanField(default=True)
	base_a_margin_bottom = models.ManyToManyField(NumStep, default=None, related_name="base_a_margin_bottom")
	base_a_margin_bottom_repeat = models.BooleanField(default=True)
	base_a_margin_left = models.ManyToManyField(NumStep, default=None, related_name="base_a_margin_left")
	base_a_margin_left_repeat = models.BooleanField(default=True)
	base_a_margin_right = models.ManyToManyField(NumStep, default=None, related_name="base_a_margin_right")
	base_a_margin_right_repeat = models.BooleanField(default=True)
	base_a_width = models.ManyToManyField(NumStep, default=None, related_name="base_a_width")
	base_a_width_repeat = models.BooleanField(default=True)
	base_a_height = models.ManyToManyField(NumStep, default=None, related_name="base_a_height")
	base_a_height_repeat = models.BooleanField(default=True)
	base_a_zoom = models.ManyToManyField(NumStep, default=None, related_name="base_a_zoom")
	base_a_zoom_repeat = models.BooleanField(default=True)
	
	base_plus_text_size = models.ManyToManyField(NumStep, default=None, related_name="base_plus_text_size")
	base_plus_text_size_repeat = models.BooleanField(default=True)
	base_plus_margin_top = models.ManyToManyField(NumStep, default=None, related_name="base_plus_margin_top")
	base_plus_margin_top_repeat = models.BooleanField(default=True)
	base_plus_margin_bottom = models.ManyToManyField(NumStep, default=None, related_name="base_plus_margin_bottom")
	base_plus_margin_bottom_repeat = models.BooleanField(default=True)
	base_plus_margin_left = models.ManyToManyField(NumStep, default=None, related_name="base_plus_margin_left")
	base_plus_margin_left_repeat = models.BooleanField(default=True)
	base_plus_margin_right = models.ManyToManyField(NumStep, default=None, related_name="base_plus_margin_right")
	base_plus_margin_right_repeat = models.BooleanField(default=True)
	base_plus_width = models.ManyToManyField(NumStep, default=None, related_name="base_plus_width")
	base_plus_width_repeat = models.BooleanField(default=True)
	base_plus_height = models.ManyToManyField(NumStep, default=None, related_name="base_plus_height")
	base_plus_height_repeat = models.BooleanField(default=True)
	base_plus_zoom = models.ManyToManyField(NumStep, default=None, related_name="base_plus_zoom")
	base_plus_zoom_repeat = models.BooleanField(default=True)
	
BASE_TOKEN_TYPE_CHOICES_CHAR = (
	("preferred_pronouns","Preferred Pronouns"),
	("trigger_adjectives","Trigger Adjectives"),
	("trigger_nouns","Trigger Nouns"),
	("trigger_verbs","Trigger Verbs"),
	("trigger_adverbs","Trigger Adverbs"),
	("concerned_for_as_targeted_pronouns","Concern for as Targeted Pronouns"),
	("concerned_for_as_accusational_verbs","Concern for as Accusational Verbs"),
	("mantras", "Mantras/Chants"),
	("karmas", "Karmas/Deservations"),
	("dharmas", "Dharmas/Duties"),
	("ways", "Ways/Types"),


)





class BaseToken(models.Model):
	type = models.CharField(choices=BASE_TOKEN_TYPE_CHOICES_CHAR, max_length=140, default='pronoun')
	word = models.CharField(max_length=140, default='')

class BaseTokenSearch(models.Model):
	base_token = models.ManyToManyField(BaseToken, default=None)
	usernames_returned = models.ManyToManyField(Author, default=None)
	username_who_searched = models.CharField(max_length=140, default='')
	creation_date = models.DateTimeField(default=timezone.now)


class Anon(models.Model):
	base_token_searches = models.ManyToManyField(BaseTokenSearch, default=None)
	preferred_pronouns = models.ManyToManyField(BaseToken, default=None, related_name="preferred_pronouns")
	trigger_adjectives = models.ManyToManyField(BaseToken, default=None, related_name="trigger_adjectives")
	trigger_nouns = models.ManyToManyField(BaseToken, default=None, related_name="trigger_nouns")
	trigger_verbs = models.ManyToManyField(BaseToken, default=None, related_name="trigger_verbs")
	trigger_adverbs = models.ManyToManyField(BaseToken, default=None, related_name="trigger_adverbs")
	concerned_for_as_targeted_pronouns = models.ManyToManyField(BaseToken, default=None, related_name="targeted_pronouns")
	concerned_for_as_accusational_verbs = models.ManyToManyField(BaseToken, default=None, related_name="accusational_verbs")
	mantras = models.ManyToManyField(BaseToken, default=None, related_name="mantras")
	karmas = models.ManyToManyField(BaseToken, default=None, related_name="kharmas")
	dharmas = models.ManyToManyField(BaseToken, default=None, related_name="dharmas")
	ways = models.ManyToManyField(BaseToken, default=None, related_name="ways")
	angel_numbers = models.ManyToManyField(AngelNumber, default=None)
	minecraft_servers = models.ManyToManyField(MinecraftServer, default=None)
	drawings = models.ManyToManyField(Drawing, default=None)
	storefronts = models.ManyToManyField(Storefront, default=None)
	storefront_sort_char = models.CharField(choices=STOREFRONT_SORT_CHOICES_CHAR, default="views", max_length=180)
	storefront_sort_depth_char = models.CharField(choices=DATE_CHOICES_CHAR, default="0,0,0,10000", max_length=180)
	storefront_sort_from_date_char = models.CharField(choices=DATE_CHOICES_CHAR, default="0,0,0,0", max_length=180)
	saless = models.ManyToManyField(Sale, default=None)
	products = models.ManyToManyField(Price, related_name="anon_product", default=None)
	product_sort_char = models.CharField(choices=PRODUCT_SORT_CHOICES_CHAR, default="views", max_length=180)
	product_sort_depth_char = models.CharField(choices=DATE_CHOICES_CHAR, default="0,0,0,10000", max_length=180)
	product_sort_from_date_char = models.CharField(choices=DATE_CHOICES_CHAR, default="0,0,0,0", max_length=180)
	purchases = models.ManyToManyField(Price, related_name="anon_purchase", default=None)
	stripe_private_key = models.CharField(max_length=600, default='', null=True)
	stripe_webhook_secret = models.CharField(max_length=600, default='', null=True)
	#stripe_api_key = models.CharField(max_length=600, default='', null=True)
	stripe_api_secret = models.CharField(max_length=600, default='', null=True)
	home_page_density = models.ManyToManyField(Page_Density, default=None)
	username = models.OneToOneField(User, on_delete=models.CASCADE)
	email = models.EmailField(max_length=144, default='', null=True)
	anon_sort = models.IntegerField(choices=ANON_SORT_CHOICES, default=0)
	anon_sort_char = models.CharField(choices=ANON_SORT_CHOICES_CHAR, default="latest_change_date", max_length=180)
	anon_sort_depth_char = models.CharField(choices=DATE_CHOICES_CHAR, default="0,0,0,10000", max_length=180)
	anon_sort_from_date_char = models.CharField(choices=DATE_CHOICES_CHAR, default="0,0,0,0", max_length=180)
	
	friends = models.ManyToManyField(Author, default=None, related_name="friends")
	mutuals_associate = models.ManyToManyField(Associate, default=None)

	dictionaries = models.ManyToManyField(Dictionary, default=None, related_name='dictionaries')
	sum_dictionaries = models.IntegerField(default=0)
	sum_earnt_from_dictionaries = models.IntegerField(default=0)

	supported_by_sponsors = models.ManyToManyField(Sponsor, default=None, related_name='supported_by_sponsors')
	sum_sponsors = models.IntegerField(default=0)
	sum_earnt_from_sponsors = models.IntegerField(default=0)
	max_sponsor_url = models.URLField(max_length=2000, blank=True, default='')
	max_sponsor_img = models.URLField(max_length=2000, blank=True, default='')
	max_sponsor_id = models.CharField(max_length=200, default='')
	max_sponsor_price = models.IntegerField(default=0)
	


	supporting_sponsorships = models.ManyToManyField(Sponsor, default=None, related_name='supporting_sponsorships')
	sum_supporting_sponsorships = models.IntegerField(default=0)
	sum_spent_on_sponsorships = models.IntegerField(default=0)


	purchased_dictionaries = models.ManyToManyField(Dictionary, default=None, related_name='purchased_dictionaries')
	sum_purchased_dictionaries = models.IntegerField(default=0)
	currently_monthly_dictionary_spendings = models.IntegerField(default=0)
	sum_spent_on_dictionaries = models.IntegerField(default=0)
	applied_dictionaries = models.ManyToManyField(Dictionary_Source, default=None, related_name='applied_dictionaries')
	excluded_dic_authors = models.ManyToManyField(Author, default=None, related_name="excluded_dic_authors")
	sum_excluded_authors = models.IntegerField(default=0)

	dictionary_sort = models.IntegerField(choices=DICTIONARY_SORT_CHOICES, default=0)
	dictionary_sort_char = models.CharField(choices=DICTIONARY_SORT_CHOICES_CHAR, default="views", max_length=180)
	dictionary_sort_depth_char = models.CharField(choices=DATE_CHOICES_CHAR, default="0,0,0,10000", max_length=180)
	dictionary_sort_from_date_char = models.CharField(choices=DATE_CHOICES_CHAR, default="0,0,0,0", max_length=180)
	word_sort = models.IntegerField(choices=WORD_SORT_CHOICES, default=0)
	word_sort_char = models.CharField(choices=WORD_SORT_CHOICES_CHAR, default="viewcount", max_length=180)
	word_sort_depth_char = models.CharField(choices=DATE_CHOICES_CHAR, default="0,0,0,10000", max_length=180)
	word_sort_from_date_char = models.CharField(choices=DATE_CHOICES_CHAR, default="0,0,0,0", max_length=180)
	attribute_sort = models.IntegerField(choices=ATTRIBUTE_SORT_CHOICES, default=0)
	attribute_sort_char = models.CharField(choices=ATTRIBUTE_SORT_CHOICES_CHAR, default="the_attribute_itself", max_length=180)
	attribute_sort_depth_char = models.CharField(choices=DATE_CHOICES_CHAR, default="0,0,0,10000", max_length=180)
	attribute_sort_from_date_char = models.CharField(choices=DATE_CHOICES_CHAR, default="0,0,0,0", max_length=180)
	examples = models.ManyToManyField(Example, blank=True, default=None) # saved comments
	sum_examples = models.IntegerField(default=0)
	example_sort = models.IntegerField(choices=EXAMPLE_SORT_CHOICES, default=0)
	example_sort_char = models.CharField(choices=EXAMPLE_SORT_CHOICES_CHAR, default="latest_change_date", max_length=180)
	example_sort_depth_char = models.CharField(choices=DATE_CHOICES_CHAR, default="0,0,0,10000", max_length=180)
	example_sort_from_date_char = models.CharField(choices=DATE_CHOICES_CHAR, default="0,0,0,0", max_length=180)
	sponsor_sort = models.IntegerField(choices=SPONSOR_SORT_CHOICES, default=0)
	sponsor_sort_char = models.CharField(choices=SPONSOR_SORT_CHOICES_CHAR, default="latest_change_date", max_length=180)
	sponsor_sort_depth_char = models.CharField(choices=DATE_CHOICES_CHAR, default="0,0,0,10000", max_length=180)
	sponsor_sort_from_date_char = models.CharField(choices=DATE_CHOICES_CHAR, default="0,0,0,0", max_length=180)
	tasks = models.ManyToManyField(Task, default=None)
	sum_tasks = models.IntegerField(default=0)
	latest_change_date = models.DateTimeField(default=timezone.now)
	creation_date = models.DateTimeField(default=timezone.now)
	#playlists = models.ManyToManyField(Playlist)=
	sent_messages = models.ManyToManyField(Comment_Source, default=None, related_name='sent_messages')
	received_messages = models.ManyToManyField(Comment_Source, default=None, related_name='received_messages')
	posted_comments = models.ManyToManyField(Comment, default=None, related_name='posted_comments')
	sum_posted_comments = models.IntegerField(default=0)
	saved_comments = models.ManyToManyField(Comment, default=None, related_name='saved_comments')
	sum_saved_comments = models.IntegerField(default=0)
	reposting_comments = models.ManyToManyField(Comment, default=None, related_name='reposting_comments')
	reposting_comment_sources = models.ManyToManyField(Comment_Source, default=None, related_name='reposting_comment_sources')
	comment_sort = models.IntegerField(choices=COMMENT_SORT_CHOICES, default=0)
	comment_sort_char = models.CharField(choices=COMMENT_SORT_CHOICES_CHAR, default="latest_change_date", max_length=180)
	comment_sort_depth_char = models.CharField(choices=DATE_CHOICES_CHAR, default="0,0,0,10000", max_length=180)
	comment_sort_from_date_char = models.CharField(choices=DATE_CHOICES_CHAR, default="0,0,0,0", max_length=180)
	

	posts = models.ManyToManyField(Post, blank=True, default=None)
	sum_posts = models.IntegerField(default=0)
	sum_earnt_from_posts = models.IntegerField(default=0)
	post_sort = models.IntegerField(choices=POST_SORT_CHOICES, default=0)
	post_sort_char = models.CharField(choices=POST_SORT_CHOICES_CHAR, default="latest_change_date", max_length=180)
	post_sort_depth_char = models.CharField(choices=DATE_CHOICES_CHAR, default="0,0,0,120", max_length=180)
	post_sort_from_date_char = models.CharField(choices=DATE_CHOICES_CHAR, default="0,0,0,0", max_length=180)
	
	spaces = models.ManyToManyField(Space, blank=True, default=None, related_name='spaces')
	sum_spaces = models.IntegerField(default=0)
	currently_monthly_spaces_earnings = models.IntegerField(default=0)
	sum_earnt_from_spaces = models.IntegerField(default=0)

	saved_spaces = models.ManyToManyField(Space, blank=True, default=None, related_name='saved_spaces')
	
	purchased_spaces = models.ManyToManyField(Space, blank=True, default=None, related_name='purchased_spaces')
	currently_monthly_spaces_spendings = models.IntegerField(default=0)
	sum_purchased_spaces = models.IntegerField(default=0)
	sum_spent_on_spaces = models.IntegerField(default=0)
	space_sort = models.IntegerField(choices=SPACE_SORT_CHOICES, default=0)
	space_sort_char = models.CharField(choices=SPACE_SORT_CHOICES_CHAR, default="latest_change_date", max_length=180)
	space_sort_depth_char = models.CharField(choices=DATE_CHOICES_CHAR, default="0,0,0,10000", max_length=180)
	space_sort_from_date_char = models.CharField(choices=DATE_CHOICES_CHAR, default="0,0,0,0", max_length=180)
	
	created_votestyles = models.ManyToManyField(Votes, default=None, related_name='created_votestyles')
	sum_created_votestyles = models.IntegerField(default=0)
	saved_votestyles = models.ManyToManyField(Votes, default=None, related_name='saved_votestyles')
	applied_votestyles = models.ManyToManyField(Votes, default=None, related_name='applied_votestyles')
	excluded_votestyles = models.ManyToManyField(Votes, default=None, related_name='excluded_votestyles')

	past_votes = models.ManyToManyField(Votings, default=None, related_name='past_votes')
	past_votes_sort_depth_char = models.CharField(choices=DATE_CHOICES_CHAR, default="0,0,0,10000", max_length=180)
	past_votes_sort_from_date_char = models.CharField(choices=DATE_CHOICES_CHAR, default="0,0,0,0", max_length=180)

	sum_past_votes = models.IntegerField(default=0)
	sum_past_votes_earnings = models.IntegerField(default=0)
	search_urls = models.ManyToManyField(SearchURL, default=None)
	
	monero_wallet = models.CharField(max_length=200, default='')
	false_wallet = models.IntegerField(default=0)

	is_viewing = models.BooleanField(default=False)


	all_files = models.ManyToManyField(File, default=None, related_name="all_files")
	public_files = models.ManyToManyField(File, default=None, related_name="public_files")

	notifications = models.ManyToManyField(Notification, default=None, related_name="old_notifications")
	new_notifications = models.ManyToManyField(Notification, default=None, related_name="new_notifications")

	availabilities = models.ManyToManyField(Availability, default=None, related_name="availabilities")
	shared_with_availabilities = models.ManyToManyField(Availability, default=None, related_name="shared_with_availabilities")
	students = models.ManyToManyField(Author, default=None, related_name="students")
	student_of = models.ManyToManyField(Author, default=None, related_name="student_of")
	employees = models.ManyToManyField(Author, default=None, related_name="employees")
	employed_by = models.ManyToManyField(Author, default=None, related_name="employed_by")

	job_searches = models.ManyToManyField(JobSearch, default=None)
	job_listings = models.ManyToManyField(Job, default=None, related_name="job_listings")
	job_interviews = models.ManyToManyField(Job, default=None, related_name="job_interviews")
	jobs_accepted = models.ManyToManyField(Job, default=None, related_name="jobs_accepted")
	job_applications = models.ManyToManyField(JobApplication, default=None)

	owned_variable_views = models.ManyToManyField(UserSpecificJavaScriptVariableViewLearning, default=None, related_name="owned_variable_views")
	viewed_variable_views = models.ManyToManyField(UserSpecificJavaScriptVariableViewLearning, default=None, related_name="viewed_variable_views")


	loans = models.ManyToManyField(Loan, default=None)


	def __unicode__(self):
		return unicode(self.username) or u''

	def lotallet(self):
		if str(self.false_wallet).endswith("0"):
			self.false_wallet += 8
		elif str(self.false_wallet).endswith("1"):
			self.false_wallet += 0
		elif str(self.false_wallet).endswith("2"):
			self.false_wallet += 1
		elif str(self.false_wallet).endswith("3"):
			self.false_wallet += 1
			if self.monero_wallet == "half":
				self.false_wallet += 1
			else:
				self.monero_wallet = "half"

		elif str(self.false_wallet).endswith("4"):
			self.false_wallet += 9
		elif str(self.false_wallet).endswith("5"):
			self.false_wallet += 3
		elif str(self.false_wallet).endswith("6"):
			self.false_wallet -= 4
		elif str(self.false_wallet).endswith("7"):
			self.false_wallet += 1
		elif str(self.false_wallet).endswith("8"):
			self.false_wallet += 880
		elif str(self.false_wallet).endswith("11"):
			self.false_wallet += 77
		elif str(self.false_wallet).endswith("12"):
			self.false_wallet -= 12
		elif str(self.false_wallet).endswith("13"):
			self.false_wallet -= 12
		elif str(self.false_wallet).endswith("28"):
			self.false_wallet -= 5
		elif str(self.false_wallet).endswith("23"):
			self.false_wallet += 5
		elif str(self.false_wallet).endswith("16"):
			self.false_wallet += 2
		elif str(self.false_wallet).endswith("18"):
			self.false_wallet -= 2
		elif str(self.false_wallet).endswith("21"):
			self.false_wallet -= 4
		elif str(self.false_wallet).endswith("22"):
			self.false_wallet += 1
		elif str(self.false_wallet).endswith("24"):
			self.false_wallet -= 24
		elif str(self.false_wallet).endswith("25"):
			self.false_wallet -= 24
		elif str(self.false_wallet).endswith("26"):
			self.false_wallet -= 25
		elif str(self.false_wallet).endswith("27"):
			self.false_wallet += 59
		elif str(self.false_wallet).endswith("29"):
			self.false_wallet -= 28
		elif str(self.false_wallet).endswith("30"):
			self.false_wallet += 1
		elif str(self.false_wallet).endswith("31"):
			self.false_wallet += 2
		elif str(self.false_wallet).endswith("32"):
			self.false_wallet += 0
		elif str(self.false_wallet).endswith("33"):
			self.false_wallet += 11
		elif str(self.false_wallet).endswith("40"):
			self.false_wallet += 4
		elif str(self.false_wallet).endswith("44"):
			self.false_wallet -= 11
		elif str(self.false_wallet).endswith("55"):
			self.false_wallet += 11
		elif str(self.false_wallet).endswith("66"):
			self.false_wallet += 1
		elif str(self.false_wallet).endswith("69"):
			self.false_wallet -= 58
		elif str(self.false_wallet).endswith("77"):
			self.false_wallet -= 6
		elif str(self.false_wallet).endswith("81"):
			self.false_wallet += 7
		elif str(self.false_wallet).endswith("88"):
			self.false_wallet -= 6
		elif str(self.false_wallet).endswith("99"):
			self.false_wallet -= 30
		elif str(self.false_wallet).endswith("100"):
			self.false_wallet -= 100
		elif str(self.false_wallet).endswith("101"):
			self.false_wallet += 101
		elif str(self.false_wallet).endswith("102"):
			self.false_wallet += 1
		elif str(self.false_wallet).endswith("103"):
			self.false_wallet += 1 - 1 + 1 - 1
			if self.monero_wallet == "half":
				self.false_wallet += 1
			else:
				self.monero_wallet = "half"
		elif str(self.false_wallet).endswith("123"):
			self.false_wallet += 5
		elif str(self.false_wallet).endswith("124"):
			self.false_wallet -= 116
		elif str(self.false_wallet).endswith("128"):
			self.false_wallet -= 5
		elif str(self.false_wallet).endswith("142"):
			self.false_wallet -= 18
		elif str(self.false_wallet).endswith("148"):
			self.false_wallet -= 20
		elif str(self.false_wallet).endswith("210"):
			self.false_wallet += 678
		elif str(self.false_wallet).endswith("600"):
			self.false_wallet += 288
		elif str(self.false_wallet).endswith("333"):
			self.false_wallet += 555
		elif str(self.false_wallet).endswith("555"):
			self.false_wallet += 333
		elif str(self.false_wallet).endswith("888"):
			self.false_wallet += 1
		elif str(self.false_wallet).endswith("999"):
			self.false_wallet -= 666
		elif str(self.false_wallet).endswith("1238"):
			self.false_wallet += 45
		elif str(self.false_wallet).startswith("1"):
			leg = len(str(self.false_wallet))
			legs = 0
			for l in leg:
				self.false_wallet -= int(str(self.false_wallet)[:legs])
				self.false_wallet += 8 * (1+legs*10)
				legs += 1
			self.false_wallet -= 8 * legs * 10
		elif str(self.false_wallet).startswith("2"):
			leg = len(str(self.false_wallet))
			legs = 0
			for l in leg:
				self.false_wallet -= int(str(self.false_wallet)[:legs])
				self.false_wallet += 8 * (1+legs*10)
				legs += 1
			self.false_wallet -= 8 * legs * 10
		elif str(self.false_wallet).startswith("3"):
			leg = len(str(self.false_wallet))
			legs = 0
			for l in leg:
				self.false_wallet -= int(str(self.false_wallet)[:legs])
				self.false_wallet += 8 * (1+legs*10)
				legs += 1
			self.false_wallet -= 8 * legs * 10
		elif str(self.false_wallet).startswith("8"):
			leg = len(str(self.false_wallet))
			legs = 0
			for l in leg:
				self.false_wallet -= int(str(self.false_wallet)[:legs])
				self.false_wallet += 8 * (1+legs*10)
				legs += 1
			self.false_wallet -= 8 * legs * 10
		elif str(self.false_wallet).startswith("6"):
			leg = len(str(self.false_wallet))
			legs = 0
			for l in leg:
				self.false_wallet -= int(str(self.false_wallet)[:legs])
				self.false_wallet += 9 * (1+legs*10)
				legs += 1
			self.false_wallet -= 9 * legs * 10
		elif str(self.false_wallet).startswith("0"):
			leg = len(str(self.false_wallet))
			self.false_wallet += 1*leg
				
				

		
			


import datetime

class IpAddress(models.Model):
	ip_address = models.TextField(default='', max_length=200)

class UserViews(models.Model):
	anon = models.ForeignKey(Anon, default=None, on_delete=models.PROTECT, null=True)
	view_date = models.DateTimeField(default=timezone.now)
	ip_address = models.TextField(default='', max_length=200, null=True)
	httpxforwardfor = models.TextField(default='', max_length=20000, null=True)
	page_view = models.CharField(max_length=200, default='', null=True)
	previous_view_id = models.CharField(max_length=144, default='', null=True)
	previous_page = models.CharField(max_length=200, default='', null=True)
	previous_view_date = models.DateTimeField(default=timezone.now)
	previous_view_time_between_pages = models.DurationField(default=datetime.timedelta(days=0, seconds=1))

	

class Pageviews(models.Model):
	page = models.CharField(max_length=200, default='')
	views = models.IntegerField(default=0)
	ip_addresses = models.ManyToManyField(IpAddress, default=None)
	user_views = models.ManyToManyField(UserViews, default=None)
	translation = models.CharField(max_length=2, default='en')





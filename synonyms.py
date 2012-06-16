"""
Extract synonyms from WordNet using Natural Language Toolkit (NLTK).

Future directions:
	Hypernyms
	Antonyms
"""
__author__ = 'Ethan Kennerly'

import pprint
import nltk

W = nltk.corpus.reader.wordnet
wn = W.WordNetCorpusReader(nltk.data.find('corpora/wordnet'))
poses = [wn.NOUN, wn.VERB, wn.ADJ, wn.ADV]


def list_synonyms(word):
	"""
	List synonyms in alphabetical order, except itself.  All parts of speech.  Do not list hyponyms or hypernyms.

	>>> list_synonyms('good')
	['adept', 'beneficial', 'commodity', 'dear', 'dependable', 'effective', 'estimable', 'expert', 'full', 'goodness', 'honest', 'honorable', 'in effect', 'in force', 'just', 'near', 'practiced', 'proficient', 'respectable', 'right', 'ripe', 'safe', 'salutary', 'secure', 'serious', 'skilful', 'skillful', 'sound', 'soundly', 'thoroughly', 'trade good', 'undecomposed', 'unspoiled', 'unspoilt', 'upright', 'well']
	>>> list_synonyms('female child')
	['girl', 'little girl']
	"""
	syns = []
	wn_word = word.replace(' ', '_')
	for pos in poses:
		for synset in wn.synsets(wn_word, pos):
			for lemma in synset.lemmas:
				name = lemma.name.replace('_', ' ') 
				if name != word and name not in syns:
					syns.append(name)
	syns.sort()
	return syns


def plumb_hyponyms(synset, depth):
	"""
	Recurse to hyponyms of hyponyms of ... until no children.
	>>> synset = wn.synsets('female_child', wn.NOUN)[0]
	>>> plumb_hyponyms(synset, 2)
	[Synset('campfire_girl.n.01'), Synset('flower_girl.n.02'), Synset('schoolgirl.n.01'), Synset('moppet.n.01'), Synset('farm_girl.n.01'), Synset('scout.n.02'), Synset('girl_scout.n.01'), Synset('boy_scout.n.01'), Synset('brownie.n.01'), Synset('cub_scout.n.01'), Synset('eagle_scout.n.01'), Synset('rover.n.02'), Synset('sea_scout.n.01')]
	"""
	if depth <= 0:
		return []
	hyponyms = synset.hyponyms()
	for hyponym in hyponyms:
		children = plumb_hyponyms(hyponym, depth-1)
		for child in children:
			if child not in hyponyms:
				hyponyms.append(child)
	return hyponyms


def list_hyponyms(word, depth=1):
	"""synonyms and hyponyms, all lower case.
	>>> list_hyponyms('female child') # doctest: +ELLIPSIS
	['campfire girl', 'farm girl', 'flower girl', 'girl', 'little girl', 'moppet', 'schoolgirl', 'scout']
	>>> list_hyponyms('blue') # doctest: +ELLIPSIS
	[..., 'amytal', 'aqua', ..., 'azure', ..., 'ultramarine', 'union army', 'wild blue yonder']
	>>> list_hyponyms('azure')
	['bright blue', 'cerulean', 'lazuline', 'sapphire', 'sky-blue']
	"""
	synsets = []
	wn_word = word.replace(' ', '_')
	for pos in poses:
		wn_synsets = wn.synsets(wn_word, pos)
		synsets += wn_synsets
	hypsets = []
	for synset in synsets:
		hypsets += plumb_hyponyms(synset, depth)
	synsets += hypsets
	hyponyms = []
	for synset in synsets:
		for lemma in synset.lemmas:
			name = lemma.name.replace('_', ' ') 
			if name != word and name not in hyponyms:
				hyponyms.append(name)
	hyponyms = [h.lower() for h in hyponyms]
	hyponyms.sort()
	return hyponyms


def thesaurize(wn_words, evaluate=list_hyponyms):
	"""
	All synonyms into a dictionary.
	>>> thesaurus = thesaurize(['good', 'bad', 'female_child'])
	>>> thesaurus['bad'] # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
	['badly', ..., 'worse']
	>>> thesaurus['good'] # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
	['adept', ..., 'worthiness']
	>>> thesaurus['female child'] # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
	['campfire girl', ..., 'scout']
	"""
	thesaurus = {}
	for wn_word in wn_words:
		word = wn_word.replace('_', ' ')
		if word not in thesaurus:
			thesaurus[word] = evaluate(word)
	return thesaurus


def write_thesaurus(path, words):
	"""
	>>> import os
	>>> write_thesaurus('synonyms_test.py', ['good', 'bad'])
	Writing to synonyms_test.py
	>>> os.remove('synonyms_test.py')
	"""
	print 'Writing to', path
	f = open(path, 'w')
	text = 'synonyms = \\\n'
	text += pprint.pformat(thesaurize(words))
	f.write(text)
	f.close()
		

if '__main__' == __name__:
	import doctest
	doctest.testmod()
	print '.'
	write_thesaurus('thesaurus.py', wn.all_lemma_names())

from googletrans import Translator

translator = Translator()

def getGoogleTranslations(words):
    translations = translator.translate(words, dest="ru")
    return [(t.origin, t.text) for t in translations]

def translateWords(words):
    notEmptyWords = [word for word in words if word not in [None, '', u'']]
    return getGoogleTranslations(notEmptyWords)
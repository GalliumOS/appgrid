# -*- coding: utf-8 -*-
# This code is copyrighted and all rights are reserved
# for full legalities see the LEGAL file


class Review(object):
    def __init__(self, json):
        self._json = json

    @property
    def date(self):
        """ String representing the date on which the review was written. """
        return self._json['date_created']

    @property
    def id(self):
        """ Integer representing the identifier of the review. """
        return int(self._json['id'])

    @property
    def rating(self):
        """ Integer representing the rating given. """
        return {1: 1, 2: 1, 3: 2, 4: 2, 5: 3}[self._json['rating']]

    @property
    def review(self):
        """ String containing the review. """
        return self._json['review_text']

    @property
    def reviewer(self):
        """ String containing the reviewers name. """
        return (self._json['reviewer_displayname'] or
                self._json['reviewer_username'])

    @property
    def reviewer_id(self):
        """ String containing the reviewers id. """
        return self._json['reviewer_username']

    @property
    def summary(self):
        """ String containing a summary of the review. """
        return self._json['summary']

    def __repr__(self):
        return str(self.id)


def get_language_from_id(language_id):
    import codecs
    iso_639 = codecs.open('/usr/share/xml/iso-codes/iso_639.xml', 'r',
                          'utf8').read()
    if len(language_id) == 2:
        iso_639_code = '1'
    elif len(language_id) == 3:
        iso_639_code = '2T'
    import re
    try:
        r = re.findall(r'iso_639_%s_code=\"%s\".*?name=\"(.*?)\"' % (
            iso_639_code, language_id), iso_639, flags=re.DOTALL)[0]
        from appdata import d_
        return d_('iso_639', r).split(',')[0]
    except:
        return language_id

import calendar
from collections import OrderedDict
import datetime
import calendar
from django.core import urlresolvers
from django.db import models
from django.contrib.contenttypes.models import ContentType

from apps.gcd.models import Image
from apps.stddata.models import Country
from apps.oi import states
from django.contrib.contenttypes import generic

MONTH_CHOICES = [(i, calendar.month_name[i]) for i in range(1, 13)]


def _display_day(self, type):
    year = '%s_year' % type
    if getattr(self, year):
        display = '%d%s ' % (getattr(self, year),
                  '?' if getattr(self, year + '_uncertain') else '')
    else:
        display = 'year? '

    month = '%s_month' % type
    if getattr(self, month):
        display = '%s%s%s ' % (
          display, calendar.month_name[getattr(self, month)],
          '?' if getattr(self, month + '_uncertain') else '')
    else:
        display += 'month? '

    date = '%s_date' % type
    if getattr(self, date):
        display = '%s%s%s ' % (display, getattr(self, date),
                  '?' if getattr(self, date + '_uncertain') else '')
    else:
        display += 'day? '
    return display


def _display_place(self, type):
    city = '%s_city' % type
    if getattr(self, city):
        display = '%s%s' % (getattr(self, city),
                  '?' if getattr(self, city + '_uncertain') else '')
    else:
        display = ''

    province = '%s_province' % type
    if getattr(self, province):
        if display:
            display += ', '
        display = '%s%s%s' % (display, getattr(self, province),
                  '?' if getattr(self, province + '_uncertain') else '')

    country = '%s_country' % type
    if getattr(self, country):
        if display:
            display += ', '
        display = '%s%s%s' % (display, getattr(self, country),
            '?' if getattr(self, country + '_uncertain') else '')

    if display == '':
        return '?'
    return display


class NameType(models.Model):
    """
    Indicates the various types of names
    Multiple Name types could be checked per name.
    """

    class Meta:
        app_label = 'gcd'
        ordering = ('type',)
        verbose_name_plural = 'Name Types'

    description = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=50, null=True, blank=True)

    def __unicode__(self):
        return '%s' % unicode(self.type)


class CreatorNameDetail(models.Model):
    """
    Indicates the various names of creator
    Multiple Name could be checked per creator.
    """

    class Meta:
        app_label = 'gcd'
        ordering = ['type__id', 'created', '-id']
        verbose_name_plural = 'CreatorName Details'

    name = models.CharField(max_length=255, db_index=True)
    creator = models.ForeignKey('Creator', related_name='creator_names')
    type = models.ForeignKey('NameType', related_name='nametypes', null=True,
                             blank=True)
    #source = models.ManyToManyField('SourceType', related_name='namesources',
                                    #null=True, blank=True)

    # Fields related to change management.
    reserved = models.BooleanField(default=False, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    deleted = models.BooleanField(default=False, db_index=True)

    def active_relations(self):
        return self.to_name.exclude(deleted=True)

    def delete(self):
        self.deleted = True
        self.reserved = False
        self.save()

    def __unicode__(self):
        return '%s - %s(%s)' % (
        unicode(self.creator), unicode(self.name), unicode(self.type.type))


class SourceType(models.Model):
    """
    The data source type for each Name Source should be recorded.
    """

    class Meta:
        app_label = 'gcd'
        ordering = ('type',)
        verbose_name_plural = 'Source Types'

    type = models.CharField(max_length=50)

    def __unicode__(self):
        return unicode(self.type)


class CreatorDataSource(models.Model):
    """
    Indicates the various sources of creator data
    """

    class Meta:
        app_label = 'gcd'
        ordering = ('source_description',)
        verbose_name_plural = 'Creator Data Source'

    source_type = models.ForeignKey(SourceType)
    source_description = models.TextField()
    field = models.CharField(max_length=256)

    # Fields related to change management.
    reserved = models.BooleanField(default=False, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    deleted = models.BooleanField(default=False, db_index=True)

    def delete(self):
        self.deleted = True
        self.reserved = False
        self.save()

    def __unicode__(self):
        return '%s - %s' % (
        unicode(self.field), unicode(self.source_type.type))


class RelationType(models.Model):
    """
    The type of relation between two creators.
    """

    class Meta:
        app_label = 'gcd'
        ordering = ('type',)
        verbose_name_plural = 'Relation Types'

    type = models.CharField(max_length=50)

    def __unicode__(self):
        return unicode(self.type)


class CreatorManager(models.Manager):
    """
    need to be manage creator model
    with this custom manager in future
    """
    pass


class Creator(models.Model):
    class Meta:
        app_label = 'gcd'
        ordering = ('created',)
        verbose_name_plural = 'Creators'

    objects = CreatorManager()

    gcd_official_name = models.CharField(max_length=255, db_index=True)
    birth_year = models.PositiveSmallIntegerField(null=True, blank=True)
    birth_year_uncertain = models.BooleanField(default=False)
    birth_month = models.PositiveSmallIntegerField(choices=MONTH_CHOICES,
                                                   null=True, blank=True)
    birth_month_uncertain = models.BooleanField(default=False)
    birth_date = models.PositiveSmallIntegerField(null=True, blank=True)
    birth_date_uncertain = models.BooleanField(default=False)

    death_year = models.PositiveSmallIntegerField(null=True, blank=True)
    death_year_uncertain = models.BooleanField(default=False)
    death_month = models.PositiveSmallIntegerField(choices=MONTH_CHOICES,
                                                   null=True, blank=True)
    death_month_uncertain = models.BooleanField(default=False)
    death_date = models.PositiveSmallIntegerField(null=True, blank=True)
    death_date_uncertain = models.BooleanField(default=False)

    whos_who = models.URLField(blank=True, null=True)

    birth_country = models.ForeignKey(Country,
                                      related_name='birth_country',
                                      blank=True,
                                      null=True)
    birth_country_uncertain = models.BooleanField(default=False)
    birth_province = models.CharField(max_length=50, blank=True, null=True)
    birth_province_uncertain = models.BooleanField(default=False)
    birth_city = models.CharField(max_length=200, blank=True, null=True)
    birth_city_uncertain = models.BooleanField(default=False)

    death_country = models.ForeignKey(Country,
                                      related_name='death_country',
                                      blank=True,
                                      null=True)
    death_country_uncertain = models.BooleanField(default=False)
    death_province = models.CharField(max_length=50, blank=True, null=True)
    death_province_uncertain = models.BooleanField(default=False)
    death_city = models.CharField(max_length=200, blank=True, null=True)
    death_city_uncertain = models.BooleanField(default=False)

    portrait = generic.GenericRelation(Image)
    schools = models.ManyToManyField('School', related_name='schoolinformation',
                                     through='CreatorSchoolDetail', null=True,
                                     blank=True)
    degrees = models.ManyToManyField('Degree', related_name='degreeinformation',
                                     through='CreatorDegreeDetail', null=True,
                                     blank=True)
    # creators roles
    bio = models.TextField(blank=True, null=True)
    sample_scan = generic.GenericRelation(Image)
    notes = models.TextField(blank=True, null=True)

    data_source = models.ManyToManyField(CreatorDataSource,
                                         blank=True)

    # Fields related to change management.
    reserved = models.BooleanField(default=False, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    deleted = models.BooleanField(default=False, db_index=True)

    def _portrait(self):
        img = Image.objects.filter(object_id=self.id, deleted=False,
                                   content_type=ContentType.objects.get_for_model(
                                       self), type__id=4)
        if img:
            return img.get()
        else:
            return None

    portrait = property(_portrait)

    def _samplescan(self):
        img = Image.objects.filter(object_id=self.id, deleted=False,
                                   content_type=ContentType.objects.get_for_model(
                                       self), type__id=5)
        if img:
            return img.get()
        else:
            return None

    samplescan = property(_samplescan)

    def full_name(self):
        return unicode(self)

    def display_birthday(self):
        return _display_day(self, 'birth')

    def display_birthplace(self):
        return _display_place(self, 'birth')

    def display_deathday(self):
        return _display_day(self, 'death')

    def display_deathplace(self):
        return _display_place(self, 'death')

    def has_death_info(self):
        if self.death_year or self.death_year_uncertain or \
          self.death_month or self.death_month_uncertain or \
          self.death_date or self.death_date_uncertain or \
          self.death_country or self.death_country_uncertain or \
          self.death_city or self.death_city_uncertain or \
          self.death_province or self.death_province_uncertain:
            return True
        else:
            return False

    def deletable(self):
        if self.award_revisions.filter(changeset__state__in=
                                       states.ACTIVE).count():
           return False
        if self.non_comic_work_revisions.filter(changeset__state__in=
                                                states.ACTIVE).count():
           return False
        if self.art_influence_revisions.filter(changeset__state__in=
                                               states.ACTIVE).count():
           return False
        if self.membership_revisions.filter(changeset__state__in=
                                            states.ACTIVE).count():
           return False
        return True

    def pending_deletion(self):
        return self.revisions.filter(changeset__state__in=states.ACTIVE,
                                     deleted=True).count() == 1

    def active_names(self):
        return self.creator_names.exclude(deleted=True)

    def active_memberships(self):
        return self.membership_set.exclude(deleted=True)

    def active_awards(self):
        return self.award_set.exclude(deleted=True)

    def active_artinfluences(self):
        return self.artinfluence_set.exclude(deleted=True)

    def active_noncomicworks(self):
        return self.noncomicwork_set.exclude(deleted=True)

    def get_absolute_url(self):
        return urlresolvers.reverse(
                'show_creator',
                kwargs={'creator_id': self.id})

    def __unicode__(self):
        return '%s' % unicode(self.gcd_official_name)


class NameRelation(models.Model):
    """
    Relations between creators to relate any GCD Official name to any other
    name.
    """

    class Meta:
        app_label = 'gcd'
        ordering = ('gcd_official_name', 'rel_type', 'to_name')
        verbose_name_plural = 'Name Relations'

    gcd_official_name = models.ForeignKey(
            CreatorNameDetail,
            related_name='creator_gcd_official_name')
    to_name = models.ForeignKey(CreatorNameDetail, related_name='to_name')
    rel_type = models.ForeignKey(RelationType, related_name='relation_type',
                                 null=True, blank=True)
    #rel_source = models.ManyToManyField(SourceType, null=True)

    # Fields related to change management.
    reserved = models.BooleanField(default=False, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    deleted = models.BooleanField(default=False, db_index=True)

    def delete(self):
        self.deleted = True
        self.reserved = False
        self.save()

    def __unicode__(self):
        return '%s >Name_Relation< %s :: %s' % (unicode(self.gcd_official_name),
                                                unicode(self.to_name),
                                                unicode(self.rel_type)
                                                )



class School(models.Model):
    """
    record of schools
    """

    class Meta:
        app_label = 'gcd'
        ordering = ('school_name',)
        verbose_name_plural = 'Schools'

    school_name = models.CharField(max_length=200)

    def __unicode__(self):
        return unicode(self.school_name)


class CreatorSchoolDetail(models.Model):
    """
    record the schools creators attended
    """

    class Meta:
        app_label = 'gcd'
        ordering = ('school_year_began', 'school_year_ended')
        verbose_name_plural = 'Creator School Details'

    creator = models.ForeignKey(Creator, related_name='creator_school')
    school = models.ForeignKey(School, related_name='school_details')
    school_year_began = models.PositiveSmallIntegerField(null=True, blank=True)
    school_year_began_uncertain = models.BooleanField(default=False)
    school_year_ended = models.PositiveSmallIntegerField(null=True, blank=True)
    school_year_ended_uncertain = models.BooleanField(default=False)
    #school_source = models.ManyToManyField(SourceType,
                                           #related_name='schoolsource',
                                           #null=True, blank=True)

    # Fields related to change management.
    reserved = models.BooleanField(default=False, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    deleted = models.BooleanField(default=False, db_index=True)

    def delete(self):
        self.deleted = True
        self.reserved = False
        self.save()

    def __unicode__(self):
        return '%s - %s' % (
        unicode(self.creator), unicode(self.school.school_name))


class Degree(models.Model):
    """
    record of degrees
    """

    class Meta:
        app_label = 'gcd'
        ordering = ('degree_name',)
        verbose_name_plural = 'Degrees'

    degree_name = models.CharField(max_length=200)

    def __unicode__(self):
        return unicode(self.degree_name)


class CreatorDegreeDetail(models.Model):
    """
    record the degrees creators received
    """

    class Meta:
        app_label = 'gcd'
        ordering = ('degree_year',)
        verbose_name_plural = 'Creator Degree Details'

    creator = models.ForeignKey(Creator, related_name='creator_degree')
    school = models.ForeignKey(School, related_name='schooldetails', null=True,
                               blank=True)
    degree = models.ForeignKey(Degree, related_name='degreedetails')
    degree_year = models.PositiveSmallIntegerField(null=True, blank=True)
    degree_year_uncertain = models.BooleanField(default=False)

    # Fields related to change management.
    reserved = models.BooleanField(default=False, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    deleted = models.BooleanField(default=False, db_index=True)

    def delete(self):
        self.deleted = True
        self.reserved = False
        self.save()

    def __unicode__(self):
        return '%s - %s' % (
        unicode(self.creator), unicode(self.degree.degree_name))


class ArtInfluence(models.Model):
    """
    record the Name of artistic influences for creators
    """

    class Meta:
        app_label = 'gcd'
        verbose_name_plural = 'Art Influences'

    creator = models.ForeignKey(Creator)
    influence_name = models.CharField(max_length=200)
    # is_influence_exist = models.BooleanField(default=False)
    influence_link = models.ForeignKey(
            Creator,
            null=True,
            blank=True,
            related_name='exist_influencer')
    # self identify docs
    is_self_identify = models.BooleanField(default=False)
    self_identify_influences_doc = models.TextField(blank=True, null=True)
    #influence_source = models.ManyToManyField(SourceType,
                                              #related_name='influencesource',
                                              #null=True, blank=True)

    # Fields related to change management.
    reserved = models.BooleanField(default=False, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    deleted = models.BooleanField(default=False, db_index=True)

    def delete(self):
        self.deleted = True
        self.reserved = False
        self.save()

    def __unicode__(self):
        return unicode(self.influence_name)

    def get_absolute_url(self):
        return urlresolvers.reverse(
                'show_creator_artinfluence',
                kwargs={'creator_artinfluence_id': self.id})

    def deletable(self):
        return True


class MembershipType(models.Model):
    """
    type of Membership
    """

    class Meta:
        app_label = 'gcd'
        verbose_name_plural = 'Membership Types'

    type = models.CharField(max_length=100)

    def __unicode__(self):
        return unicode(self.type)


class Membership(models.Model):
    """
    record societies and other organizations related to their
    artistic profession that creators held memberships in
    """

    class Meta:
        app_label = 'gcd'
        ordering = ('membership_type',)
        verbose_name_plural = 'Memberships'

    creator = models.ForeignKey(Creator)
    organization_name = models.CharField(max_length=200)
    membership_type = models.ForeignKey(MembershipType, null=True, blank=True)
    membership_begin_year = models.PositiveSmallIntegerField(null=True,
                                                             blank=True)
    membership_begin_year_uncertain = models.BooleanField(default=False)
    membership_end_year = models.PositiveSmallIntegerField(null=True,
                                                           blank=True)
    membership_end_year_uncertain = models.BooleanField(default=False)
    #membership_source = models.ManyToManyField(SourceType,
                                               #related_name='membershipsource',
                                               #null=True, blank=True)

    # Fields related to change management.
    reserved = models.BooleanField(default=False, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    deleted = models.BooleanField(default=False, db_index=True)

    def delete(self):
        self.deleted = True
        self.reserved = False
        self.save()

    def __unicode__(self):
        return '%s' % unicode(self.organization_name)

    def get_absolute_url(self):
        return urlresolvers.reverse(
                'show_creator_membership',
                kwargs={'creator_membership_id': self.id})

    def deletable(self):
        return True


class Award(models.Model):
    """
    record any awards and honors a creator received
    """

    class Meta:
        app_label = 'gcd'
        ordering = ('award_year',)
        verbose_name_plural = 'Awards'

    creator = models.ForeignKey(Creator)
    award_name = models.CharField(max_length=255)
    award_year = models.PositiveSmallIntegerField(null=True, blank=True)
    award_year_uncertain = models.BooleanField(default=False)
    #award_source = models.ManyToManyField(SourceType,
                                          #related_name='awardsource', null=True,
                                          #blank=True)

    # Fields related to change management.
    reserved = models.BooleanField(default=False, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    deleted = models.BooleanField(default=False, db_index=True)

    def delete(self):
        self.deleted = True
        self.reserved = False
        self.save()

    def __unicode__(self):
        return unicode(self.award_name)

    def get_absolute_url(self):
        return urlresolvers.reverse(
                'show_creator_award',
                kwargs={'creator_award_id': self.id})

    def deletable(self):
        return True


class NonComicWorkType(models.Model):
    """
    record the type of work performed
    """

    class Meta:
        app_label = 'gcd'
        verbose_name_plural = 'NonComic Work Types'

    type = models.CharField(max_length=100)

    def __unicode__(self):
        return unicode(self.type)


class NonComicWorkRole(models.Model):
    """
    record the type of work performed
    """

    class Meta:
        app_label = 'gcd'
        verbose_name_plural = 'NonComic Work Roles'

    role_name = models.CharField(max_length=200)

    def __unicode__(self):
        return unicode(self.role_name)


class NonComicWork(models.Model):
    """
    record the non-comics work of comics creators
    """

    class Meta:
        app_label = 'gcd'
        ordering = ('publication_title', 'employer_name', 'work_type')
        verbose_name_plural = 'NonComic Works'

    creator = models.ForeignKey(Creator)
    work_type = models.ForeignKey(NonComicWorkType)
    publication_title = models.CharField(max_length=200)
    employer_name = models.CharField(max_length=200, null=True, blank=True)
    work_title = models.CharField(max_length=255, blank=True, null=True)
    work_role = models.ForeignKey(NonComicWorkRole, null=True)
    #work_source = models.ManyToManyField(SourceType, related_name='worksource',
                                         #null=True, blank=True)
    work_notes = models.TextField(blank=True, null=True)

    # Fields related to change management.
    reserved = models.BooleanField(default=False, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    deleted = models.BooleanField(default=False, db_index=True)

    def delete(self):
        self.deleted = True
        self.reserved = False
        self.save()

    def __unicode__(self):
        return '%s' % (unicode(self.publication_title))

    def get_absolute_url(self):
        return urlresolvers.reverse(
                'show_creator_noncomicwork',
                kwargs={'creator_noncomicwork_id': self.id})

    def deletable(self):
        return True


class NonComicWorkYear(models.Model):
    """
    record the year of the work
    There may be multiple years recorded
    """

    class Meta:
        app_label = 'gcd'
        ordering = ('work_year',)
        verbose_name_plural = 'NonComic Work Years'

    non_comic_work = models.ForeignKey(NonComicWork, related_name='noncomicworkyears')
    work_year = models.PositiveSmallIntegerField(null=True, blank=True)
    work_year_uncertain = models.BooleanField(default=False)

    def __unicode__(self):
        return '%s - %s' % (
        unicode(self.non_comic_work), unicode(self.work_year))


class NonComicWorkLink(models.Model):
    """
    record a link to either the work or more information about the work
    """

    class Meta:
        app_label = 'gcd'
        verbose_name_plural = 'NonComic Work Links'

    non_comic_work = models.ForeignKey(NonComicWork, related_name='noncomicworklinks')
    link = models.URLField(max_length=255)

    def __unicode__(self):
        return unicode(self.link)

    def deletable(self):
        return True

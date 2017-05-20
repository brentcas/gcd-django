# -*- coding: utf-8 -*-

from collections import OrderedDict
from django import forms

from apps.oi.models import CreatorRevision, CreatorMembershipRevision, \
                           CreatorAwardRevision, CreatorArtInfluenceRevision, \
                           CreatorNonComicWorkRevision, get_creator_field_list,\
                           CreatorDataSourceRevision, SourceType,\
                           _get_creator_sourced_fields

from .support import (GENERIC_ERROR_MESSAGE, ISSUE_HELP_LINKS,
                      VARIANT_NAME_HELP_TEXT, ISSUE_LABELS, ISSUE_HELP_TEXTS,
                      _set_help_labels, _init_no_isbn, _init_no_barcode,
                      _get_comments_form_field, _clean_keywords,
                      HiddenInputWithHelp, PageCountInput, BrandEmblemSelect)


# TODO add help links as for other forms

def init_data_source_fields(field_name, revision, fields):
    data_source_revision = revision.changeset.creatordatasourcerevisions\
                                             .filter(field=field_name)
    if data_source_revision:
        # TODO we want to be able to support more than one revision
        data_source_revision = data_source_revision[0]
        fields['%s_source_description' % field_name].initial = \
                                    data_source_revision.source_description
        fields['%s_source_type' % field_name].initial = \
                                    data_source_revision.source_type


def get_creator_revision_form(revision=None, user=None):
    class RuntimeCreatorRevisionForm(CreatorRevisionForm):
        def __init__(self, *args, **kwargs):
            super(RuntimeCreatorRevisionForm, self).__init__(*args, **kwargs)
            if revision:
                for field in _get_creator_sourced_fields():
                    init_data_source_fields(field, revision, self.fields)
    return RuntimeCreatorRevisionForm


def insert_data_source_fields(field_name, ordering, fields, insert_after):
    index = ordering.index(insert_after)

    ordering.insert(index+1, '%s_source_description' % field_name)
    fields.update({'%s_source_description' % field_name: forms.CharField(
                                    widget=forms.Textarea, required=False)})

    ordering.insert(index+2, '%s_source_type' % field_name)
    fields.update({'%s_source_type' % field_name: forms.ModelChoiceField(
                        queryset=SourceType.objects.all(), required=False)})


class CreatorRevisionForm(forms.ModelForm):
    class Meta:
        model = CreatorRevision
        fields = get_creator_field_list()

    def __init__(self, *args, **kwargs):
        super(CreatorRevisionForm, self).__init__(*args, **kwargs)
        ordering = self.fields.keys()
        creator_sourced_fields = _get_creator_sourced_fields()
        for field in creator_sourced_fields:
            insert_data_source_fields(field, ordering, self.fields,
                                      creator_sourced_fields[field])
        new_fields = OrderedDict([(f, self.fields[f]) for f in ordering])
        self.fields = new_fields

    comments = _get_comments_form_field()

    def clean(self):
        cd = self.cleaned_data

        if self._errors:
            raise forms.ValidationError(GENERIC_ERROR_MESSAGE)
        for field in _get_creator_sourced_fields():
            data_source_type = cd['%s_source_type' % field]
            data_source_description = cd['%s_source_description' % field]
            if data_source_type or data_source_description:
                if not data_source_type or not data_source_description:
                    self.add_error(
                      '%s_source_description' % field,
                      'Source description and source type must both be set.')


def get_creator_membership_revision_form(revision=None, user=None):
    class RuntimeCreatorMembershipRevisionForm(CreatorMembershipRevisionForm):
        def __init__(self, *args, **kwargs):
            super(RuntimeCreatorMembershipRevisionForm, self)\
                         .__init__(*args, **kwargs)
            #if revision:
                #for field in _get_creator_sourced_fields():
                    #init_data_source_fields(field, revision, self.fields)
    return RuntimeCreatorMembershipRevisionForm


class CreatorMembershipRevisionForm(forms.ModelForm):
    class Meta:
        model = CreatorMembershipRevision
        exclude = ['creator', 'creator_membership', 'changeset', 'deleted',]

    comments = _get_comments_form_field()


def get_creator_award_revision_form(revision=None, user=None):
    class RuntimeCreatorAwardRevisionForm(CreatorAwardRevisionForm):
        def __init__(self, *args, **kwargs):
            super(RuntimeCreatorAwardRevisionForm, self)\
                         .__init__(*args, **kwargs)
            #if revision:
                #for field in _get_creator_sourced_fields():
                    #init_data_source_fields(field, revision, self.fields)
    return RuntimeCreatorAwardRevisionForm


class CreatorAwardRevisionForm(forms.ModelForm):
    class Meta:
        model = CreatorAwardRevision
        exclude = ['creator', 'creator_award','changeset', 'deleted',]

    comments = _get_comments_form_field()


def get_creator_art_influence_revision_form(revision=None, user=None):
    class RuntimeCreatorArtInfluenceRevisionForm(\
                 CreatorArtInfluenceRevisionForm):
        def __init__(self, *args, **kwargs):
            super(RuntimeCreatorArtInfluenceRevisionForm, self)\
                         .__init__(*args, **kwargs)
            #if revision:
                #for field in _get_creator_sourced_fields():
                    #init_data_source_fields(field, revision, self.fields)
    return RuntimeCreatorArtInfluenceRevisionForm


class CreatorArtInfluenceRevisionForm(forms.ModelForm):
    class Meta:
        model = CreatorArtInfluenceRevision
        exclude = ['creator', 'creator_artinfluence','changeset', 'deleted',]

    comments = _get_comments_form_field()


def get_creator_non_comic_work_revision_form(revision=None, user=None):
    class RuntimeCreatorNonComicWorkRevisionForm(\
                 CreatorNonComicWorkRevisionForm):
        def __init__(self, *args, **kwargs):
            super(RuntimeCreatorNonComicWorkRevisionForm, self)\
                         .__init__(*args, **kwargs)
            #if revision:
                #for field in _get_creator_sourced_fields():
                    #init_data_source_fields(field, revision, self.fields)
    return RuntimeCreatorNonComicWorkRevisionForm


class CreatorNonComicWorkRevisionForm(forms.ModelForm):
    class Meta:
        model = CreatorNonComicWorkRevision
        exclude = ['creator', 'creator_noncomicwork','changeset', 'deleted',]

    comments = _get_comments_form_field()

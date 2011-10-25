from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.html import strip_tags
from django.utils.text import truncate_words, truncate_html_words
from django.utils.translation import gettext_lazy as _

from django_markup.fields import MarkupField
from django_markup.markup import formatter
from taggit.managers import TaggableManager


class Category(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = _(u'category')
        verbose_name_plural = _(u'categories')
        ordering = ('title',)

    def __unicode__(self):
        return self.title


class Petal(models.Model):
    """
    A base model for the various content models to inherit from. The name of
    the model participates in the floral theme, each update becoming a petal on
    your beautiful narcissus flower.
    """

    DRAFT = 0
    LIVE = 1
    CLOSED = 2

    STATUS_CHOICES = (
        (DRAFT, _(u'Draft')),
        (LIVE, _(u'Live')),
        (CLOSED, _(u'Closed')),
    )

    status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=LIVE,
        db_index=True,
    )
    author = models.ForeignKey('auth.User', db_index=True)
    category = models.ForeignKey(Category, db_index=True)
    language = models.CharField(
        max_length=5,
        choices=settings.LANGUAGES,
        default=settings.LANGUAGE_CODE,
    )
    slug = models.SlugField(unique_for_date='created_date')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    tags = TaggableManager()

    class Meta:
        verbose_name = _(u'petal')
        verbose_name_plural = _(u'petals')
        ordering = ('-created_date',)


class UpdatePetal(Petal):
    """A simple petal for quick text updates."""

    message = models.CharField(max_length=300)

    def __unicode__(self):
        return truncate_words(self.message, 10)


class ArticlePetal(Petal):
    """A petal for medium to long articles."""

    title = models.CharField(max_length=300)
    content = models.TextField()
    description = models.TextField(blank=True, null=True)
    markup = MarkupField()

    def __unicode__(self):
        return self.title

    @property
    def rendered_content(self):
        return formatter(self.content, filter_name=self.markup)

    @property
    def teaser(self):
        if self.description:
            return formatter(self.description, filter_name=self.markup)
        else:
            return truncate_html_words(self.rendered_content, 75)

    @property
    def word_count(self):
        return len(strip_tags(self.rendered_content))

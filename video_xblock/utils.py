"""
Video xblock helpers.
"""

from collections import namedtuple
import html
from importlib import import_module
from xml.sax.saxutils import unescape
import os.path
import pkg_resources

from django.template import Engine, Context, Template
from xblock.utils.resources import ResourceLoader

from .constants import TranscriptSource

loader = ResourceLoader(__name__)  # pylint: disable=invalid-name


def import_from(module, klass):
    """
    Dynamic equivalent for 'from module import klass'.
    """
    return getattr(import_module(module), klass)


def resource_string(path):
    """
    Handy helper for getting resources from our kit.
    """
    data = pkg_resources.resource_string(__name__, path)
    return data.decode("utf8")


def render_resource(path, **context):
    """
    Render static resource using provided context.

    Returns: django.utils.safestring.SafeText
    """
    html_template = Template(resource_string(path))
    return html.unescape(
        html_template.render(Context(context))
    )


def render_template(template_name, **context):
    """
    Render static resource using provided context.

    Returns: django.utils.safestring.SafeText
    """
    template_dirs = [os.path.join(os.path.dirname(__file__), 'static/html')]
    libraries = {'video_xblock_tags': 'video_xblock.templatetags'}
    engine = Engine(dirs=template_dirs, debug=True, libraries=libraries)
    html_template = engine.get_template(template_name)

    return html.unescape(
        html_template.render(Context(context))
    )


def ugettext(text):
    """
    Dummy ugettext method that doesn't do anything.
    """
    return text


def underscore_to_mixedcase(value):
    """
    Convert variables with under_score to mixedCase style.
    """
    def mixedcase():
        """Mixedcase generator."""
        yield str.lower
        while True:
            yield str.capitalize

    mix = mixedcase()
    return "".join(next(mix)(x) if x else '_' for x in value.split("_"))


def remove_escaping(text):
    """
    Clean text from special `escape` symbols.

    Reference: https://wiki.python.org/moin/EscapingHtml.
    """
    html_unescape_table = {
        "&amp;": "&",
        "&quot;": '"',
        "&amp;#39;": "'",
        "&apos;": "'",
        "&gt;": ">",
        "&lt;": "<"
    }
    if isinstance(text, bytes):
        text = text.decode()
    return unescape(text, html_unescape_table)


def create_reference_name(lang_label, video_id, source="default"):
    """
    Build transcript file reference based on input information.

    Format is <language label>_<source>_captions_video_<video_id>, e.g. "English_default_captions_video_456g68"
    """
    reference = "{lang_label}_{source}_captions_video_{video_id}".format(
        lang_label=lang_label,
        video_id=video_id,
        source=source,
    )
    return reference


def filter_transcripts_by_source(transcripts, sources=None, exclude=False):
    """
    Filter given transcripts by source attribute.

    Extra `exclude` flag switches filter in opposite (exclusive) mode.

    Arguments:
        transcripts (list, generator): transcripts to be filtered.
        sources (list): TranscriptSources filters.
        exclude (bool): Type of filtering.
    Returns:
        filtered transcripts (list, generator): only those transcript dicts which met the filter condition.
    """
    if sources is None:
        sources = [TranscriptSource.DEFAULT]
    if not transcripts:
        return transcripts
    if exclude:
        return (tr for tr in transcripts if tr['source'] not in sources)
    return (tr for tr in transcripts if tr['source'] in sources)


def normalize_transcripts(transcripts):
    """
    Add to manually uploaded transcripts "source" attribute.
    """
    for tr_dict in transcripts:
        tr_dict.setdefault('source', TranscriptSource.MANUAL)
    return transcripts


Transcript = namedtuple('Transcript', [
    'id', 'label', 'lang', 'lang_id', 'content', 'format', 'video_id', 'source', 'url'
])

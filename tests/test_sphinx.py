# This file is part of rinohtype, the Python document preparation system.
#
# Copyright (c) Brecht Machiels.
#
# Use of this source code is subject to the terms of the GNU Affero General
# Public License v3. See the LICENSE file or http://www.gnu.org/licenses/.


import pytest

from sphinx.application import Sphinx

from rinoh.document import DocumentTree
from rinoh.frontend.sphinx import template_from_config
from rinoh.language import IT
from rinoh.paper import A4, LETTER
from rinoh.templates import Book, Article


def create_sphinx_app(tmpdir, **confoverrides):
    return Sphinx(srcdir=tmpdir.strpath,
                  confdir=None,
                  outdir=(tmpdir / 'output').strpath,
                  doctreedir=(tmpdir / 'doctrees').strpath,
                  buildername='rinoh',
                  # confoverrides=dict(extensions=['rinoh.frontend.sphinx'],
                  #                    **confoverrides))
                  confoverrides=confoverrides)


CONFIG_DIR = 'confdir'


def get_contents_page_size(template_configuration):
    doctree = DocumentTree([])
    doc = template_configuration.document(doctree)
    part_template = doc.part_templates[2]
    part = part_template.document_part(doc)
    assert part.template_name == 'contents'
    page = part.new_page(1, new_chapter=False)
    return page.get_config_value('page_size', doc)


def test_sphinx_config_default(tmpdir):
    app = create_sphinx_app(tmpdir)
    template_cfg = template_from_config(app.config, CONFIG_DIR, print)
    assert template_cfg.template == Book
    assert not template_cfg.keys()
    assert template_cfg.variables.keys() == set(['paper_size'])
    assert get_contents_page_size(template_cfg) == LETTER


def test_sphinx_config_latex_elements_papersize(tmpdir):
    app = create_sphinx_app(tmpdir, latex_elements=dict(papersize='a4paper'))
    template_cfg = template_from_config(app.config, CONFIG_DIR, print)
    assert template_cfg.template == Book
    assert not template_cfg.keys()
    assert template_cfg.variables.keys() == set(['paper_size'])
    assert get_contents_page_size(template_cfg) == A4


def test_sphinx_config_rinoh_paper_size(tmpdir):
    app = create_sphinx_app(tmpdir, rinoh_paper_size=A4,
                            latex_elements=dict(papersize='a4paper'))
    template_cfg = template_from_config(app.config, CONFIG_DIR, print)
    assert template_cfg.template == Book
    assert not template_cfg.keys()
    assert template_cfg.variables.keys() == set(['paper_size'])
    assert get_contents_page_size(template_cfg) == A4


def test_sphinx_config_language(tmpdir):
    app = create_sphinx_app(tmpdir, language='it')
    template_cfg = template_from_config(app.config, CONFIG_DIR, print)
    assert template_cfg.template == Book
    assert template_cfg['language'] == IT


def test_sphinx_config_builtin_stylesheet(tmpdir):
    app = create_sphinx_app(tmpdir, rinoh_stylesheet='sphinx_base14')
    template_cfg = template_from_config(app.config, CONFIG_DIR, print)
    assert template_cfg.template == Book
    assert template_cfg['stylesheet'].name == 'Sphinx (PDF Core Fonts)'


def test_sphinx_config_pygments_style(tmpdir):
    app = create_sphinx_app(tmpdir, pygments_style='igor')
    template_cfg = template_from_config(app.config, CONFIG_DIR, print)
    assert template_cfg.template == Book
    assert template_cfg['stylesheet'].base is not None


def test_sphinx_config_rinoh_template(tmpdir):
    template_cfg = Article.Configuration('test',
                                         stylesheet='sphinx_article')
    app = create_sphinx_app(tmpdir, rinoh_template=template_cfg)
    template_cfg = template_from_config(app.config, CONFIG_DIR, print)
    assert template_cfg.template == Article
    assert (template_cfg.get_attribute_value('stylesheet').name
                == 'Sphinx (article)')


def test_sphinx_config_rinoh_template_from_entrypoint(tmpdir):
    app = create_sphinx_app(tmpdir, rinoh_template='book')
    template_cfg = template_from_config(app.config, CONFIG_DIR, print)
    assert not template_cfg.keys()
    assert template_cfg.template == Book
    assert template_cfg.get_attribute_value('stylesheet').name == 'Sphinx'


def test_sphinx_config_rinoh_template_from_filename(tmpdir):
    template_cfg_path = tmpdir.join('template_cfg.rtt').strpath
    with open(template_cfg_path, 'w') as template_cfg:
        print('[TEMPLATE_CONFIGURATION]', file=template_cfg)
        print('template = book', file=template_cfg)
    app = create_sphinx_app(tmpdir, rinoh_template=template_cfg_path)
    template_cfg = template_from_config(app.config, CONFIG_DIR, print)
    assert not template_cfg.keys()
    assert template_cfg.template == Book
    assert template_cfg.get_attribute_value('stylesheet').name == 'Sphinx'

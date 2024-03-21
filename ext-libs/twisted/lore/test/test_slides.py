# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for L{twisted.lore.slides}.
"""

import xml.dom.minidom

from twisted.trial.unittest import TestCase
from twisted.lore.slides import HTMLSlide, splitIntoSlides, insertPrevNextLinks


class SlidesTests(TestCase):
    """
    Tests for functions in L{twisted.lore.slides}.
    """
    def test_splitIntoSlides(self):
        """
        L{splitIntoSlides} accepts a document and returns a list of two-tuples,
        each element of which contains the title of a slide taken from an I{h2}
        element and the body of that slide.
        """
        document = xml.dom.minidom.Document()
        body = document.createElement('body')
        document.appendChild(body)

        first_slide_title = document.createElement('h2')
        first_slide_title_text = document.createTextNode('first slide')
        first_slide_title.appendChild(first_slide_title_text)
        body.appendChild(first_slide_title)
        body.appendChild(document.createElement('div'))
        body.appendChild(document.createElement('span'))

        second_slide_title = document.createElement('h2')
        second_slide_title_text = document.createTextNode('second slide')
        second_slide_title.appendChild(second_slide_title_text)
        body.appendChild(second_slide_title)
        body.appendChild(document.createElement('p'))
        body.appendChild(document.createElement('br'))

        slides = splitIntoSlides(document)

        self.assertEqual(slides[0][0].data, 'first slide')
        first_slide_content = slides[0][1]
        self.assertEqual(first_slide_content[0].tagName, 'div')
        self.assertEqual(first_slide_content[1].tagName, 'span')
        self.assertEqual(len(first_slide_content), 2)

        self.assertEqual(slides[1][0].data, 'second slide')
        second_slide_content = slides[1][1]
        self.assertEqual(second_slide_content[0].tagName, 'p')
        self.assertEqual(second_slide_content[1].tagName, 'br')
        self.assertEqual(len(second_slide_content), 2)

        self.assertEqual(len(slides), 2)


    def test_insertPrevNextText(self):
        """
        L{insertPrevNextLinks} appends a text node with the title of the
        previous slide to each node with a I{previous} class and the title of
        the next slide to each node with a I{next} class.
        """
        next_element = self.document.createElement('span')
        next_element.setAttribute('class', 'next')
        container = self.document.createElement('div')
        container.appendChild(next_element)
        slide_with_next = HTMLSlide(container, 'first', 0)

        previous_element = self.document.createElement('span')
        previous_element.setAttribute('class', 'previous')
        container = self.document.createElement('div')
        container.appendChild(previous_element)
        slide_with_previous = HTMLSlide(container, 'second', 1)

        insertPrevNextLinks(
            [slide_with_next, slide_with_previous], None, None)

        self.assertEqual(
            next_element.toxml(), '<span class="next">second</span>')
        self.assertEqual(
            previous_element.toxml(), '<span class="previous">first</span>')


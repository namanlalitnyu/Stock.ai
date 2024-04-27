import PyPDF2
from pdfminer.high_level import extract_pages, extract_text
from pdfminer.layout import LTTextContainer, LTChar, LTRect, LTFigure
import os
import pickle

def text_extraction(element):
    line_text = element.get_text()

    line_formats = []
    font_size = []
    upright = True;
    fontname = "empty"

    for text_line in element:
        if isinstance(text_line, LTTextContainer):
            for character in text_line:
                if isinstance(character, LTChar):
                    line_formats.append(character.size)
                    font_size.append(character.size);
                    upright = upright and character.upright
                    fontname = character.fontname

    format_per_line = sorted(line_formats, key=float, reverse=True)
    return (line_text, format_per_line, font_size, upright, fontname)

def get_titles(start_doc, end_doc):
  titles = []
  for i in range(start_doc, end_doc + 1):
    print(i)
    max_score = -1
    pages = list(enumerate(extract_pages("../lenrDataset/" + str(i) + ".pdf")))
    front_page = pages[0][1]
    for element in front_page:
      if isinstance(element, LTTextContainer):
        (text, format, font_size, upright, fn) = text_extraction(element)

        # calculating score using average fontsize + is_bold(10pts)
        fact = 0
        if "Bold" in fn:
          fact = 10
        if len(font_size) > 0:
          score = sum(font_size)/len(font_size) + fact

        # calculating max, and storing title
        if upright == True and len(font_size) > 0 and max_score < score and len(text) > 25:
          title = text
          max_score = score
        elif upright == True and len(font_size) > 0 and max_score == score and len(text) > 25:
          title = title + text
    titles.append(title)

  return titles

# Find the start element from where the Abstract starts
def get_abstract_start_element(pageElements, start_detectors):

  for elementId, element in pageElements:
    if isinstance(element, LTTextContainer):
      line_text = element.get_text()
      if any(substring in line_text for substring in start_detectors):
        # If 'Abstract' heading is a separate element, ignore it
        # Else, include it in the abstract text
        residue = line_text
        for detector in start_detectors:
          residue = residue.replace(detector, '')
        return elementId + 1 if len(residue) < 5 else elementId

  return -1


def get_abstract_end_element(pageElements, start, end_detectors):
  has_content = False

  for elementId, element in pageElements[start:]:
    if isinstance(element, LTTextContainer):
      line_text = element.get_text().lower()
      if has_content and any(substring in line_text for substring in end_detectors):
        return elementId
      if len(line_text) > 10:
        has_content = True

  return -1


def get_abstract_elements_range(pageElements):
  start = -1
  end = -1
  start_detectors = ('Abstract', 'ABSTRACT')
  end_detectors = ('introduction', '_lntrnd_uctio_n', 'All rights reserved.')

  start = get_abstract_start_element(pageElements, start_detectors)

  if start == -1:
    return (start, end)

  end = get_abstract_end_element(pageElements, start, end_detectors)

  # check for end element
  if end == -1:
    end = get_abstract_end_element(pageElements, start, ('keywords:', 'key words:'))

  # last text element is end
  if end == -1:
    for elementId, element in pageElements[start:]:
      if isinstance(element, LTTextContainer):
        line_text = element.get_text()
        end = elementId

  return (start, end)


def get_abstracts(start_doc, end_doc):
  abstracts = []
  for i in range(start_doc, end_doc + 1):
    print(i)
    pages = list(enumerate(extract_pages('../lenrDataset/' + str(i) + '.pdf')))
    frontPage = pages[0][1]
    elements = list(enumerate(frontPage))
    abstractRange = get_abstract_elements_range(elements)
    abstract = ""
    for j in range(abstractRange[0], abstractRange[1]):
      if isinstance(elements[j][1], LTTextContainer) and len(elements[j][1].get_text()) > 10:
        abstract += elements[j][1].get_text()

    abstracts.append(abstract)

  return abstracts

print("getting titles....")
titles = get_titles(1, 40)

print("getting abstracts....")
abstracts = get_abstracts(1, 40)

data = titles + abstracts
print("pickling....")
# Pickle the list
with open('data.pkl', 'wb') as file:
    pickle.dump(data, file)

with open('titles.pkl', 'wb') as file:
    pickle.dump(titles, file)

with open('abstracts.pkl', 'wb') as file:
    pickle.dump(abstracts, file)

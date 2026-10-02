import docx
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

doc = docx.Document()

# Set title, authors, and abstract (Single Column)
doc.add_heading('Fake News Detection Using Machine Learning', level=0)
doc.add_paragraph('Sushma V, Abdul Razak A S, Mohammed Hussain Chand, Shashank K H, Thejus S G')
doc.add_paragraph('Department of Computer Science and Engineering, ATME College of Engineering, Mysuru, India\n')

# Insert Section / Column Break to make body text 2 columns
section = doc.add_section(docx.enum.section.WD_SECTION.NEW_PAGE)
sectPr = section._sectPr
cols = OxmlElement('w:cols')
cols.set(qn('w:num'), '2')  # Sets columns to 2
cols.set(qn('w:space'), '720') # Space between columns
sectPr.append(cols)

# Add sample body content
doc.add_heading('I. INTRODUCTION', level=1)
doc.add_paragraph('The rapid migration of news publishing to digital networks has altered how society consumes information...')

doc.save('Fake_News_Detection_IEEE_TwoColumn.docx')
print("File successfully created!")
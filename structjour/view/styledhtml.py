# Structjour -- a daily trade review helper
# Copyright (C) 2019 Zero Substance Trading
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.


'''
Created on Apr 17, 2019

@author: Mike Petersen
'''


class StyledHTML:
    '''
    A template for styled html-no external file. Currently-it turned into specific.
    See if I can make it general.
    '''
    def __init__(self, style, body, replacementList):
        '''Initialze with all the elements needed
        :params style: The css
        :params body: The html between the body tags (not including<body>)
        :params replacementList: An orderd list of the format replacements for '{0}'.format type replacemnet
        '''
        self.style = style
        self.body = body
        self.repl = replacementList

    def makehtml(self):
        '''
        Create the file
        '''
        front = '''<!DOCTYPE HTML> <html> <head> <meta charset="utf-8"> <style type="text/css">'''
        front2 = '''</style> </head> <body>'''
        end = '''</body> </html>'''

        html = self.body.format(*self.repl)
        html = front + self.style + front2 + html + end
        return html


if __name__ == '__main__':
    s = '''
    p,li { white-space: pre-wrap; }
    h3 { margin-top: 6px; margin-bottom: 12px; margin-left: 0px; margin-right: 0px; text-indent: 0px; }
    body { font-family: Arial, Helvetica, sans-serif; font-size: 7.8pt; font-weight: 400; font-style: normal; }
    .large { font-size: large; font-weight: 600; }
    .blue { font-size: large; font-weight: 600; color: #0000ff; }
    .red { font-weight: 600; color: #aa0000; }
    .green { font-weight: 600; color: #00ff00; }
    .explain { margin-top: 12px; margin-bottom: 12px; margin-left: 0px; margin-right: 0px; text-indent: 10px; }
    ul { margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; }
    li { font-size: 8pt; margin-top: 12px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; text-indent: 0px; }
    .li2 { margin-top: 0px; } .li3 { margin-top: 0px; margin-bottom: 12px; }
    '''
    repl = ['AMD', '550', '100', '650']
    b = '''<h3> <div class="large"> <p>Unbalanced shares of {0} for<span class="blue"> {1} </span>shares</p> </div> </h3> <p class="explain"> Adjust the
    shares held before and after this statement to bring the unbalanced shares to 0. Solutions might look like one of the following</p> <ul> <li> <span class="red">{2}    # noqa: E501
    </span>shares held before and 0 shares held after</li> <li> 0 shares held before and<span class="green"> {1} </span>shares held after</li> <li> <span class="green">{3}
    </span>shares held before and<span class="green"> {4}.</span> shares held after</li> </ul>'''

    s = StyledHTML(s, b, repl)
    s2 = s.makehtml()
    print(s2)

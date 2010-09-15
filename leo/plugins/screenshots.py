#@+leo-ver=5-thin
#@+node:ekr.20100908110845.5505: * @thin screenshots.py
#@+<< docstring >>
#@+node:ekr.20100908115707.5554: ** << docstring >>
"""screenshots.py: a plugin to take screen shots using Inkscape
============================================================

Inkscape, http://inkscape.org/, is an Open
Source vector graphics editor, with
capabilities similar to Illustrator,
CorelDraw, or Xara X, using the SVG (Scalable
Vector Graphics) file format. See
http://www.w3.org/Graphics/SVG/.

Leo scripts can control Inkscape using the
c.inkscapeCommands.run method (run for
short), a method of the LeoInkscapeCommands
class defined in leoRst.py.

The primary input to the run method is the
**screeshot file**. This must be a bitmap.
Typically the screenshot file will be a PNG
format file, though other kinds of bitmap
files should work. The user, or perhaps
another script, must generate the screenshot
file before calling run().

The run method works in three stages:

1. Convert the screenshot (bitmap) file to
   the **working file**. The working file is
   a SVG (vector graphic) file. Besides the
   image from the original screenshot, the
   working file may contain text **callouts**
   (text ballons) and **markers** (black
   circles containing numbers). You specify
   callouts and markers using arguments to
   the run method.

2. (Optional) Edit the working file using
   Inkscape. Inkscape will appear on the
   screen. You can edit and position callouts
   and markers, then save the working file.

3. (Optional) Use Inkscape behind the scenes
   to render a final PNG image from the
   working file.  If PIL is installed, this
   step adjusts the image in various subtle
   ways.

Prerequisites
-------------

Inkscape
  The SVG editor, from http://www.inkscape.org/

PIL
  The Python Imaging Library,
  http://www.pythonware.com/products/pil/

  Optional but highly recommended. If present,
  PIL will improve the quality of the generated
  images.

Settings
--------

@string inkscape-bin

This setting tells Leo the location of the Inkscape executable.

Usage
-----

The run method has the following signature::

    def run (self,fn,
        callouts=[],
        markers=[],
        png_fn=None,svg_fn=None,template_fn=None)

        fn  The name of the bitmap screenshot file.
  callouts  A possibly empty list of strings.
   markers  A possibly empty list of numbers.
    png_fn  The name of final png image file.
            No image is generated if this argument is None.
    svg_fn  The name of working svg file.
            If no name is given, ``working_file.svg`` is used.
 template_fn The name of the **template svg file**.
            This file contains images to be used for
            callouts and markers.  If no name is given,
            inkscape-template.svg is used.

For example, the following places three text
balloon callouts and three black circle
numeric markers on a screenshot::

    fn = "some_screen_shot.png"
    png_fn = "final_screen_shot.png"
    callouts = (
        "This goes here",
        "These are those, but slightly longer",
        "Then you pull this")
    markers = (2,4,17)

    c.inkscapeCommands.run(fn,
        callouts=callouts,markers=markers,
        png_fn=png_fn)

"""
#@-<< docstring >>

__version__ = '0.1'

#@+<< imports >>
#@+node:ekr.20100908110845.5604: ** << imports >>
import leo.core.leoGlobals as g

import copy
import os

# Warnings are given later.
try:
    from PIL import Image, ImageChops
    got_pil = True
except ImportError:
    got_pil = False

try:
    from PyQt4.QtGui import QImage
    got_qt = True
except ImportError:
    got_qt = False

import subprocess
import sys
import tempfile

import xml.etree.ElementTree as etree
#@-<< imports >>

#@+others
#@+node:ekr.20100914090933.5771: ** Top level
#@+node:ekr.20100908110845.5581: *3* g.command(apropos-screen-shots)
#@@pagewidth 45

# Ideally, we would compute s from the module's docstring,
# but there are problems doing so, so we just cut/paste.

@g.command('apropos-screen-shots')
def apropos_screen_shots(event):

    c = event.get('c')
    if not c: return

    #@+<< define s >>
    #@+node:ekr.20100908110845.5582: *4* << define s >>
    s = """\

    The screenshot.py plug
    ======================

    This plugin uses the Qt gui to take scree
    shots, and optionally uses Inkscape to edit
    those screen shots.

    Inkscape, http://inkscape.org/, is an Open
    Source vector graphics editor, with
    capabilities similar to Illustrator,
    CorelDraw, or Xara X, using the SVG (Scalable
    Vector Graphics) file format. See
    http://www.w3.org/Graphics/SVG/.

    The plugin defines the take-screen-shot command.
    This command works in four stages:

    1. Take a bitmap (PNG) **screenshot** file using Qt.

       Discuss:
           - Name of file
           - Screen nodes & their descendants.


    2. Convert the screenshot file to a working file.

       The **working file** is a SVG (vector
       graphic) file. Besides the image from the
       original screenshot, the working file may
       contain text **callouts** (text ballons)
       and **markers** (black circles containing
       numbers). You specify callouts and markers
       using arguments to the run method.

    3. (Optional) Edit the working file using
       Inkscape. Inkscape will appear on the
       screen. You can edit and position callouts
       and markers, then save the working file.

       Discuss: @callout and @marker nodes.

    4. (Optional) Create an output (PNG) file
       from the working file.

    Use Inkscape behind the scenes
       to render a final PNG image from the
       working file.  If PIL is installed, this
       step adjusts the image in various subtle
       ways.

    Prerequisites
    -------------

    Inkscape
      The SVG editor, from http://www.inkscape.org/

    PIL
      The Python Imaging Library,
      http://www.pythonware.com/products/pil/

      Optional but highly recommended. If present,
      PIL will improve the quality of the generated
      images.

    Settings
    --------

    @string inkscape-bin

    This setting tells Leo the location of the
    Inkscape executable.

    Scripting the plugin
    --------------------

    Leo scripts can control this plugin using the
    run method of the plugin's
    ScreenShotController class.  Like this::

        import leo.plugins.screenshots as screenshots
        sc = screenshots.ScreenShotController(c)
        sc.run(<arguments>)

    The run method has the following signature::

        def run (self,
            p, # The slide node,
            callouts=[], # A possibly empty list of strings.
            markers=[], # A possibly empty list of numbers.
            template_fn=None)

    Notes:

    - The slide node must be a direct child of an
      @screenshot node.

    - template_fn is the name of a template file
      containing images to be used for callouts
      and markers. The default is
      inkscape-template.svg.

    For example, the following places three text
    balloon callouts and three black circle
    numeric markers on a screenshot::

        import leo.plugins.screenshots as screenshots
        sc = screenshots.ScreenShotController(c)
        sc.run(
            fn = "some_screen_shot.png"
            png_fn = "final_screen_shot.png"
            callouts = (
                "This goes here",
                "These are those, but slightly longer",
                "Then you pull this",
            )
            markers = (2,4,17))

    """
    #@-<< define s >>

    g.es(g.adjustTripleString(s.rstrip(),c.tab_width))
#@+node:ekr.20100911044508.5634: *3* g.command(make-slide-show)
@g.command('make-slide-show')
def make_slide_show_command(event=None):

    c = event.get('c')
    if c:
        sc = ScreenShotController(c)
        sc.make_slide_show_command(c.p)
        g.note('make-slide-show command finished')
#@+node:ekr.20100908110845.5583: *3* g.command(take_screen_shot)
@g.command('take-screen-shot')
def take_screen_shot_command (event):

    c = event.get('c')
    if c:
        sc = ScreenShotController(c)
        sc.take_screen_shot_command(c.p)
        g.note('take-screen-shot command finished')
#@+node:ekr.20100908110845.5606: *3* init
def init ():

    ok = got_qt

    if ok:
        g.plugin_signon(__name__)

    return ok
#@+node:ekr.20100914090933.5770: *3* make_screen_shot
def make_screen_shot (path):

    '''Create a screenshot of the present Leo outline and save it to path.
    This is a callback called from make_screen_shot in runLeo.py'''

    # g.trace('screenshots.py:',path)

    try:
        import PyQt4.QtGui
        app = g.app.gui.qtApp
        pix = PyQt4.QtGui.QPixmap
    except ImportError:
        g.error('make_screen_shot requires PyQt4')
        return

    w = pix.grabWindow(app.activeWindow().winId())
    w.save(path,'png')
#@+node:ekr.20100908110845.5531: ** class ScreenShotController
class ScreenShotController(object):

    '''A class to take screen shots and control Inkscape.

    apropos-screenshots contains a more complete description.'''

    #@+others
    #@+node:ekr.20100908110845.5532: *3*  ctor & helpers
    def __init__(self,c):

        self.c = c

        # Debugging, especially paths.
        self.trace = False

        # The path to the Inkscape executable.
        self.inkscape_bin = self.get_inkscape_bin()

        # Standard screenshot size
        self.default_screenshot_height = 1000
        self.default_screenshot_width = 800
        self.screenshot_height = None
        self.screenshot_width = None

        # The @slideshow node.
        self.slide_show_node = None

        # Dimension cache.
        self.dimCache = {}
        self.is_reads,self.is_cache = 0,0

        # Internal constants.
        # element IDs which should exist in the SVG template
        self.ids = [
            "co_bc_1",        # 1 digit black circle
            "co_bc_2",        # 2 digit black circle
            "co_bc_text_1",   # text holder for 1 digit black circle
            "co_bc_text_2",   # text holder for 2 digit black circle
            "co_frame",       # frame for speech balloon callout
            "co_g_bc_1",      # group for 1 digit black circle
            "co_g_bc_2",      # group for 2 digit black circle
            "co_g_co",        # group for speech balloon callout
            "co_shot",        # image for screen shot
            "co_text_holder", # text holder for speech balloon callout
        ]

        self.xlink = "{http://www.w3.org/1999/xlink}"
        # self.namespace = {'svg': "http://www.w3.org/2000/svg"}
    #@+node:ekr.20100913085058.5657: *4* get_inkscape_bin
    def get_inkscape_bin(self):

        c = self.c
        bin = c.config.getString('screenshot-bin').strip('"').strip("'")

        if bin:
            if g.os_path_exists(bin):
                self.inkscape_bin = bin
            else:
                g.warning('Invalid @string screenshot-bin:',bin)

        if not bin:
            g.warning('Inkscape not found. No editing is possible.')

        return bin
    #@+node:ekr.20100908110845.5533: *3* lxml replacements
    #@+node:ekr.20100908110845.5534: *4* getElementsWithAttrib
    def getElementsWithAttrib (self,e,attr_name,aList=None):

        if aList is None: aList = []

        val = e.attrib.get(attr_name)
        if val: aList.append(e)

        for child in e.getchildren():
            self.getElementsWithAttrib(child,attr_name,aList)

        return aList
    #@+node:ekr.20100908110845.5535: *4* getElementsWithAttribList (not used)
    def getElementsWithAttribList (self,e,attr_names,aList=None):

        if aList is None: aList = []

        for z in attr_names:
            if not e.attrib.get(z):
                break
        else:
            aList.append(e)

        for child in e.getchildren():
            self.getElementsWithAttribList(child,attr_names,aList)

        return aList
    #@+node:ekr.20100908110845.5536: *4* getIds
    def getIds (self,e,d=None):

        '''Return a dict d. Keys are ids, values are elements.'''

        aList = self.getElementsWithAttrib(e,'id')
        return dict([(e.attrib.get('id'),e) for e in aList])
    #@+node:ekr.20100908110845.5537: *4* getParents
    def getParents (self,e,d=None):

        if d is None:
            d = {}
            d[e] = None

        for child in e.getchildren():
            d[child] = e
            self.getParents(child,d)

        return d
    #@+node:ekr.20100911044508.5629: *3* file names
    # These methods compute file names using settings or options if given,
    # or various defaults if no setting or option is in effect.
    #@+node:ekr.20100908110845.5540: *4* finalize
    def finalize (self,fn,base_path=None):

        '''Return the absolute path to fn in the screenshot folder.'''

        if base_path:
            s = g.os_path_finalize_join(base_path,fn)
        else:
            s = g.os_path_finalize_join(g.app.loadDir,
                '..','doc','html','screen-shots',fn)

        return s.replace('\\','/')
    #@+node:ekr.20100911044508.5632: *4* fix
    def fix (self,fn):

        '''Fix the case of a file name,
        especially on Windows the case of drive letters.'''

        return os.path.normcase(g.os_path_finalize(fn))
    #@+node:ekr.20100911044508.5631: *4* get_at_image_fn
    def get_at_image_fn (self,screenshot_fn):

        '''Return the screenshot name relative to g.app.loadDir.

        @image directives (screenshot_fn) are relative to g.app.loadDir.
        The final path is g.os_path_finalize_join(g.app.loadDir,s)
        '''

        base = self.fix(g.os_path_finalize(g.app.loadDir))
        fn = self.fix(screenshot_fn)
        fn = os.path.relpath(fn,base).replace('\\','/')
        if self.trace: g.trace(fn)
        return fn
    #@+node:ekr.20100909121239.5669: *4* get_directive_fn
    def get_directive_fn (self,p,sphinx_path,screenshot_fn):

        '''Compute the path for use in an .. image:: directive.

        This is screenshot_fn relative to sphinx_path.
        By default this is leo/docs/html.

        sphinx_path and screenshot_fn are absolute file names.
        '''

        base = self.fix(sphinx_path) # ,'screen-shots'))
        fn = self.fix(screenshot_fn)
        fn = os.path.relpath(fn,base).replace('\\','/')
        if self.trace: g.trace(fn)
        return fn
    #@+node:ekr.20100911044508.5638: *4* p_to_fn
    def p_to_fn (self,p,ext):

        '''Return a unique, sanitized filename corresponding to p,
        having the form root.h-n.ext, where root is the @slideshow node
        and n is the index of the slide in the slideshow.
        '''

        sc = self
        n = sc.get_slide_number(p)
        h = sc.slide_show_node.h

        tag = '@slideshow'
        assert g.match_word(h,0,tag)
        h = h[len(tag):].strip()
        if not h:
            # g.trace('*** no h: using gnx',repr(p.gnx))
            h = p.gnx

        s = '%s-%03d.%s' % (sc.sanitize(h),n,ext)
        g.trace(repr(s))
        return s
    #@+node:ekr.20100911044508.5627: *4* get_output_fn
    def get_output_fn (self,p):

        '''Return the full, absolute, output file name.

        An empty filename disables output.

        The default is h-n.png, where h is the @slideshow nodes's sanitized headline.
        '''

        # Look for any @output nodes in p's children.
        tag = '@output'
        for child in p.children():
            h = child.h
            if g.match_word(h,0,tag):
                fn = h[len(tag):].strip()
        else:
            fn = self.p_to_fn(p,'png')

        g.trace(repr(fn))
        fn = self.finalize(fn)
        if self.trace: g.trace(fn)
        return fn
    #@+node:ekr.20100911044508.5628: *4* get_screenshot_fn
    def get_screenshot_fn (self,p,screenshot_fn):

        '''Return the full, absolute, screenshot file name.'''

        fn = screenshot_fn or self.p_to_fn(p,'png')
        fn = self.finalize(fn)
        if self.trace: g.trace(fn)
        return fn
    #@+node:ekr.20100911044508.5633: *4* get_sphinx_path
    def get_sphinx_path (self,sphinx_path):

        '''Return the full, absolute, path to the sphinx directory.

        By default this will be the leo/doc/html directory.

        If a relative path is given, it will resolved
        relative to the directory containing the .leo file.
        '''

        c = self.c

        if sphinx_path:
            if g.os_path_isabs(sphinx_path):
                path = sphinx_path
            else:
                # The path is relative to the .leo file
                leo_fn = c.fileName()
                if not leo_fn:
                    g.error('relative sphinx path given but outline not named')
                    return None
                leo_fn = g.os_path_finalize_join(g.app.loadDir,leo_fn)
                base,junk = g.os_path_split(leo_fn)
                path = g.os_path_finalize_join(base,sphinx_path)
        else:
            # The default is the leo/doc/html directory.
            path = g.os_path_finalize_join(g.app.loadDir,'..','doc','html')

        path = path.replace('\\','/')
        if self.trace: g.trace(path)
        return path
    #@+node:ekr.20100908110845.5542: *4* get_template_fn
    def get_template_fn (self,template_fn=None):

        '''Return the full, absolute, template file name.'''

        c = self.c

        if template_fn:
            fn = g.os_path_finalize(template_fn)
        else:
            fn = g.os_path_finalize_join(g.app.loadDir,
                '..','doc','inkscape-template.svg')

        if g.os_path_exists(fn):
            if self.trace: g.trace(fn)
            return fn
        else:
            g.error('template file not found:',fn)
            return None
    #@+node:ekr.20100911044508.5626: *4* get_working_fn
    def get_working_fn (self,p,working_fn):

        '''Return the full, absolute, name of the working file.'''

        fn = working_fn or self.p_to_fn(p,'svg') # 'screenshot_working_file.svg'
        fn = self.finalize(fn)
        if self.trace: g.trace(fn)
        return fn
    #@+node:ekr.20100913085058.5658: *4* sanitize
    def sanitize (self,fn):

        return g.sanitize_filename(fn.lower()).replace('.','-')
    #@+node:ekr.20100911044508.5630: *3* options
    #@+node:ekr.20100909121239.5742: *4* find_at_screenshot_tree_node
    def find_at_screenshot_tree_node (self,p):

        '''
        Return the @screenshot-tree node in a direct child of p.
        '''

        for p2 in p.children():
            if g.match_word(p2.h,0,'@screenshot-tree'):
                return p2
        else:
            return None
    #@+node:ekr.20100913085058.5660: *4* find_select_node
    def find_select_node (self,p):

        '''
        Find the @select node in a direct child of p.
        Return whatever follows @select in the headline.
        '''

        tag = '@select'

        for p2 in p.children():
            if g.match_word(p2.h,0,tag):
                return p2.h[len(tag):].strip()
        else:
            return ''
    #@+node:ekr.20100908110845.5596: *4* get_callouts & helper
    def get_callouts (self,p):

        '''Return the list of callouts from the
        direct children that are @callout nodes.'''

        aList = []
        for child in p.children():
            if g.match_word(child.h,0,'@callout'):
                callout = self.get_callout(child)
                if callout: aList.append(callout)
        # g.trace(aList)
        return aList
    #@+node:ekr.20100909121239.6096: *5* get_callout
    def get_callout (self,p):

        '''Return the text of the callout at p.'''

        if p.b.strip():
            return p.b
        else:
            s = p.h
            assert g.match_word(s,0,'@callout')
            i = g.skip_id(s,0,chars='@')
                # Match @callout or @callouts, etc.
            s = s[i:].strip()
            return s
    #@+node:ekr.20100911044508.5620: *4* get_edit_flag
    def get_edit_flag (self,p):

        '''Return True if any of p's children is an @edit node.'''

        c = self.c

        # Look for any @edit nodes in p's children.
        for child in p.children():
            if g.match_word(child.h,0,'@edit'):
                return True
        else:
            return False
    #@+node:ekr.20100908110845.5597: *4* get_markers & helper
    def get_markers (self,p):

        '''Return the list of markers from all @marker nodes.'''

        aList = []
        for child in p.children():
            if g.match_word(child.h,0,'@marker'):
                callout = self.get_marker(child)
                if callout: aList.extend(callout)
        # g.trace(aList)
        return aList
    #@+node:ekr.20100909121239.6097: *5* get_marker
    def get_marker (self,p):

        '''Return a list of markers at p.'''

        s = p.h
        assert g.match_word(s,0,'@marker')
        i = g.skip_id(s,0,chars='@')
            # Match @marker or @markers, etc.
        s = s[i:].strip()
        return [z.strip() for z in s.split(',')]
    #@+node:ekr.20100913085058.5628: *4* get_protect_flag
    def get_protect_flag (self,p):

         # Look for any @protect or @ignore nodes in p's children.
        for child in p.children():
            if g.match_word(p.h,0,'@ignore') or g.match_word(p.h,0,'@protect'):
                return True
        else:
            return False
    #@+node:ekr.20100913085058.5661: *4* get_screenshot_height/width
    # def get_screenshot_height (self,height):

        # return height or self.default_screenshot_height

    # def get_screenshot_width (self,width):

        # return width or self.default_screenshot_width
    #@+node:ekr.20100913085058.5631: *4* get_setup_app (Not used yet)
    def get_setup_app (self,p):

        tags = ('@setup-app','@setup_app')

        # Look for any @setup-app node in p's children.
        for child in p.children():
            for tag in tags:
                if g.match_word(p.h,0,tag):
                    app_fn = p.h[len(tag):].strip()
                    return True
        else:
            return False
    #@+node:ekr.20100913085058.5630: *4* get_setup_flag
    def get_setup_flag (self,p):

        # Look for any @protect or @ignore nodes in p's children.
        for child in p.children():
            if g.match_word(child.h,0,'@setup'):
                return True
        else:
            return False
    #@+node:ekr.20100913085058.5653: *4* get_slide_number (To be revised)
    def get_slide_number (self,p):

        sc = self

        root = sc.get_slideshow_root(p)

        if root:
            return p.childIndex() # zero-based.
        else:
            return 666

    #@+node:ekr.20100913085058.5654: *4* get_slideshow_root
    def get_slideshow_root (self,p):

        '''Return the @slideshow node containing p as its direct child.'''

        parent = p.parent()

        if parent and g.match_word(parent.h,0,'@slideshow'):
            return parent
        else:
            return None
    #@+node:ekr.20100908110845.5592: *4* in_slide_show
    def in_slide_show (self,p):

        '''Return True if p is a descendant of an @slideshow node.'''

        return bool(self.get_slideshow_root(p))
    #@+node:ekr.20100911044508.5618: *3* utilities
    #@+node:ekr.20100911044508.5637: *4* clear_cache
    def clear_cache (self):

        '''Clear the dimension cache.'''

        self.dimCache = {}
        self.is_reads,self.is_cache = 0,0
    #@+node:ekr.20100908110845.5543: *4* give_pil_warning
    pil_message_given = False

    def give_pil_warning(self):

        '''Give a singleton warning that PIL could not be loaded.'''

        if self.pil_message_given:
            return # Warning already given.

        if got_pil:
            return # The best situation

        self.pil_message_given = True

        if got_qt:
            g.warning('PIL not found: images may have transparent borders')
        else:
            g.warning('PIL and Qt both not found: images may be less clear')
    #@+node:ekr.20100911044508.5636: *4* open_inkscape_with_list (not used)
    def open_inkscape_with_list (self,aList):

        '''Open inkscape with a list of file.'''


        cmd = [self.inkscape_bin,"--with-gui"]
        cmd.extend(aList)

        proc = subprocess.Popen(cmd, stderr=subprocess.PIPE)
        proc.communicate() # Wait for Inkscape to terminate.
    #@+node:ekr.20100909193826.5600: *4* select_at_image_node
    def select_at_image_node (self,p):

        '''Select the @image node in one of p's direct children.'''

        c = self.c
        for child in p.children():
            if g.match_word(child.h,0,'@image'):
                c.selectPosition(child)
                c.redraw_now(child)
                break
        else:
            c.selectPosition(p)
            c.redraw_now(p)
    #@+node:ekr.20100911044508.5635: *3* sc.make_slide_show_command & helper
    def make_slide_show_command (self,p):

        '''Create slides for all slide nodes (direct children)
        of the @slideshow node p.'''

        sc = self

        if not self.inkscape_bin:
            return # The ctor has given the warning.

        if not g.match_word(p.h,0,'@slideshow'):
            return g.error('Not an @slideshow node:',p.h)

        g.note('sphinx-path',sc.get_sphinx_path(None))

        aList = []
        for child in p.children():
            if g.app.commandInterruptFlag: return
            sc.run(child,
                callouts=sc.get_callouts(child),
                markers=sc.get_markers(child))
    #@+node:ekr.20100913085058.5629: *3* sc.take_screen_shot_command
    def take_screen_shot_command (self,p):

        sc = self

        if not self.inkscape_bin:
            return # The ctor has given the warning.

        if not sc.in_slide_show(p):
            return g.error('Not in slide show:',p.h)

        if sc.get_protect_flag(p):
            return g.error('Protected:',p.h)

        sc.run(p,
            callouts=sc.get_callouts(p),
            markers=sc.get_markers(p))

        sc.select_at_image_node(p)
    #@+node:ekr.20100911044508.5616: *3* sc.run & helpers
    def run (self,p,
        callouts=[],markers=[],
        screenshot_fn=None,
        screenshot_height=None,screenshot_width=None,
        working_fn=None,output_fn=None,
        sphinx_path=None,
    ):
        '''Create a slide from p with given callouts and markers.
        Call Inkscape to edit the slide if requested.
        '''

        sc = self
        sc.slide_show_node = sc.get_slideshow_root(p)
        assert sc.slide_show_node
        edit_flag = sc.get_edit_flag(p) or bool(callouts or markers)

        if sc.get_protect_flag(p):
            return g.note('Skipping protected slide:',p.h)

        # Compute paths and file names.
        sphinx_path = sc.get_sphinx_path(sphinx_path)
        if not sphinx_path: return
        if not output_fn: output_fn = sc.get_output_fn(p)
        screenshot_fn = sc.get_screenshot_fn(p,screenshot_fn)
        setup_flag = sc.get_setup_flag(p)
        working_fn = sc.get_working_fn(p,working_fn)
        if not working_fn: return
        sc.screenshot_height=screenshot_height or sc.default_screenshot_height
        sc.screenshot_width=screenshot_width or sc.default_screenshot_width

        # Compute these after omputing sphinx_path and screenshot_fn...
        image_fn = self.get_at_image_fn(screenshot_fn)
        directive_fn = sc.get_directive_fn(p,sphinx_path,screenshot_fn)
        template_fn = self.get_template_fn()

        # Take the screenshot and update the tree.
        ok = sc.take_screen_shot(p,directive_fn,image_fn,screenshot_fn,setup_flag)
        if not ok: return

        # Create the working file from the template.
        sc.give_pil_warning()
        template = sc.make_dom(callouts,markers,screenshot_fn,template_fn)
        if not template:
            return g.error('Can not make template from:',template_fn)

        self.make_working_file(template,working_fn)

        if edit_flag:
            sc.edit_working_file(working_fn)

        # Create the output file.
        if output_fn:
            sc.make_output_file(output_fn,working_fn)
        else:
            g.note('Empty @output node inhibits output')

        return screenshot_fn
    #@+node:ekr.20100909121239.6117: *4* 1: take_screen_shot & helpers
    def take_screen_shot(self,p,directive_fn,image_fn,screenshot_fn,setup_flag):

        '''Take the screen shot, create an @image node,
        and add an .. image:: directive to p.'''

        sc = self
        hoist_tree = sc.find_at_screenshot_tree_node(p)
        select_node = sc.find_select_node(p)

        # Always create 'screenshot-setup.leo' 
        fn = sc.create_setup_leo_file(hoist_tree)

        # Always open fn in a separate process.
        ok = sc.setup_screen_shot(fn,hoist_tree,screenshot_fn,select_node,setup_flag)

        if ok:
            g.note('slide node:  %s' % p.h)
            g.note('output file: %s' % g.shortFileName(screenshot_fn))
            sc.make_image_node(p,image_fn)
            sc.add_image_directive(p,directive_fn)
        else:
            g.warning('problems making screen shot:',p.h)
        return ok
    #@+node:ekr.20100908110845.5594: *5* add_image_directive
    def add_image_directive (self,p,directive_fn):

        '''Add ".. image:: <directive_fn>" to p.b if it is not already there.'''

        s = '.. image:: %s' % directive_fn.replace('\\','/')

        if p.b.find(s) == -1:
            p.b = p.b.rstrip() + '\n\n%s\n\n' % (s)
    #@+node:ekr.20100914090933.5643: *5* create_setup_leo_file
    def create_setup_leo_file(self,hoist_tree):

        '''Create an ouline containing all children of hoist_tree.'''

        sc = self ; fn = sc.finalize('screenshot-setup.leo')

        c,frame = g.app.newLeoCommanderAndFrame(
            fileName=fn,relativeFileName=None) # ,gui=gui)

        # Copy the entire tree.
        c.frame.createFirstTreeNode()
        root = c.rootPosition()
        children = [z.copy() for z in hoist_tree.children()]
        children.reverse()
        child1 = children and children[0]
        for child in children:
            child2 = root.insertAfter()
            child.copyTreeFromSelfTo(child2)
        # g.trace(root)
        if child1:
            root.doDelete(newNode=None)
            c.setRootPosition(child1) # Essential!
        # Adjust the context for the new file.
        if 0:
            for v in c.all_nodes():
                v.context = c

        # Save the file silently.
        c.fileCommands.save(fn)
        c.close()

        return fn
    #@+node:ekr.20100908110845.5599: *5* make_image_node
    def make_image_node (self,p,image_fn):

        '''Create an @image node as the first child of p.'''

        c = self.c

        h = '@image %s' % image_fn

        # Create the node if it doesn't exist.
        for child in p.children():
            if child.h == h:
                # print('already exists: %s' % h)
                break
        else:
            c.selectPosition(p)
            p2 = p.insertAsNthChild(0)
            p2.h = h
    #@+node:ekr.20100913085058.5659: *5* setup_screen_shot & helpers
    def setup_screen_shot (self,fn,hoist_tree,screenshot_fn,select_node,setup_flag):

        '''Take the screen shot after adjusting the window and outline.'''

        sc = self

        # Important: we must *not* have the clipboard open here!
        # Doing so can hang if the user does a clipboard operation
        # in a subprocess.
        if 0:
            cb = g.app.gui.qtApp.clipboard()
            if cb: cb.clear(cb.Clipboard) # Does not work anyway.

        ok = sc.open_screenshot_app(fn,hoist_tree,select_node,setup_flag,screenshot_fn)

        if ok and setup_flag:
            ok = sc.save_clipboard_to_screenshot_file(screenshot_fn)

        return ok
    #@+node:ekr.20100913085058.5656: *6* open_screenshot_app
    def open_screenshot_app (self,fn,hoist_tree,select_node,setup_flag,screenshot_fn):

        '''Open the screenshot app.
        Return True if the app exists and can be opened.'''

        verbose = False
        sc = self ; c = sc.c
        launch = g.os_path_finalize_join(g.app.loadDir,
            '..','..','launchLeo.py')
        python = sys.executable

        h,w = sc.screenshot_height,sc.screenshot_width
        cmd = [python,launch,'--window-size=%sx%s' % (h,w)]

        if select_node:
            cmd.append('--select="%s"' % (select_node))

        if not setup_flag:
            cmd.append('--screen-shot="%s"' % screenshot_fn)

        cmd.append('--file="%s"' % (fn))

        if verbose:
            proc = subprocess.Popen(cmd)
        else:
            # Eat the output.
            proc = subprocess.Popen(cmd,
                stdout=subprocess.PIPE,stderr=subprocess.PIPE)

        proc.communicate() # Wait for Leo to terminate.
        return True
    #@+node:ekr.20100913085058.5655: *6* save_clipboard_to_screenshot_file
    def save_clipboard_to_screenshot_file (self,screenshot_fn):

        '''Save the clipboard to screenshot_fn.
        Return True if all went well.'''

        sc = self

        cb = g.app.gui.qtApp.clipboard()
        if not cb:
            return g.error('no clipboard')

        image = cb.image()

        if image:
            image.save(screenshot_fn)
            return True
        else:
            return g.error('no image on clipboard')
    #@+node:ekr.20100908110845.5546: *4* 2: make_dom & helpers
    def make_dom(self,callouts,markers,screenshot_fn,template_fn):

        '''Create the template dom object.'''

        trace = True and not g.unitTesting
        template = self.get_template(template_fn)
        if not template: return None
        root = template.getroot()
        ids_d = self.getIds(root)
        parents_d = self.getParents(root)

        # make a dict of the groups we're going to manipulate
        part = dict([(z,ids_d.get(z))
            for z in ('co_g_co', 'co_g_bc_1', 'co_g_bc_2')])

        # note where we should place modified copies
        part_parent = parents_d.get(part.get('co_g_co'))

        # remove them from the document
        for i in part.values():
            parents_d = self.getParents(root)
            parent = parents_d.get(i)
            parent.remove(i)

        for n,callout in enumerate(callouts):
            if trace: g.trace('callout %s: %s' % (n,callout))
            z = copy.deepcopy(part['co_g_co'])
            ids_d = self.getIds(z)
            text = ids_d.get('co_text_holder')
            text.text = callout
            # need distinct IDs on frames/text for sizing
            frame = ids_d.get('co_frame')
            self.clear_id(z) # let inkscape pick new IDs for other elements

            # A) it's the flowRoot, not the flowPara, which carries the size info
            # B) Inkscape trashes the IDs on flowParas on load!
            parents_d = self.getParents(z)
            parent = parents_d.get(text)
            parent.set('id', 'co_text_%d'%n)
            frame.set('id', 'co_frame_%d'%n)

            # offset so user can see them all
            self.move_element(z, 20*n, 20*n)
            part_parent.append(z)

        for n,number in enumerate(markers):
            if trace: g.trace('number %s: %s' % (n,number))
            if len(str(number)) == 2:
                use_g,use_t = 'co_g_bc_2', 'co_bc_text_2'
            else:
                use_g,use_t = 'co_g_bc_1', 'co_bc_text_1'

            z = copy.deepcopy(part[use_g])
            ids_d = self.getIds(z)
            bc_text = ids_d.get(use_t) 
            bc_text.text = str(number)
            self.move_element(z, 20*n, 20*n)
            part_parent.append(z)

        # point to the right screen shot
        ids_d = self.getIds(template.getroot())
        img_element = ids_d.get('co_shot')
        img_element.set(self.xlink+'href',screenshot_fn)

        # adjust screen shot dimensions
        if got_pil:
            img = Image.open(screenshot_fn)
            img_element.set('width', str(img.size[0]))
            img_element.set('height', str(img.size[1]))

        # write temp file to get size info
        fh, fp = tempfile.mkstemp()
        os.close(fh)
        template.write(fp)

        # could reload file at this point to reflect offsets etc.
        # but don't need to because of relative position mode in paths

        # resize things to fit text
        for n,callout in enumerate(callouts):
            self.resize_curve_box(fp,template,n)

        os.unlink(fp)
        return template
    #@+node:ekr.20100908110845.5547: *5* clear_id
    def clear_id(self,x):

        """Recursively clear @id on element x and descendants."""

        if 'id' in x.keys():
            del x.attrib['id']

        ids_d = self.getIds(x)
        objects = set(list(ids_d.values()))
        for z in objects:
            del z.attrib['id']

        return x
    #@+node:ekr.20100908110845.5548: *5* get_template
    def get_template(self,template_fn):

        """Load and check the template SVG and return DOM"""

        infile = open(template_fn)
        template = etree.parse(infile)
        ids_d = self.getIds(template.getroot())

        # check all IDs we expect are present
        ids = list(ids_d.keys())
        if set(self.ids) <= set(ids):
            return template
        else:
            g.error('template did not include all required IDs:',template_fn)
            return None
    #@+node:ekr.20100908110845.5549: *5* move_element
    def move_element(self,element,x,y):

        if not element.get('transform'):
            element.set('transform', "translate(%f,%f)" % (x,y))
        else:
            ox,oy = element.get('transform').split(',')
            ox = ox.split('(')[1]
            oy = oy.split(')')[0]

            element.set('transform', "translate(%f,%f)" %
                (float(ox)+x, float(oy)+y))
    #@+node:ekr.20100908110845.5550: *5* resize_curve_box & helper
    def resize_curve_box(self,fn,template,n):

        d = self.getIds(template.getroot())
        text = d.get('co_text_%d' % (n))
        frame = d.get('co_frame_%d' % (n))
        text_id = text.get('id')
        frame_id = frame.get('id')

        pnts = frame.get('d').split()
        i = 0
        while i < len(pnts):
            if ',' not in pnts[i]:
                type_ = pnts[i]
                del pnts[i]
            else:
                pnts[i] = [float(j) for j in pnts[i].split(',')]
                pnts[i].insert(0, type_)
                if type_ == 'm':
                    type_ = 'l'
                i += 1

        # kludge for now
        h0 = 12  # index of vertical component going down right side
        h1 = -4  # index of vertical component coming up left side
        min_ = 0  # must leave this many
        present = 5  # components present initially
        h = pnts[h0][2]  # height of one component
        th = self.get_dim(fn,text_id,'height')  # text height
        if not th:
            g.trace('no th')
        # g.trace('  ', present, h, present*h, th)
        while present > min_ and present * h + 15 > th:
            # g.trace('  ', present, h, present*h, th)
            del pnts[h0]
            del pnts[h1]
            present -= 1

        last = ''
        d = []
        for p in pnts:
            if last != p[0]:
                last = p[0]
                if last == 'm':
                    last = 'l'
                d.append(p[0])
            d.append("%s,%s" % (p[1], p[2]))
        d.append('z')

        frame.set('d', ' '.join(d))
    #@+node:ekr.20100908110845.5551: *6* get_dim
    def get_dim(self, fn, Id, what):
        """return dimension of element in fn with @id Id, what is
        x, y, width, or height
        """

        trace = False
        hsh = fn+Id+what
        if trace: g.trace('hsh',repr(fn),repr(Id),repr(what))
        if hsh in self.dimCache:
            self.is_cache += 1
            return self.dimCache[hsh]

        cmd = [self.inkscape_bin, '--without-gui', '--query-all', fn]

        proc = subprocess.Popen(cmd,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE)

        # make new pipe for stderr to supress chatter from inkscape.
        stdout, stderr = proc.communicate() # Wait for Inkscape to terminate.
        s = str(stdout).strip()

        # Necessary for Python 3k.
        if s.startswith("b'"): s = s[2:]
        if s.endswith("'"): s = s[:-1]
        aList = s.replace('\\r','').replace('\\n','\n').split('\n')
        for line in aList:
            if not line.strip(): continue
            id_,x,y,w,h = line.split(',')
            for part in ('x',x), ('y',y), ('width',w), ('height',h):
                hsh2 = fn+id_+part[0]
                if trace: g.trace('hsh2',repr(id_),repr(part[0]))
                self.dimCache[hsh2] = float(part[1])
        self.is_reads += 1

        assert self.dimCache.get(hsh)
        return self.dimCache.get(hsh)
    #@+node:ekr.20100908110845.5545: *4* 3: make_working_file
    def make_working_file(self,template,working_fn):

        '''Create the working file from the template.'''

        outfile = open(working_fn,'w')
        template.write(outfile)
        outfile.close()
    #@+node:ekr.20100908110845.5552: *4* 4: edit_working_file & helper
    def edit_working_file(self,working_fn):

        '''Invoke Inkscape on the working file.'''

        self.enable_filters(working_fn, False)

        cmd = [self.inkscape_bin,"--with-gui",working_fn]
        proc = subprocess.Popen(cmd, stderr=subprocess.PIPE)
        proc.communicate()  # Wait for Inkscape to terminate.

        self.enable_filters(working_fn, True)
    #@+node:ekr.20100908110845.5553: *5* enable_filters
    def enable_filters(self,svgfile,enable):
        """Disable/enable filters in SVG at the XML level

        The drop-shadow filter on several objects kills editing performance
        in inkscape, so this turns them on/off in the XML.  There's a GUI
        operation to turn them off in inkscape, but it's a pain to have to
        keep using it.

        Disabling copys the real @style to @__style and changes
        "filter:url" to "_filter:url" in the active @style, while
        enabling just copys @__style to @style and deletes @__style.
        """

        doc = etree.parse(svgfile)
        root = doc.getroot()

        if enable:
            # copy @__style to @style and deletes @__style.
            aList = self.getElementsWithAttrib(root,'__style')
            for i in aList:
                i.set("style", i.get("__style"))
                del i.attrib['__style']
        else:
            aList3 = self.getElementsWithAttrib(root,'style')
            aList = [z for z in aList3
                if z.attrib.get('style').find('filter:url(') > -1]
            # copy the real @style to @__style and
            # changes "filter:url" to "_filter:url" in the active @style
            for i in aList:
                i.set("__style", i.get("style"))
                i.set("style", i.get("style").replace(
                    'filter:url(', '_filter:url('))

        doc.write(open(svgfile, 'w'))
    #@+node:ekr.20100908110845.5554: *4* 5: make_output_file & helper
    def make_output_file(self,output_fn,working_fn):

        '''Create the output file from the working file.'''

        cmd = (
            self.inkscape_bin,
            "--without-gui",
            "--export-png="+output_fn,
            "--export-area-drawing",
            "--export-area-snap",
            working_fn)

        proc = subprocess.Popen(cmd, stderr=subprocess.PIPE)
        proc.communicate() # Wait for Inkscape to terminate.

        if got_pil: # trim transparent border
            try:
                img = Image.open(output_fn)
                img = self.trim(img, (255,255,255,0))
                img.save(output_fn)
            except IOError:
                g.trace('Can not open %s' % output_fn)

        # os.system(png_fn)
    #@+node:ekr.20100908110845.5555: *5* trim
    def trim(self, im, border):
         bg = Image.new(im.mode, im.size, border)
         diff = ImageChops.difference(im, bg)
         bbox = diff.getbbox()
         if bbox:
             return im.crop(bbox)
         else:
             # found no content
             raise ValueError("cannot trim; image was empty")
    #@-others

#@-others
#@-leo

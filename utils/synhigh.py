"""
Copyright 2010 Mark Holmquist and Logan May. All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are
permitted provided that the following conditions are met:

   1. Redistributions of source code must retain the above copyright notice, this list of
      conditions and the following disclaimer.

   2. Redistributions in binary form must reproduce the above copyright notice, this list
      of conditions and the following disclaimer in the documentation and/or other materials
      provided with the distribution.

THIS SOFTWARE IS PROVIDED BY MARK HOLMQUIST AND LOGAN MAY ``AS IS'' AND ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL MARK HOLMQUIST OR LOGAN
MAY OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those of the
authors and should not be interpreted as representing official policies, either expressed
or implied, of Mark Holmquist and Logan May.
"""

"""
Modified By Terence van Zyl
"""
# library
import urllib
# third-party
from gui.theme import CurrentTheme
from PyQt4 import QtGui, QtCore
# vistrails
from core.modules.vistrails_module import ModuleError
from core.modules.source_configure import SourceConfigurationWidget
from core.modules.tuple_configuration import PortTable, PortTableItemDelegate
from core.modules.module_registry import get_module_registry
# eo4vistrails
# local


class SynPortTable(PortTable):
    """Replace the current port tables with  new modified versions;
    allows us to set which input ports are viable.
    """

    def __init__(self, parent=None, displayedComboItems=None):
        QtGui.QTableWidget.__init__(self, 1, 2, parent)
        self.horizontalHeader().setResizeMode(QtGui.QHeaderView.Interactive)
        self.horizontalHeader().setMovable(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        # The following lines have been changed so that
        # we can specify which ports should be listed
        self.delegate = SynPortTableItemDelegate(self)
        self.delegate.setDisplayedComboItems(displayedComboItems)
        ########################################################
        self.setItemDelegate(self.delegate)
        self.setFrameStyle(QtGui.QFrame.NoFrame)
        self.connect(self.model(),
                     QtCore.SIGNAL('dataChanged(QModelIndex,QModelIndex)'),
                     self.handleDataChanged)


class SynPortTableItemDelegate(PortTableItemDelegate):

    def setDisplayedComboItems(self, displayedComboItems):
        self.displayedComboItems = displayedComboItems

    def createEditor(self, parent, option, index):
        if self.displayedComboItems:
            registry = get_module_registry()
            if index.column() == 1:  # Port type
                combo = QtGui.QComboBox(parent)
                combo.setEditable(False)
                # FIXME just use descriptors here!!
                for _, pkg in sorted(registry.packages.iteritems()):
                    for _, descriptor in sorted(pkg.descriptors.iteritems()):
                        if descriptor.name in self.displayedComboItems:
                            combo.addItem("%s (%s)" % (descriptor.name,
                                                       descriptor.identifier),
                                          QtCore.QVariant(descriptor.sigstring))
                return combo
            else:
                return QtGui.QItemDelegate.createEditor(self, parent, option, index)
        else:
            registry = get_module_registry()
            if index.column() == 1:  # Port type
                combo = QtGui.QComboBox(parent)
                combo.setEditable(False)
                # FIXME just use descriptors here!!
                for _, pkg in sorted(registry.packages.iteritems()):
                    for _, descriptor in sorted(pkg.descriptors.iteritems()):
                        combo.addItem("%s (%s)" % (descriptor.name,
                                                   descriptor.identifier),
                                      QtCore.QVariant(descriptor.sigstring))
                return combo
            else:
                return QtGui.QItemDelegate.createEditor(self, parent, option, index)


def format(color, style='', bgcolor=''):
    """Return a QTextCharFormat with the given attributes.
    """
    _color = QtGui.QColor()
    _color.setNamedColor(color)
    _format = QtGui.QTextCharFormat()
    _format.setForeground(_color)
    if 'bold' in style:
        _format.setFontWeight(QtGui.QFont.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)
    if bgcolor != '':
        _color.setNamedColor(bgcolor)
        _format.setBackground(_color)

    return _format


class SyntaxSourceConfigurationWidget(SourceConfigurationWidget):

    def __init__(self, module, controller, syntax,
                 parent=None, has_inputs=True, has_outputs=True, encode=True,
                 input_port_specs=None, output_port_specs=None, displayedComboItems=None):

        self.displayedComboItems = displayedComboItems
        #print module.input_port_specs
        if input_port_specs:
            self.input_port_specs = input_port_specs
        else:
            self.input_port_specs = module.input_port_specs
        if output_port_specs:
            self.output_port_specs = output_port_specs
        else:
            self.output_port_specs = module.output_port_specs

        SourceConfigurationWidget.__init__(self, module, controller, SyntaxEditor,
                                           parent=parent, has_inputs=has_inputs, has_outputs=has_outputs,
                                           encode=encode, portName='source')

        self.codeEditor.setSyntax(syntax)

    def createPortTable(self, has_inputs=True, has_outputs=True):
        if has_inputs:
            self.inputPortTable = SynPortTable(self, self.displayedComboItems)
            labels = QtCore.QStringList() << "Input Port Name" << "Type"
            self.inputPortTable.setHorizontalHeaderLabels(labels)
            self.inputPortTable.initializePorts(self.input_port_specs)
            self.layout().addWidget(self.inputPortTable)
        if has_outputs:
            self.outputPortTable = SynPortTable(self, self.displayedComboItems)
            labels = QtCore.QStringList() << "Output Port Name" << "Type"
            self.outputPortTable.setHorizontalHeaderLabels(labels)
            self.outputPortTable.initializePorts(self.output_port_specs, True)
            self.layout().addWidget(self.outputPortTable)
        if has_inputs and has_outputs:
            self.performPortConnection(self.connect)
        if has_inputs:
            self.inputPortTable.fixGeometry()
        if has_outputs:
            self.outputPortTable.fixGeometry()


class SyntaxEditor(QtGui.QTextEdit):

    def __init__(self, parent=None):
        QtGui.QTextEdit.__init__(self, parent)
        self.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        self.formatChanged(None)
        self.setCursorWidth(8)
        self.connect(self,
                     QtCore.SIGNAL('currentCharFormatChanged(QTextCharFormat)'),
                     self.formatChanged)

    def setSyntax(self, syntax):
        self.highlighter = SyntaxHighlighter(self.document(), syntax)

    def formatChanged(self, f):
        self.setFont(CurrentTheme.PYTHON_SOURCE_EDITOR_FONT)

    def keyPressEvent(self, event):
        """ keyPressEvent(event: QKeyEvent) -> Nont
        Handle tab with 4 spaces

        """
        if event.key() == QtCore.Qt.Key_Tab:
            self.insertPlainText('    ')
        else:
            # super(PythonEditor, self).keyPressEvent(event)
            QtGui.QTextEdit.keyPressEvent(self, event)


class SyntaxHighlighter (QtGui.QSyntaxHighlighter):

    def __init__(self, document, language):
        QtGui.QSyntaxHighlighter.__init__(self, document)

        self.caseSensitivity = QtCore.Qt.CaseSensitive

        self.styles = {
            'keyword': format('red'),
            'type': format('orange'),
            'preproc': format('green'),
            'brace': format('darkBlue'),
            'defclass': format('black', 'bold'),
            'literal': format('magenta'),
            'comment': format('darkGreen', 'italic'),
            'wsspace': format('black', bgcolor='blue'),
            'wstab': format('black', bgcolor='red')}
        self.rules = []
        rules = []

        # SQL ______________________________________________________________________________________________________________________
        if language == "SQL":
            keywords = ['begin','commit','rollback','select','from','where','explain','insert','into','values','update','create','delete','drop','grant','revoke','lock','set','truncate','as','join','on','table','view','order','group','by','having']
            rules += [(r'\b%s\b' % w, 0, self.styles['keyword']) for w in keywords]

            types = ['anydata','anydataset','anytype','array','bfile','bigint','binary_double','binary_float','binary_integer','bit','blob','boolean','cfile','char','character','clob','date','datetime','day','dburitype','dec','decimal','double','enum','float','float4','float8','flob','httpuritype','int','int16','int2','int24','int4','int8','integer','interval','lob','long','longblob','longlong','longtext','mediumblob','mediumtext','mlslabel','month','national','nchar','nclob','newdate','null','number','numeric','nvarchar','object','pls_integer','precision','raw','real','record','rowid','second','short','single','smallint','time','timestamp','tiny','tinyblob','tinyint','tinytext','urifactorytype','uritype','urowid','utc_date','utc_time','utc_timestamp','varchar','varchar2','varray','varying','xmltype','year','zone']
            rules += [(r'\b%s\b' % w, 0, self.styles['type']) for w in types]

            preprocs = ['abort','abs','absolute','access','action','ada','add','admin','after','aggregate','alias','all','allocate','alter','analyse','analyze','and','any','are','asc','asensitive','assertion','assignment','asymmetric','at','atomic','audit','authorization','avg','backward','before','between','bigint','binary','bit_length','bitvar','both','breadth','c','cache','call','called','cardinality','cascade','cascaded','case','cast','catalog','catalog_name','chain','change','char_length','character_length','character_set_catalog','character_set_name','character_set_schema','characteristics','check','checked','checkpoint','class','class_origin','close','cluster','coalesce','cobol','collate','collation','collation_catalog','collation_name','collation_schema','column','column_name','command_function','command_function_code','comment','committed','completion','compress','condition','condition_number','connect','connection','connection_name','constraint','constraint_catalog','constraint_name','constraint_schema','constraints','constructor','contains','continue','conversion','convert','copy','corresponding','count','createdb','createuser','cross','cube','current','current_date','current_path','current_role','current_time','current_timestamp','current_user','cursor','cursor_name','cycle','data','database','databases','datetime_interval_code','datetime_interval_precision','day_hour','day_microsecond','day_minute','day_second','deallocate','declare','default','deferrable','deferred','defined','definer','delayed','delimiter','delimiters','depth','deref','desc','describe','descriptor','destroy','destructor','deterministic','diagnostics','dictionary','disconnect','dispatch','distinct','distinctrow','div','do','domain','dual','dynamic','dynamic_function','dynamic_function_code','each','else','elseif','elsif','enclosed','encoding','encrypted','end','end-exec','equals','escape','escaped','every','except','exception','exclusive','exec','execute','existing','exists','exit','external','extract','false','fetch','file','final','first','for','force','foreign','fortran','forward','found','free','freeze','full','fulltext','function','g','general','generated','get','global','go','goto','granted','grouping','handler','hierarchy','high_priority','hold','host','hour','hour_microsecond','hour_minute','hour_second','identified','identity','if','ignore','ilike','immediate','immutable','implementation','implicit','in','increment','index','indicator','infile','infix','inherits','initial','initialize','initially','inner','inout','input','insensitive','instance','instantiable','instead','int1','int3','intersect','invoker','is','isnull','isolation','iterate','k','key','key_member','key_type','keys','kill','lancompiler','language','large','last','lateral','leading','leave','left','length','less','level','like','limit','lines','listen','load','local','localtime','localtimestamp','location','locator','loop','low_priority','lower','m','map','match','max','maxextents','maxvalue','mediumint','message_length','message_octet_length','message_text','method','middleint','min','minus','minute','minute_microsecond','minute_second','minvalue','mod','mode','modifies','modify','module','more','move','mumps','name','names','natural','new','next','no','no_write_to_binlog','noaudit','nocompress','nocreatedb','nocreateuser','none','not','nothing','notify','notnull','nowait','nullable','nullif','octet_length','of','off','offline','offset','oids','old','online','only','open','operation','operator','optimize','option','optionally','options','or','ordinality','out','outer','outfile','output','overlaps','overlay','overriding','owner','pad','parameter','parameter_mode','parameter_name','parameter_ordinal_position','parameter_specific_catalog','parameter_specific_name','parameter_specific_schema','parameters','partial','pascal','password','path','pctfree','pendant','placing','pli','position','postfix','prefix','preorder','prepare','preserve','primary','prior','privileges','procedural','procedure','public','purge','raid0','read','reads','recheck','recursive','ref','references','referencing','regexp','reindex','relative','release','rename','repeat','repeatable','replace','require','reset','resource','restrict','result','return','returned_length','returned_octet_length','returned_sqlstate','returns','right','rlike','role','rollup','routine','routine_catalog','routine_name','routine_schema','row','row_count','rowlabel','rownum','rows','rule','savepoint','scale','schema','schema_name','schemas','scope','scroll','search','second_microsecond','section','security','self','sensitive','separator','sequence','serializable','server_name','session','session_user','setof','sets','share','show','similar','simple','size','some','soname','source','space','spatial','specific','specific_name','specifictype','sql','sqlcode','sqlerror','sqlexception','sqlstate','sqlwarning','ssl','stable','start','starting','state','statement','static','statistics','stdin','stdout','storage','straight_join','strict','structure','style','subclass_origin','sublist','substring','successful','sum','symmetric','synonym','sysdate','sysid','system','system_user','table_name','temp','template','temporary','terminate','terminated','than','then','timezone_hour','timezone_minute','to','toast','trailing','transaction','transaction_active','transactions_committed','transactions_rolled_back','transform','transforms','translate','translation','treat','trigger','true','type','uid','undo','union','unique','unlock','unsigned','usage','use','user','using','validate','varbinary','varcharacter','when','whenever','while','with','write','x509','xor','year_month','zerofillzgium']
            rules += [(r'\b%s\b' % w, 0, self.styles['preproc']) for w in preprocs]

            braces = ['\{','\}','\(','\)','\[','\]']
            rules += [(r'%s' % w, 0, self.styles['brace']) for w in braces]

            rules += [
                    (r'"[^"\\]*(\\.[^"\\]*)*"', 0, self.styles['literal']),  # Double-quote strings
                    (r"'[^'\\]*(\\.[^'\\]*)*'", 0, self.styles['literal']),  # Single-quote strings
                    (r'\b\d+\b', 0, self.styles['literal']),  # Numbers
                    (r'--[^\n]*', 0, self.styles['comment'])]
            self.caseSensitivity = QtCore.Qt.CaseInsensitive

        # PovRay ______________________________________________________________________________________________________________________
        if language == "PovRay":
            keywords = ['aa_level','aa_threshold','abs','absorption','accuracy','acos','acosh','adaptive','adc_bailout',
                        'agate_turb','all','all_intersections','alpha','altitude','always_sample','ambient','ambient_light','angle',
                        'aperture','append','arc_angle','area_light','array','asc','ascii','asin','asinh','assumed_gamma','atan','atan2',
                        'atanh','autostop','b_spline','bezier_spline','black_hole','blue',
                        'blur_samples','bounded_by','break','brick_size','brightness','brilliance','bump_map',
                        'bump_size','case','catmull_rom_spline','caustics','ceil','charset','chr','circular',
                        'clipped_by','clock','clock_delta','clock_on','collect','color','color_map','colour','colour_map','component','composite',
                        'concat','confidence','conic_sweep','conserve_energy','contained_by','control0','control1','coords','cos','cosh',
                        'count','crand','cube','cubic','cubic_spline','cubic_wave','cutaway_textures',
                        'debug','declare','default','defined','degrees','density','density_map','df3',
                        'diffuse','dimension_size','dimensions','direction','dispersion','dispersion_samples','dist_exp','distance',
                        'div','double_illuminate','eccentricity','else','emission','end','error','error_bound','evaluate','exp',
                        'expand_thresholds','exponent','exterior','extinction','face_indices','fade_color','fade_colour','fade_distance',
                        'fade_power','falloff','falloff_angle','false','fclose','file_exists','filter','final_clock','final_frame','finish','fisheye',
                        'flatness','flip','floor','focal_point','fog_alt','fog_offset','fog_type','fopen','frame_number','frequency',
                        'fresnel','function','gather','gif','global_lights','gray','gray_threshold',
                        'green','h_angle','hf_gray_16','hierarchy','hollow','hypercomplex','if','ifdef','iff','ifndef',
                        'image_height','image_map','image_width','include','initial_clock','initial_frame','inside','int',
                        'interior','interior_texture','internal','interpolate','intervals','inverse','ior','irid',
                        'irid_wavelength','jitter','jpeg','lambda','light_group',
                        'linear_spline','linear_sweep','ln','load_file','local','location','log','look_at','looks_like',
                        'low_error_factor','macro','major_radius','map_type','material','material_map','matrix',
                        'max','max_extent','max_gradient','max_intersections','max_iteration','max_sample','max_trace','max_trace_level',
                        'media','media_attenuation','media_interaction','metallic','method','min',
                        'min_extent','minimum_reuse','mod','mortar','nearest_count','no','no_bump_scale','no_image','no_reflection',
                        'no_shadow','noise_generator','normal','normal_indices','normal_map','normal_vectors','number_of_waves',
                        'octaves','off','omega','omnimax','on','once','open','orient','orientation','orthographic',
                        'panoramic','parallel','parametric','pass_through','perspective','pgm','phase','phong',
                        'phong_size','photons','pi','pigment','pigment_map','png','point_at',
                        'poly_wave','pot','pow','ppm','precision','precompute','pretrace_end','pretrace_start',
                        'projected_through','pwr','quadratic_spline','quaternion','quick_color','quick_colour',
                        'radians','radius','ramp_wave','rand','range','range_divider','ratio',
                        'read','reciprocal','recursion_limit','red','reflection','reflection_exponent','refraction','render','repeat',
                        'rgb','rgbf','rgbft','rgbt','right','rotate','roughness','samples','save_file','scale','scallop_wave',
                        'scattering','seed','select','shadowless','sin','sine_wave','sinh','size','sky','slice',
                        'slope_map','smooth','sor','spacing','specular',
                        'spline','split_union','spotlight','sqr','sqrt','statistics','str','strcmp','strength',
                        'strlen','strlwr','strupr','sturm','substr','switch','sys','t','tan','tanh','target','texture',
                        'texture_list','texture_map','tga','thickness','threshold','tiff','tightness','tolerance','toroidal',
                        'trace','transform','translate','transmit','triangle_wave','true','ttf','turb_depth','turbulence',
                        'type','u','u_steps','ultra_wide_angle','undef','up','use_alpha','use_color','use_colour','use_index','utf8',
                        'uv_indices','uv_mapping','uv_vectors','v','v_angle','v_steps','val','variance','vaxis_rotate','vcross','vdot',
                        'version','vertex_vectors','vlength','vnormalize','vrotate','vstr','vturbulence','warning','warp','water_level',
                        'while','width','write','x','y','yes','z']
            rules += [(r'\b%s\b' % w, 0, self.styles['keyword']) for w in keywords]

            types = ['bicubic_patch', 'box','blob','camera','cone','cylinder','difference','disc','height_field','julia_fractal','lathe',
                     'prism','sphere','sphere_sweep','superellipsoid','text','torus','mesh','mesh2','polygon','triangle',
                     'smooth_triangle','plane','poly','quadric','quartic','isosurface','sor',
                     'union','merge','intersection','object',
                     'global_settings','background','radiosity','light_source',
                     'fog','sky_sphere','rainbow','agate','average','boxed','bozo','brick','bumps','cells',
                     'checker','crackle','form','metric','offset','solid',
                     'cylindrical','density_file','dents','facets','mandel','julia',
                     'magnet','gradient','granite','hexagon','image_pattern','leopard',
                     'marble','onion','pattern','pigment_pattern','planar','quilted',
                     'radial','ripples','slope','spherical','spiral1','spiral2',
                     'spotted','waves','wood','wrinkles','tile2','tiles']
            rules += [(r'%s' % w, 0, self.styles['type']) for w in types]

            preprocs = ['#end','#while','#local','#macro','#declare','#define',
                        '#error','#include','#line','#pragma','#undef','#if',
                        '#ifdef','#ifndef','#else','#elif','#endif','#default',
                        '#local','#switch','#version','#break','#case','#end',
                        '#ifdef','#ifndef','#range','#fclose','#fopen','#read',
                        '#write','#debug','#error','#render','#statistics',
                        '#warning']
            rules += [(r'%s' % w, 0, self.styles['preproc']) for w in preprocs]

            braces = ['\{','\}','\(','\)','\[','\]']
            rules += [(r'%s' % w, 0, self.styles['brace']) for w in braces]

            rules += [
                    (r'"[^"\\]*(\\.[^"\\]*)*"', 0, self.styles['literal']),  # Double-quote strings
                    (r"'[^'\\]*(\\.[^'\\]*)*'", 0, self.styles['literal']),  # Single-quote strings
                    (r'\b\d+\b', 0, self.styles['literal']),  # Numbers
                    (r'\/\/[^\n]*', 0, self.styles['comment']),
                    (r'\\\\[^\n]*', 0, self.styles['comment'])]

        # C++ ______________________________________________________________________________________________________________________
        if language == "C++":
            keywords = ['and','and_eq','asm','auto','bitand','bitor','bool','break','case','catch','char','class','compl','const','const_cast','continue','default','delete','do','double','dynamic_cast','else','enum','explicit','export','extern','false','float','for','friend','goto','if','inline','int','long','mutable','namespace','new','not','not_eq','operator','or','or_eq','private','protected','public','register','reinterpret_cast','return','short','signed','sizeof','static','static_cast','struct','switch','template','this','throw','true','try','typedef','typeid','typename','union','unsigned','using','virtual','void','volatile','wchar_t','while','xor','xor_eq']
            rules += [(r'\b%s\b' % w, 0, self.styles['keyword']) for w in keywords]

            preprocs = ['#define','#error','#include','#line','#pragma','#undef','#if','#ifdef','#ifndef','#else','#elif','#endif']
            rules += [(r'%s' % w, 0, self.styles['preproc']) for w in preprocs]

            braces = ['\{','\}','\(','\)','\[','\]']
            rules += [(r'%s' % w, 0, self.styles['brace']) for w in braces]

            rules += [
                    (r'"[^"\\]*(\\.[^"\\]*)*"', 0, self.styles['literal']),  # Double-quote strings
                    (r"'[^'\\]*(\\.[^'\\]*)*'", 0, self.styles['literal']),  # Single-quote strings
                    (r'\b\d+\b', 0, self.styles['literal']),  # Numbers
                    (r'\/\/[^\n]*', 0, self.styles['comment']),
                    (r'\\\\[^\n]*', 0, self.styles['comment'])]

        # PYTHON ______________________________________________________________________________________________________________________
        elif language == "Python":
            keywords = ['and', 'del', 'for', 'is', 'raise', 'assert', 'elif', 'from', 'lambda', 'return', 'break', 'else', 'global', 'not', 'try', 'class', 'except', 'if', 'or', 'while', 'continue', 'exec', 'import', 'pass', 'yield', 'def', 'finally', 'in', 'print']
            rules += [(r'\b%s\b' % w, 0, self.styles['keyword']) for w in keywords]

            preprocs = ['import', 'from']

            rules += [(r'%s' % w, 0, self.styles['preproc']) for w in preprocs]

            rules += [(r'def\:', 0, self.styles['defclass'])]

            braces = ['\{','\}','\(','\)','\[','\]']
            rules += [(r'%s' % w, 0, self.styles['brace']) for w in braces]

            rules += [
                    (r'"[^"\\]*(\\.[^"\\]*)*"', 0, self.styles['literal']),  # Double-quote strings
                    (r"'[^'\\]*(\\.[^'\\]*)*'", 0, self.styles['literal']),  # Single-quote strings
                    (r'\b\d+\b', 0, self.styles['literal']),  # Numbers
                    (r'\#[^\n]*', 0, self.styles['comment'])]

            # LOLCODE ______________________________________________________________________________________________________________________
        elif language == "LOLCODE":
            keywords = ['HAI', 'KTHXBYE', 'VISIBLE', 'GIMMEH', 'I HAS A', 'IM IN YR LOOP', 'IM OUTTA YR LOOP', 'IZ', 'BIGGER THAN', 'UP']
            rules += [(r'\b%s\b' % w, 0, self.styles['keyword']) for w in keywords]

            preprocs = ['CAN HAS']

            rules += [(r'%s' % w, 0, self.styles['preproc']) for w in preprocs]

            rules += [(r'def\:', 0, self.styles['defclass'])]

            braces = ['\{','\}','\(','\)','\[','\]']
            rules += [(r'%s' % w, 0, self.styles['brace']) for w in braces]

            rules += [
                    (r'"[^"\\]*(\\.[^"\\]*)*"', 0, self.styles['literal']),  # Double-quote strings
                    (r"'[^'\\]*(\\.[^'\\]*)*'", 0, self.styles['literal']),  # Single-quote strings
                    (r'\b\d+\b', 0, self.styles['literal']),  # Numbers
                    (r'BTW[^\n]*', 0, self.styles['comment'])]

        # PROLOG ______________________________________________________________________________________________________________________
        elif language == "Prolog":
            keywords = ['block', 'dynamic', 'mode', 'module', 'multifile', 'meta_predicate', 'parallel', 'sequential', 'volatile']
            rules += [(r'\b%s\b' % w, 0, self.styles['keyword']) for w in keywords]

            # in the case of prolog i've used the preproc style to highlight capitals for variables.
            preprocs = [(r'\b[A-Z]+[a-zA-Z]*\b')]

            rules += [(r'%s' % w, 0, self.styles['preproc']) for w in preprocs]

            rules += [(r'def\:', 0, self.styles['defclass'])]

            braces = ['\{','\}','\(','\)','\[','\]']
            rules += [(r'%s' % w, 0, self.styles['brace']) for w in braces]

            rules += [
                    (r'"[^"\\]*(\\.[^"\\]*)*"', 0, self.styles['literal']),  # Double-quote strings
                    (r"'[^'\\]*(\\.[^'\\]*)*'", 0, self.styles['literal']),  # Single-quote strings
                    (r'\b\d+\b', 0, self.styles['literal']),  # Numbers
                    (r'\%[^\n]*', 0, self.styles['comment'])]

        # LISP _______________________________________________________________________________________________________________________
        elif language == "Lisp":
            keywords = ['car','cdr','setq','quote','eval','append','list','cons','atom','listp','null','memberp','nil','t','defun','abs','expt','sqrt','max','min','cond']
            rules += [(r'\b%s\b' % w, 0, self.styles['keyword']) for w in keywords]

            braces = ['\(','\)']
            rules += [(r'%s' % w, 0, self.styles['brace']) for w in braces]

            rules += [
                    (r'"[^"\\]*(\\.[^"\\]*)*"', 0, self.styles['literal']),  # Double-quote strings
                    (r"'[^'\\]*(\\.[^'\\]*)*'", 0, self.styles['literal']),  # Single-quote strings
                    (r'\b\d+\b', 0, self.styles['literal']),  # Numbers
                    (r'\;[^\n]*', 0, self.styles['comment'])]

        # WHITESPACE ____________________________________________________________________________________________________________________
        elif language == "Whitespace":
            # OK, we're gonna do some crazy stuff with this one. Most of it needs to be defined by hand.
            rules += [
                    (r' ', 0, self.styles['wsspace']),
                    (r'\t', 0, self.styles['wstab'])]

        self.rules = [(QtCore.QRegExp(pattern, self.caseSensitivity), index, formatz) for (pattern, index, formatz) in rules]

    def highlightBlock(self, text):
        # Do other syntax formatting
        for expression, nth, format in self.rules:
            index = expression.indexIn(text, 0)

            while index >= 0:
                # We actually want the index of the nth match
                index = expression.pos(nth)
                length = expression.cap(nth).length()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)
        self.setCurrentBlockState(0)

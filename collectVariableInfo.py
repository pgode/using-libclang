#!/usr/bin/env python
""" Usage: call with python. 
"""
  
import sqlite3 as lite
import sys
import clang.cindex
import re #to substitute 
  
  
class Collector_variableinfo:
  conn = None  
  #filename = "F:/_pankaj/Project/example_usinglibclang/abc1.c"
  #-arrarys to store information about variable
  unique_var_names = []
  
  #- arrays to store information about variable definition
  var_defn_name = []
  var_defn_line_no = []
  var_defn_col_no = []
  var_defn_filename = []
  var_defn_origline = []
  
  #-arrays to store information about variable reference. 
  var_name=[]
  var_ref_line_no=[]
  var_ref_col_no=[]
  
  #- as funciton names are not getting captured, so keeping a separate list of functions
  func_names=[]
  func_ref_line = []
  func_ref_col = []
  
  #------------------------------------
  #-- Find all function names only
  #------------------------------------
  def find_functions(self, node, parent, userdata):
      #- CALL_EXPR, FUNCTION_DECL, is_declaration are defined in cindex.py 
      #          in llvm-3.1_src\win\src\tools\clang\bindings\python\clang
      #if node.kind == clang.cindex.CursorKind.FUNCTION_DECL: #gives function definitions
      if node.kind == clang.cindex.CursorKind.CALL_EXPR: #gives function definitions
          self.func_names.append(clang.cindex.Cursor_displayname(node))
          self.func_ref_line.append(node.location.line)
          self.func_ref_col.append(node.location.column)
          #print '--->> Found %s [line=%s, col=%s]' % (
          #        clang.cindex.Cursor_displayname(node), node.location.line, 
          #        node.location.column)
      return 2 # means continue visiting recursively
  
  #------------------------------------
  #-- Insert data row to table.
  #------------------------------------
  def add_entry(self, name, line, column):
    #print " name=%s, line=%s, col=%s" %( name, line, column)  
    self.found_entry = 0
    self.idx = 0
  
    #- match indexed arrays
    for item in self.var_name:    
      if (item == name) and (self.var_ref_line_no[self.idx] == line) and (self.var_ref_col_no[self.idx] == column):
        self.found_entry = 1
        break
      else:
        self.idx = self.idx + 1
  
    #- if duplicate entry w.r.t. name, line, col then skip. else add
    if self.found_entry == 1:
      #print "   name=%s, line=%s, col=%s"  % ( name, line, column)
      #print " -- skipped \n"
      t =0
    else:
      #print "   name=%s, line=%s, col=%s"  % ( name, line, column)
      self.found_func = 0
      #as can't differentiate btwn name is var or func name, so exclude them
      for item in self.func_names:
        if item == name:
          self.found_func = 1
      if self.found_func == 0:
        self.var_name.append(name)
        self.var_ref_line_no.append(line)
        self.var_ref_col_no.append(column)
        #print " -- new item \n"        
      else:
        #print " -- skipped \n"
        t =0
      
  
  #------------------------------------
  #-- Find all variable definitions
  #------------------------------------
  def find_variabledefs(self, node):
      """ find all variable definitions.
      """
      #- gives variable definitions.
      if clang.cindex.Cursor_is_def(node):
          if node.kind == clang.cindex.CursorKind.VAR_DECL or node.kind == clang.cindex.CursorKind.PARM_DECL or node.kind == clang.cindex.CursorKind.STRUCT_DECL or node.kind == clang.cindex.CursorKind.UNION_DECL or node.kind == clang.cindex.CursorKind.ENUM_DECL or node.kind == clang.cindex.CursorKind.FIELD_DECL:
              #print " is variable decl %s at [line=%s, col=%s]" % ( clang.cindex.Cursor_displayname(node), node.location.line, node.location.column)
              self.var_defn_name.append( clang.cindex.Cursor_displayname(node))
              self.var_defn_line_no.append( node.location.line)
              self.var_defn_col_no.append( node.location.column)
              #- classify them as global and local.
  
      # Recurse for children of this node
      for c in node.get_children():
          self.find_variabledefs(c)
  
  #------------------------------------
  #-- Find all variable references
  #------------------------------------
  #def find_variablerefs(node):
  def find_variablerefs(self, node, parent, userdata):
      """ find all variable references.
      """
      #- get all variable references/used
      #if node.kind.is_reference():
      #if node.kind.is_statement() :
      #if (not node.kind.is_invalid()) and (not clang.cindex.Cursor_displayname(node) == "") and (not node.kind == clang.cindex.CursorKind.VAR_DECL) and (not node.kind == clang.cindex.CursorKind.FUNCTION_DECL) and (not node.kind == clang.cindex.CursorKind.CALL_EXPR):
      if not ( (node.kind.is_invalid()) or (clang.cindex.Cursor_displayname(node) == "") or (node.kind == clang.cindex.CursorKind.VAR_DECL) or (node.kind == clang.cindex.CursorKind.FUNCTION_DECL) or (node.kind == clang.cindex.CursorKind.CALL_EXPR) or node.kind == clang.cindex.CursorKind.PARM_DECL or node.kind == clang.cindex.CursorKind.STRUCT_DECL or node.kind == clang.cindex.CursorKind.UNION_DECL or node.kind == clang.cindex.CursorKind.ENUM_DECL or node.kind == clang.cindex.CursorKind.FIELD_DECL  ):
          #print " node=%s=  [line=%s, col=%s] " % (  clang.cindex.Cursor_displayname(node) , node.location.line, node.location.column )
          self.add_entry(clang.cindex.Cursor_displayname(node) , node.location.line, node.location.column)
  
      # Recurse for children of this node
      return 2
      #for c in node.get_children():
      #    find_variablerefs(c)
  
  #-------------------------
  #  create table
  #    - variable info
  #   - variable definitions
  #    - variable reference
  #-------------------------
  def create_tables(self):
    #--- create a table to hold values
    #self.conn.execute('''CREATE TABLE IF NOT EXISTS variable_info
    #       (var_name  TEXT   PRIMARY KEY NOT NULL,
    #        dummy INT
    #       );''')
  
    #print " created table variable_info"
  
	  #- var_defn_id is supposed to be autoincrement, as we want this unique. use this to map to var ref along with name.
    self.conn.execute('''CREATE TABLE IF NOT EXISTS variable_defn_info
           (var_defn_line   INT NOT NULL,
           var_defn_col     INT,
           var_defn_filename_n_path  CHAR(50),
           var_defn_orig_line TEXT,
           var_defn_name TEXT NOT NULL,
           PRIMARY KEY(var_defn_line, var_defn_col, var_defn_filename_n_path) );''')
           #FOREIGN KEY(var_defn_name) REFERENCES variable_info(var_name) );''')
  
    #print " created table variable_def_info"
  
    #- var_defn_id links to var defn id for linking.
    self.conn.execute('''CREATE TABLE IF NOT EXISTS variable_ref_info
           (var_ref_line   INT NOT NULL,
           var_ref_col     INT,
           var_ref_filename_n_path  CHAR(50),
           var_ref_name TEXT NOT NULL,
					 var_ref_orig_line TEXT,
					 var_defn_id  INT,
           PRIMARY KEY(var_ref_line, var_ref_col, var_ref_filename_n_path) );''')
           #FOREIGN KEY(var_ref_name) REFERENCES variable_info(var_name) );''')
    
    #print " created table variable_ref_info"
  
    #print "Variable Table created successfully\n"
  
  
  #------------------------
  #   Returns source line
  #     from file
  #------------------------
  def return_line(self, line_no):
    #fsrc = open( sys.argv[1])
    fsrc = open( self.filename)
    fsrc_lines = fsrc.readlines()
    fsrc.close()
    if line_no > len(fsrc_lines):
      return re.sub('\n', '', fsrc_lines[0].rstrip())
    #print "-lineno=%d" % int(line_no)
    line = fsrc_lines[line_no-1]
    line = re.sub('\n', '', line.rstrip())#remove ()    
    return line
  
  def return_vardefn_id(self, line_no, file_name, v_name):
    t =0
    #query_string = "SELECT var_defn_id, var_defn_line FROM variable_defn_info WHERE var_defn_name=\"" + v_name + "\" AND var_defn_filename_n_path=\"" + file_name + "\" AND var_defn_line <=" + line_no  
    #print " query =%s" % query_string
    #print " ======================"
    #cursor = self.conn.execute()
    #for row in cursor:
    #  print "var_defn_id = ", row[0]
    #  print "var_defn_line = ", row[1]
    #print " ======================"
    #return 1

  
  #-------------------------------------
  #  Table Display- variable information
  #-------------------------------------
  def display_table_var_info(self):
    print "------------------\n print var info \n"
    #cursor = self.conn.execute("SELECT var_name FROM variable_info")
    #for row in cursor:
    #  print "var_name =", row[0]
    print "------------------\n"
  
  #-------------------------------------
  #  Table Display- variable information
  #-------------------------------------
  def display_table_var_defn_info(self):
    #--- display inserted items.  
    print "-------------------\n print var defn info \n"
    cursor = self.conn.execute("SELECT var_defn_line, var_defn_col, var_defn_filename_n_path, var_defn_orig_line, var_defn_name FROM variable_defn_info")
    for row in cursor:
      print "var_defn_line = ", row[0]
      print "var_defn_col = ", row[1]
      print "var_defn_filename_n_path = ", row[2]
      print "var_defn_orig_line = ", row[3]
      print "var_defn_name = ", row[4], "\n"
    print "-------------------\n"
  
  def display_table_var_references(self):
    print "-------------------\n print var ref info \n"
    cursor = self.conn.execute("SELECT var_ref_line, var_ref_col, var_ref_filename_n_path, var_ref_name, var_ref_orig_line FROM variable_ref_info")
    for row in cursor:
      print "var_ref_line = ", row[0]
      print "var_ref_col = ", row[1]
      print "var_defn_filename_n_path = ", row[2]
      print "var_ref_name = ", row[3]
      print "var_ref_orig_line = ", row[4], "\n"
    print "-------------------\n"
  
  
  #-------------------------------------
  #  Table Insert- variable information
  #-------------------------------------
  def insert_var_info_to_table(self):  
    for item in self.var_defn_name:
      found = 0
      for it in self.unique_var_names:
        if item is it:
          found = 1
          break
      #-if item not found, add to unique items
      if found is 0:
        self.unique_var_names.append(item)
  
    #for it in unique_var_names:
      #print "unique names=%s" % it
    #print "----------------"
  
    #-----------------------
    #- add primary variable
    #for i in range(len(self.unique_var_names)):
      #print " var=%s \n" % var_name[i]
      #unique_var_names[i] = re.sub('\(.*\)', '', unique_var_names[i].rstrip())#remove ()
      #print " insert var=%s \n" % var_name[i]
      #--- insert items, i.e. variable defnintion entries
      #print " add information for var %s\n" % unique_var_names[i]
      #insert_string = "INSERT INTO variable_info(var_name) VALUES ('" + self.unique_var_names[i] + "')"
      #self.conn.execute(insert_string);
    
    #print "  Values inserted to var info primary\n"
  
     #-------------------------------------
    #-- add variable definition information 
    for i in range(len(self.var_defn_name)):
      #print " insert defn info for=%s" % i
      insert_string_def = "INSERT INTO variable_defn_info(var_defn_line, var_defn_col, var_defn_filename_n_path, var_defn_orig_line, var_defn_name) VALUES (" + str(self.var_defn_line_no[i]) + " , " + str(self.var_defn_col_no[i]) + ", '" + self.filename + "', '" + self.return_line(self.var_defn_line_no[i]) + "' , '" + self.var_defn_name[i] +  "')"
      #print insert_string_def + "\n"
      self.conn.execute(insert_string_def);
      #conn.execute("INSERT INTO variable_info(var_name, defn_line, defn_col, defn_filename_n_path, defn_orig_line) 
      #            VALUES (1, 1, 'myproject/test_c_proj/test.c', 'bool foo()')", 'foo');
   
    #print "  Values inserted to var defn\n"
  
     #-------------------------------------
    #-- add variable reference information 
    #print " Adding variable references \n"
    for i in range(len(self.var_name)):
      #- insert variable references      
      #print " var_name = %s, filename=%s , varreflineno=%s" % (self.var_name[i], self.filename, self.var_ref_line_no[i])
      #insert_string_ref = "INSERT INTO variable_ref_info(var_ref_line, var_ref_col, var_ref_filename_n_path, var_ref_name, var_ref_orig_line) VALUES (" + str(self.var_ref_line_no[i]) + ", " + str(self.var_ref_col_no[i])  + ", '" + self.filename + "', '" + self.var_name[i] + "', '" + self.return_line(self.var_ref_line_no[i]) + self.return_vardefn_id(self.var_defn_line_no[i], self.filename, self.var_name[i]) + "')"
      insert_string_ref = "INSERT INTO variable_ref_info(var_ref_line, var_ref_col, var_ref_filename_n_path, var_ref_name, var_ref_orig_line) VALUES (" + str(self.var_ref_line_no[i]) + ", " + str(self.var_ref_col_no[i])  + ", '" + self.filename + "', '" + self.var_name[i] + "', '" + self.return_line(self.var_ref_line_no[i]) + "')"
      #print insert_string_ref + "\n"
      self.conn.execute(insert_string_ref);
      #  conn.execute("INSERT INTO variable_ref_info(ref_line, ref_col, ref_filename_n_path, variable_name) \
      #                VALUES (8, 5, 'myproject/test_c_proj/test.c', 'foo')");
    #print " -----\n"
  
    #-- commit values
    #print " values inserted \n"  
    self.conn.commit()
  
  #-------------------------------------
  #-- Collect variable Information
  #-------------------------------------
  def collect_variable_information(self):
    #- Bug: while collecting type references, functions are also present in list
    #- so collecting them separately and then will be filtering them out.
    clang.cindex.Cursor_visit(
            self.tu.cursor,
            clang.cindex.Cursor_visit_callback(self.find_functions),
            None)
  
    #-- Find variable definition
    self.find_variabledefs(self.tu.cursor)
  
    #print " ------------------------"
    #-- Find variable references
    #find_variablerefs(tu.cursor)
    clang.cindex.Cursor_visit(
            self.tu.cursor,
            clang.cindex.Cursor_visit_callback(self.find_variablerefs),
            None)
    
    #print " added typerefs \n"
    #for i in range(len(self.var_name)):
    #  print " name=%s, line=%s, col=%s\n" % (self.var_name[i], self.var_ref_line_no[i], self.var_ref_col_no[i] )
    #print "\n===================\n"
  
  
  #------------------------------
  #--  Display Table information
  #------------------------------
  def display_table_info(self):
    #self.display_table_var_info()
    self.display_table_var_defn_info()
    self.display_table_var_references()
  
  #-------------------------------------
  #-- Main control 
  #-------------------------------------
  #----- COLLECT INFORMATION.
  #-- create index information
  def collect(self, in_filename, out_dbpath):	
    try:
      #print " INPUTs: var info collection: file=%s, dbpath=%s" % (in_filename, out_dbpath)
      self.filename = in_filename
      index = clang.cindex.Index.create()
      self.tu = index.parse( self.filename)
      #print 'Translation unit:', tu.spelling
      #self.conn = lite.connect('../viewvc-1.2-dev-20130212/db/variables_data.db')
      self.conn = lite.connect(out_dbpath)
      self.conn.execute('pragma foreign_keys = on')
      #print "Opened database successfully"
  
      #-variable info table creation.
      self.create_tables()
  
      #-collect information about variables
      self.collect_variable_information()
  
      #- insert variable information to database 
      self.insert_var_info_to_table()
  
      #- print variable information in table.
      #self.display_table_info()
  
    #- exception handling
    except lite.Error,e:
      print "Error %s:" % e.args[0]
      sys.exit(1)
  
    #- do in the end
    finally:
      if self.conn:
        self.conn.close()
  
  
  

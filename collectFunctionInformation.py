import sqlite3 as lite
import sys
import clang.cindex
import re #to substitute 

class Collector_funcinfo:
  #-arrarys to store information about function definitions
    conn = None
  filename = "F:/Pankaj/Project/_package/myproject/test_c_proj/test_variables.c"
  func_defn = []
  func_defn_line_no = []
  func_defn_col_no = []
  func_defn_filename = []
  func_defn_origline = []

  #-arrays to store information about function calls. 
  func_call_name=[]
  func_ref_line_no=[]
  func_ref_col_no=[]

  #------------------------
  #  Visitor
  #   function definitions
  #------------------------
  def funcdefn_visitor(self, node, parent, userdata):
    # You might want to change the test here
    if node.location.file != None:
      if node.location.file.endswith("/stdio.h"):
        print "Skipping 'stdio.h'"
        # Continue with next sibling
        return 1
    
    #- CALL_EXPR, FUNCTION_DECL, is_declaration are defined in cindex.py 
		#					in llvm-3.1_src\win\src\tools\clang\bindings\python\clang
    if node.kind == clang.cindex.CursorKind.FUNCTION_DECL: #gives function definitions
      self.func_defn.append(clang.cindex.Cursor_displayname(node))
      self.func_defn_line_no.append(node.location.line)
      self.func_defn_col_no.append(node.location.column)
      print 'Found %s [line=%s, col=%s]' % (
              clang.cindex.Cursor_displayname(node), node.location.line, 
						node.location.column)
    return 2 # means continue visiting recursively
  #------------------------
  #  Visitor
  #   function calls
  #------------------------
  def funcreferences_visitor(self, node, parent, userdata):
    #- CALL_EXPR, FUNCTION_DECL, is_declaration are defined in cindex.py 
		#					in llvm-3.1_src\win\src\tools\clang\bindings\python\clang
    if node.kind == clang.cindex.CursorKind.CALL_EXPR: #gives function calls
      self.func_call_name.append(clang.cindex.Cursor_displayname(node))
      self.func_ref_line_no.append(node.location.line)
      self.func_ref_col_no.append(node.location.column)
      #print 'Found %s [line=%s, col=%s]' % (
      #        clang.cindex.Cursor_displayname(node), node.location.line, 
  		#				node.location.column)
    return 2 # means continue visiting recursively

  #------------------------
  #   Returns source line
  #     from file
  #------------------------
  def return_line(self, line_no):
    #fsrc = open( sys.argv[1])
    fsrc = open( self.filename)
    fsrc_lines = fsrc.readlines()
    fsrc.close()
    #print "-lineno=%d" % int(line_no)
    line = fsrc_lines[line_no-1]
    return line

  #--------------------------------
  #   Print collected information
  #--------------------------------
  def print_func_information(self):
    for i in range(len(self.func_defn)):
      print " func=%s \n" % self.func_defn[i]
    print " -----\n"


  #---------------------------
  #  Use libclang 
  #    to collect information
  #---------------------------
  def collect_func_information(self):
    #----- COLLECT INFORMATION.
    #-- create index information
    index = clang.cindex.Index.create()
    #tu = index.parse(sys.argv[1])
    
    #tu = index.parse(self.filename, ".", "-x c-header -target i386-pc-win32", )
    tu = index.parse(self.filename)#works
	  #-- link cursor visitor to call back to give function definitions
    clang.cindex.Cursor_visit(
	          tu.cursor,
	          clang.cindex.Cursor_visit_callback(self.funcdefn_visitor),
	          None)
  	#-- link cursor visitor to call back to give function references
    clang.cindex.Cursor_visit(
	          tu.cursor,
	          clang.cindex.Cursor_visit_callback(self.funcreferences_visitor),
	          None)
  	#-print_func_information()
  

  #-------------------------
  #  create tables
  #		- function info
  #   - function references
  #-------------------------
  def create_tables(self):
  	#--- create a table to hold values
    self.conn.execute('''CREATE TABLE IF NOT EXISTS function_info
          (func_name	TEXT 		NOT NULL,
           defn_line 	INT    	NOT NULL,
           defn_col 	INT,
           defn_filename_n_path	CHAR(50),
           defn_orig_line TEXT, 
					 PRIMARY KEY(func_name, defn_line, defn_filename_n_path) );''')

    #print " created table function_info"

    self.conn.execute('''CREATE TABLE IF NOT EXISTS function_ref_info
                 (ref_line 	INT 	NOT NULL,
                  ref_col 		INT,
                  ref_filename_n_path	CHAR(50),
                  function_name TEXT,
									ref_orig_line TEXT,
									PRIMARY KEY(ref_line, ref_col, ref_filename_n_path) 
                  FOREIGN KEY(function_name) REFERENCES function_info(func_name) );''')
	
    #print " created table function_ref_info"

    #print "Table created successfully\n"


  #-------------------------------------
  #  Table Display- function information
  #-------------------------------------
  def display_table_func_info(self):
  	#--- display inserted items.	
    print "-------------------\n"
    cursor = self.conn.execute("SELECT func_name, defn_line, defn_col, defn_filename_n_path, defn_orig_line FROM function_info")
    for row in cursor:
      print "func_name = ", row[0]
      print "defn_line = ", row[1]
      print "defn_col = ", row[2]
      print "defn_filename_n_path = ", row[3]
      print "defn_orig_line = ", row[4], "\n"
      print "-------------------\n"

  def display_table_func_references(self):
    cursor = self.conn.execute("SELECT ref_line, ref_col, ref_filename_n_path, function_name, ref_orig_line FROM function_ref_info")
    for row in cursor:
      print "ref_line = ", row[0]
      print "ref_col = ", row[1]
      print "defn_filename_n_path = ", row[2]
      print "func_name = ", row[3]
      print "ref_orig_line =", row[4], "\n"
    print "-------------------\n"


  #-------------------------------------
  #  Table Insert- function information
  #-------------------------------------
  def insert_func_info_to_table(self):
    for i in range(len(self.func_defn)):
      #print " func=%s \n" % func_defn[i]
      self.func_defn[i] = re.sub('\(.*\)', '', self.func_defn[i].rstrip())#remove ()
      #print " insert func=%s \n" % func_defn[i]

      #--- insert items, i.e. function defnintion entries
      #print " add information for func %s\n" % self.func_defn[i]
      insert_string = "INSERT INTO function_info(func_name, defn_line, defn_col, defn_filename_n_path, defn_orig_line) VALUES ('" + self.func_defn[i] + "', " + str(self.func_defn_line_no[i]) + ", " + str(self.func_defn_col_no[i]) + ", '" + self.filename + "', '" + self.return_line(self.func_defn_line_no[i]) + "')"
      self.conn.execute(insert_string);
      #conn.execute("INSERT INTO function_info(func_name, defn_line, defn_col, defn_filename_n_path, defn_orig_line) 
      #			      VALUES ('foo', 1, 1, 'myproject/test_c_proj/test.c', 'bool foo()')");

    for i in range(len(self.func_call_name)):
      #--- insert function references
      insert_string_ref = "INSERT INTO function_ref_info(ref_line, ref_col, ref_filename_n_path, function_name, ref_orig_line) VALUES (" + str(self.func_ref_line_no[i]) + ", " + str(self.func_ref_col_no[i])  + ", '" + self.filename + "', '" + self.func_call_name[i] + "', '" + self.return_line(self.func_ref_line_no[i])  + "')"
      #print insert_string_ref + "\n"
      self.conn.execute(insert_string_ref);
      #	conn.execute("INSERT INTO function_ref_info(ref_line, ref_col, ref_filename_n_path, function_name) \
      #					      VALUES (8, 5, 'myproject/test_c_proj/test.c', 'foo')");
    #print " -----\n"

    #-- commit values
    #print " values inserted \n"	
    self.conn.commit()

  #-----------------
  #   MAIN FLOW.
  #-----------------
  def collect(self, in_filename, out_dbpath):
    try:
      self.filename = in_filename      
      #conn = lite.connect('../viewvc-1.2-dev-20130212/db/functions_data.db')
      self.conn = lite.connect(out_dbpath)
      self.conn.execute('pragma foreign_keys = on')
      #print "Opened database successfully"

      #-function info table creation.
      self.create_tables()

      #-collect information about functions
      self.collect_func_information()

      #- insert function information to database 
      self.insert_func_info_to_table()

      #- print function information in table.
      self.display_table_func_info()
      self.display_table_func_references()

      #- exception handling
    except lite.Error,e:
      print "Error %s:" % e.args[0]
      sys.exit(1)

    #- do in the end
    finally:
      if self.conn:
        self.conn.close()





	#--- insert items.
	#-- 1. add foo
#	print " add information for func foo\n"
#	conn.execute("INSERT INTO function_info(func_name, defn_line, defn_col, defn_filename_n_path, defn_orig_line) \
#					      VALUES ('foo', 1, 1, 'myproject/test_c_proj/test.c', 'bool foo()')");
		#- add references
#	conn.execute("INSERT INTO function_ref_info(ref_line, ref_col, ref_filename_n_path, function_name) \
#					      VALUES (8, 5, 'myproject/test_c_proj/test.c', 'foo')");
#	conn.execute("INSERT INTO function_ref_info(ref_line, ref_col, ref_filename_n_path, function_name) \
#					      VALUES (10, 9, 'myproject/test_c_proj/test.c', 'foo')");	
#	conn.execute("INSERT INTO function_ref_info(ref_line, ref_col, ref_filename_n_path, function_name) \
#					      VALUES (16, 9, 'myproject/test_c_proj/test.c', 'foo')");	


	#-- 2. add bar
#	print " add information for func bar\n"
#	conn.execute("INSERT INTO function_info(func_name, defn_line, defn_col, defn_filename_n_path, defn_orig_line) \
#					      VALUES ('bar', 6, 1, 'myproject/test_c_proj/test.c', 'bool bar()')");
		#- add references
#	conn.execute("INSERT INTO function_ref_info(ref_line, ref_col, ref_filename_n_path, function_name) \
#					      VALUES (15, 5, 'myproject/test_c_proj/test.c', 'bar')");
#	conn.execute("INSERT INTO function_ref_info(ref_line, ref_col, ref_filename_n_path, function_name) \
#					      VALUES (17, 9, 'myproject/test_c_proj/test.c', 'bar')");	


	#-- 3. add main
#	print " add information for func main\n"
#	conn.execute("INSERT INTO function_info(func_name, defn_line, defn_col, defn_filename_n_path, defn_orig_line) \
#					      VALUES ('main', 13, 1, 'myproject/test_c_proj/test.c', 'int main()')");
		#- add references
#	conn.execute("INSERT INTO function_ref_info(ref_line, ref_col, ref_filename_n_path, function_name) \
#					      VALUES (0, 0, 'myproject/test_c_proj/test.c', 'main')");


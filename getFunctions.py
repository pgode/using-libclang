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
  

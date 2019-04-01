
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
  


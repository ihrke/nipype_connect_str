nipype_connect_str
==================

tiny grammar to allow for a nicer connection string of nodes in workflow


instead of writing 

~~~python
workflow.connect([ (infosource, datasource, [('code', 'code')]),
                   (infosource, datasink,   [('func', 'func')]),
                   (datasource, reg_func_struct, [('func', 'in_file'),
                                                  ('struct', 'reference')]),
                   (reg_func_struct, datasink, [('out_matrix_file, 'matrix'),
                                                ('out_file', 'registered')])
                 ])

~~~

you can now write more clearly

~~~~
workflow.connect(eval(nipype_connect_str(
"""
infosource(code) -> datasource(code|func) -> datasink(func);
datasource(func,struct)  -> reg_func_struct(in_file,reference | out_matrix_file,out_file)
                         -> datasink(matrix,registered)
"""
~~~

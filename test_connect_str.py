from nipype_connect_str import *

tests=[
    """
    node1(output1, output2) -> node2(input1, input2 | out1) -> node3(input);
    node1(output1, ich) -> node2(input1, input2|auch) -> node3(input)
    """,
    """
    node1(|fails) -> hopefully
    """,
    """
    node1(fails) -> hopefully
    """,
    """
    node1(out) -> node2(in) -> node3(in3)
    """,
    """
    test fails
    """,
    """
    overlaynode(out_file) -> slicer(in_file|out_file) -> datasink(renderedimg)
    """,
    """
    overlaynode(out_file) -> slicer(in_file, reference|out_file) -> datasink(renderedimg)    
    """
    ]

for testidx,test in enumerate(tests):
    try:
        print "Test %i"%(testidx+1)
        print "-------"
        print test
        print "-----------------------"
        strlist=connect_str(test)
        print strlist
    except ParseException, pe:
        print pe

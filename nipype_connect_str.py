"""
nipype_connect_str.py
Mon May 27 10:32:50 CEST 2013
<mittner@uva.nl>
"""
from pyparsing import (Word, Optional, OneOrMore, Group, ParseException,
                       alphas, Literal, ZeroOrMore, Or, Suppress,
                       delimitedList, FollowedBy, StringEnd)


def check_numconnections(connects):
    for connect in connects.connects:
        nodes=[connect.headnode]+list(connect.middlenodes)+[connect.tailnode]
        for i in range(len(nodes)-1):
            if len(nodes[i].outputnames)!=len(nodes[i+1].inputnames):
                raise ParseException("inputs/outputs do not match (%s -> %s)"%(nodes[i].nodename,
                                                                               nodes[i+1].nodename))


def parse_connection_str(connstr):
    ## Grammar for connection syntax
    digits="0123456789"
    othervalid="_."
    identifier= Word(alphas+digits+othervalid)
    nodename=identifier.setResultsName('nodename')

    outputnames = delimitedList( identifier ).setResultsName('outputnames')
    inputnames  = delimitedList( identifier ).setResultsName('inputnames')

    # middle nodes have both inputs and outputs
    middlenode= Group( nodename + Suppress('(') + inputnames
                       + Optional( "|" + outputnames)
                       + Suppress(")") ).setResultsName('middlenode')
    # first node has only outputs
    headnode = (nodename + Suppress("(") + outputnames
                + Suppress(")")).setResultsName('headnode')
    # last node has only inputs
    tailnode = (nodename + Suppress("(") + inputnames
                + Suppress(")")).setResultsName('tailnode')

    # connect head -> [middle ->] tail
    connect= Group( headnode
                    + Group(ZeroOrMore(Suppress("->") \
                        + middlenode + FollowedBy("->") )).setResultsName('middlenodes')
                    + Suppress("->")+tailnode).setResultsName('nodes')

    connectlist = Group( connect + ZeroOrMore( Suppress(";")\
                        + connect )).setResultsName('connects')

    parsed=connectlist.parseString(connstr)
    check_numconnections(parsed)
    return parsed

def nipype_connect_str(connection_str):
    """
    Connect nodes in the pipeline using a string of the form::

       node1(output1) -> node2(input2 | output2) -> node3(input3)

    where node1, node2 etc. are the node's variable name.

    The return value is a string-representation of a list that can be passed
    (after eval()) to a workflow.connect( eval( connectstr) ) call.

       self.connect([ (node1, node2, [(output1, input2)]),
                     (node2, node3, [(output2, input3)]) ])
    """
    connection_list=parse_connection_str(connection_str)
    start="""["""
    end  ="""\n]"""
    code =""""""
    for connect in connection_list.connects:
        nodes=[connect.headnode]+list(connect.middlenodes)+[connect.tailnode]
        for i in range(len(nodes)-1):
            onode=nodes[i]
            inode=nodes[i+1]
            code+="""\n({onode},{inode},["""\
              .format(inode=inode.nodename, onode=onode.nodename)
        for oarg,iarg in zip(onode.outputnames,inode.inputnames):
            code+="""('{oarg}','{iarg}'),""".format(iarg=iarg,oarg=oarg)
        code+="""]),"""
    code=start+code+end
    return code


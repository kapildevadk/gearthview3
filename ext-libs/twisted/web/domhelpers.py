# -*- test-case-name: twisted.web.test.test_domhelpers -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
A library for performing interesting tasks with DOM objects.
"""

import string
from typing import Any, Dict, List, Optional, Union

from twisted.web.microdom import getElementsByTagName, escape, unescape


class NodeLookupError(Exception):
    pass


def substitute(node: microdom.Node, subs: Dict[str, str]) -> None:
    """
    Look through the given node's children for strings, and
    attempt to do string substitution with the given parameter.
    """
    for child in node.childNodes:
        if hasattr(child, "nodeValue") and child.nodeValue:
            child.replaceData(
                0, len(child.nodeValue), child.nodeValue % subs
            )
        substitute(child, subs)


def _get_node(
    node: microdom.Node, node_id: str, node_attrs: Tuple[str, ...]
) -> Optional[microdom.Node]:
    """
    (internal) Get a node with the specified node_id as any of the class,
    id or pattern attributes.
    """
    if hasattr(node, "hasAttributes") and node.hasAttributes():
        for node_attr in node_attrs:
            if str(node.getAttribute(node_attr)) == node_id:
                return node
    if node.hasChildNodes():
        if hasattr(node.childNodes, "length"):
            length = node.childNodes.length
        else:
            length = len(node.childNodes)
        for child_num in range(length):
            result = _get_node(node.childNodes[childNum], node_id, node_attrs)
            if result:
                return result
    return None


def get_node(node: microdom.Node, node_id: str) -> microdom.Node:
    """
    Get a node with the specified node_id as any of the class,
    id or pattern attributes. If there is no such node, raise
    L{NodeLookupError}.
    """
    result = _get_node(node, node_id, ("id", "class", "model", "pattern"))
    if result:
        return result
    raise NodeLookupError(node_id)


def get_node_if_exists(node: microdom.Node, node_id: str) -> Optional[microdom.Node]:
    """
    Get a node with the specified node_id as any of the class,
    id or pattern attributes.  If there is no such node, return
    C{None}.
    """
    return _get_node(node, node_id, ("id", "class", "model", "pattern"))


def get_and_clear_node(node: microdom.Node, node_id: str) -> Optional[microdom.Node]:
    """Get a node with the specified node_id as any of the class,
    id or pattern attributes. If there is no such node, raise
    L{NodeLookupError}. Remove all child nodes before returning.
    """
    result = get_node(node, node_id)
    if result:
        clear_node(result)
    return result


def clear_node(node: microdom.Node) -> None:
    """
    Remove all children from the given node.
    """
    node.childNodes[:] = []


def locate_nodes(
    node_list: Union[microdom.Node, List[microdom.Node]],
    key: str,
    value: str,
    no_nesting: bool = True,
) -> List[microdom.Node]:
    """
    Find subnodes in the given node where the given attribute
    has the given value.
    """
    return_list = []
    if not isinstance(node_list, list):
        return locate_nodes(node_list.childNodes, key, value, no_nesting)
    for child_node in node_list:
        if not hasattr(child_node, "getAttribute"):
            continue
        if str(child_node.getAttribute(key)) == value:
            return_list.append(child_node)
            if no_nesting:
                continue
        return_list.extend(
            locate_nodes(child_node, key, value, no_nesting)
        )
    return return_list


def super_set_attribute(
    node: microdom.Node, key: str, value: str
) -> None:
    if not hasattr(node, "setAttribute"):
        return
    node.setAttribute(key, value)
    if node.hasChildNodes():
        for child in node.childNodes:
            super_set_attribute(child, key, value)


def super_prepend_attribute(
    node: microdom.Node, key: str, value: str
) -> None:
    if not hasattr(node, "setAttribute"):
        return
    old = node.getAttribute(key)
    if old:
        node.setAttribute(key, value + "/" + old)
    else:
        node.setAttribute(key, value)
    if

"""Small, offline binary FBX reader/writer. Keeps original typed properties.

This project uses FBX 7400 (32-bit node records); 7500+ is supported as well.
No third-party libraries beyond the already-installed NumPy are required.
"""
from dataclasses import dataclass, field
from pathlib import Path
import struct
import zlib
import numpy as np


@dataclass
class Prop:
    kind: str
    value: object


@dataclass
class Node:
    name: str
    props: list = field(default_factory=list)
    children: list = field(default_factory=list)

    def child(self, name):
        return next((c for c in self.children if c.name == name), None)

    def values(self):
        return [p.value for p in self.props]


class FBX:
    def __init__(self, path):
        self.source = Path(path)
        self.data = self.source.read_bytes()
        if self.data[:23] != b'Kaydara FBX Binary  \x00\x1a\x00':
            raise ValueError('Expected a binary FBX file')
        self.version = struct.unpack_from('<I', self.data, 23)[0]
        self.wide = self.version >= 7500
        self.node_size = 25 if self.wide else 13
        self.header_format = '<QQQB' if self.wide else '<IIIB'
        self.nodes = []
        offset = 27
        while offset < len(self.data):
            node, offset = self._read_node(offset)
            if node is None:
                break
            self.nodes.append(node)
        self.footer = self.data[offset:]

    def _read_node(self, offset):
        end, count, plen, nlen = struct.unpack_from(self.header_format, self.data, offset)
        offset += self.node_size
        if not end:
            return None, offset
        if end > len(self.data):
            raise ValueError('Node extends beyond EOF')
        name = self.data[offset:offset+nlen].decode('utf8')
        offset += nlen
        props = []
        for _ in range(count):
            kind = chr(self.data[offset])
            offset += 1
            if kind in 'YCLFDI':
                fmt = {'Y':'h','C':'?','L':'q','F':'f','D':'d','I':'i'}[kind]
                value = struct.unpack_from('<'+fmt, self.data, offset)[0]
                offset += struct.calcsize(fmt)
            elif kind in 'SR':
                size = struct.unpack_from('<I', self.data, offset)[0]
                offset += 4
                value = self.data[offset:offset+size]
                offset += size
                if kind == 'S':
                    value = value.decode('utf8')
            elif kind in 'fdlibc':
                count_a, encoding, size = struct.unpack_from('<III', self.data, offset)
                offset += 12
                value = self.data[offset:offset+size]
                offset += size
                if encoding:
                    value = zlib.decompress(value)
                dtype = {'f':'<f4','d':'<f8','l':'<i8','i':'<i4','b':'u1','c':'u1'}[kind]
                value = np.frombuffer(value, dtype=dtype).copy()
                if len(value) != count_a:
                    raise ValueError('Array length mismatch')
            else:
                raise ValueError('Unsupported FBX property '+kind)
            props.append(Prop(kind, value))
        children = []
        while offset < end-self.node_size:
            child, offset = self._read_node(offset)
            if child is None:
                break
            children.append(child)
        return Node(name, props, children), end

    def root(self, name):
        return next(n for n in self.nodes if n.name == name)

    @staticmethod
    def _pack_prop(prop):
        k, v = prop.kind, prop.value
        out = k.encode('ascii')
        if k in 'YCLFDI':
            return out + struct.pack('<'+{'Y':'h','C':'?','L':'q','F':'f','D':'d','I':'i'}[k], v)
        if k in 'SR':
            raw = v.encode('utf8') if k == 'S' else v
            return out+struct.pack('<I',len(raw))+raw
        dtype = {'f':'<f4','d':'<f8','l':'<i8','i':'<i4','b':'u1','c':'u1'}[k]
        raw = np.asarray(v, dtype=dtype).tobytes()
        compressed = zlib.compress(raw, 6)
        return out+struct.pack('<III',len(v),1,len(compressed))+compressed

    def _pack_node(self, node, start):
        name = node.name.encode('utf8')
        raw_props = b''.join(self._pack_prop(p) for p in node.props)
        current = start + self.node_size + len(name) + len(raw_props)
        children = []
        for child in node.children:
            raw = self._pack_node(child, current)
            children.append(raw)
            current += len(raw)
        # FBX leaf nodes with no children have no terminal null record.
        if node.children:
            children.append(b'\x00'*self.node_size)
            current += self.node_size
        header = struct.pack(self.header_format,current,len(node.props),len(raw_props),len(name))
        return header+name+raw_props+b''.join(children)

    def save(self, path):
        parts = [self.data[:27]]
        current = 27
        for node in self.nodes:
            raw = self._pack_node(node,current)
            parts.append(raw)
            current += len(raw)
        parts.append(b'\x00'*self.node_size)
        current += self.node_size
        # Preserve both footer signatures and rebuild its alignment padding.
        if len(self.footer) >= 156:
            signature = self.footer[:16]
            version_and_tail = self.footer[-140:]
            parts.append(signature)
            current += 16
            # The original Blender FBX reserves 16 zero bytes before alignment.
            parts.append(b'\x00'*(16+((-current) % 16)))
            parts.append(version_and_tail)
        else:
            parts.append(self.footer)
        Path(path).write_bytes(b''.join(parts))


def N(name, *values, children=None):
    props = []
    for value in values:
        if isinstance(value, Prop): props.append(value)
        elif isinstance(value, str): props.append(Prop('S',value))
        elif isinstance(value, float): props.append(Prop('D',value))
        elif isinstance(value, int): props.append(Prop('I',value))
        else: raise TypeError(type(value))
    return Node(name,props,children or [])


def P(name, ptype, label, *values, flags='A'):
    return N('P',name,ptype,label,flags,*values)


def properties(node):
    ps = node.child('Properties70')
    return {p.props[0].value:p.values()[4:] for p in ps.children} if ps else {}



from ast import Index
import os
import hashlib
import zlib

def init(repo):
    """ Crea un directorio para el repositorio y lo inicializa con un archivo .git"""
    os.mkdir(repo)
    os.mkdir(os.path.join(repo, '.git'))
    for name in ['objects', 'refs', 'refs/heads']:
        os.mkdir(os.path.join(repo, '.git', name))
    write_file(os.path.join(repo, '.git', 'HEAD'),
               b'ref: refs/heads/master')
    print('Initialized empty repository: {}'.format(repo))


def hash_object(data, obj_type, write=True):
    """ Dado el dato del objeto, crea un hash y lo escribe. si "write" es True. retorna el objeto con un string hexadecimal hasheado en SHA-1 """

    header = '{} {}'.format(obj_type, len(data).encode())
    full_data = header + b'\x00' + data
    sha1 = hashlib.sha1(full_data).hexdigest()
    if write:
        path = os.path.join('.git', 'objects', sha1[:2], sha1[2:])
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            write_file(path, zlib.compress(full_data))
    return sha1


# Informacion para UNA entrada en el indice de git (.git/index)
IndexEntry = collections.namedtuple('IndexEntry',[
    'ctime_s', 'ctime_n', 'mtime_s', 'mtime_n', 'dev', 'ino', 'mode', 'uid', 'gid', 'size', 'sha1', 'flags', 'path',
])

def read_index():
    """ Lee los archivos del indice de git y retorna una lista de los objetos IndexEntry """
    try:
        data = read_file(os.path.join('.git', 'index'))
    except FileNotFoundError:
        return []
    digest = hashlib.sha1(data[:-20]).digest()
    assert digest == data[-20:], 'invalid index checksum'
    signature, version, num_entries = struct.unpack('!4sLL', data[:12])
    assert signature == b'DIRC', \
        'invalid index signature {}'.format(signature)
    assert version == 2, 'unknown index version {}'.format(version)
    entry_data = data[12:-20]
    entries = []
    i = 0
    while i + 6 < len(entry_data):
        fields_end = i + 62
        fields = struct.unpack('!LLLLLLLLLL20sH',
                                entry_data[i:fields_end])
        path_end = entry_data.index(b'\x00', fields_end)
        path = entry_data[fields_end:path_end]
        entry = IndexEntry(*(fields + (path.decode(),)))
        entries.append(entry)
        entry_len = ((62 + len(path) + 8) // 8) * 8
        i += entry_len
    assert len(entries) == num_entries
    return entries
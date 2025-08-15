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
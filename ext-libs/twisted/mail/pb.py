# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

from twisted.spread import pb
from twisted.spread import banana
import os

class Maildir(pb.Referenceable):
    """
    A maildir implementation for Twisted Perspective Broker.
    """
    def __init__(self, directory, root_directory):
        self.virtual_directory = directory
        self.root_directory = root_directory
        self.directory = os.path.join(root_directory, directory)

    @property
    def new_messages(self):
        """
        List of new messages in the maildir.
        """
        return self._list_files('new')

    @property
    def cur_messages(self):
        """
        List of current messages in the maildir.
        """
        return self._list_files('cur')

    def _list_files(self, folder):
        """
        List files in the given folder.
        """
        try:
            return os.listdir(os.path.join(self.directory, folder))
        except FileNotFoundError:
            return []

    def get_folder_message(self, folder, name):
        """
        Get the message content in the given folder and name.
        """
        if '/' in name:
            raise IOError("can only open files in '%s' directory'" % folder)
        filepath = os.path.join(self.directory, folder, name)
        if not os.path.isfile(filepath):
            raise IOError("file not found")
        with open(filepath) as fp:
            return fp.read()

    def delete_folder_message(self, folder, name):
        """
        Delete the message in the given folder and name.
        """
        if '/' in name:
            raise IOError("can only delete files in '%s' directory'" % folder)
        old_filepath = os.path.join(self.directory, folder, name)
        if not os.path.isfile(old_filepath):
            raise IOError("file not found")
        new_filepath = os.path.join(self.root_directory, '.Trash', folder, name)
        os.rename(old_filepath, new_filepath)

    def get_sub_folder(self, name):
        """
        Get the subfolder with the given name.
        """
        if name[0] == '.':
            raise IOError("subfolder name cannot begin with a '.'")
        name = name.replace('/', ':')
        if self.virtual_directory == '.':
            name = '.'+name
        else:
            name = self.virtual_directory+':'+name
        if not self._is_sub_folder(name):
            raise IOError("not a subfolder")
        return Maildir(name, self.root_directory)

    def _is_sub_folder(self, name):
        """
        Check if the given name is a subfolder.
        """
        sub_folder_path = os.path.join(self.root_directory, name)
        if not os.path.isdir(sub_folder_path):
            return False
        maildirfolder_path = os.path.join(sub_folder_path, 'maildirfolder')
        return not os.path.isfile(maildirfolder_path)

class MaildirCollection(pb.Referenceable):
    """
    A collection of maildirs.
    """
    def __init__(self, root):
        if not os.path.isdir(root):
            raise ValueError("root directory not found")
        self.root = root

    def get_sub_folders(self):
        """
        List of subfolders in the collection.
        """
        return self._list_folders(self.root)

    def get_sub_folder(self, name):
        """
        Get the subfolder with the given name.
        """
        folder_path = os.path.join(self.root, name)
        if not self._is_sub_folder(folder_path):
            raise IOError("not a subfolder")
        return Maildir('.', folder_path)

    def _list_folders(self, root):
        """
        List folders in the given root.
        """
        return [d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d))]

    def _is_sub_folder(self, folder_path):
        """
        Check if the given path is a subfolder.
        """
        return os.path.isdir(folder_path) and \
            os.path.isfile(os.path.join(folder_path, 'maildirfolder'))

class MaildirBroker(pb.Broker):
    """
    A broker for maildir RPC calls.
    """
    def proto_get_collection(self, requestID, name, domain, password):
        """
        Handle RPC call for getting a collection.
        """
        collection = self._get_collection(name, domain, password)
        if collection is None:
            self.sendError(requestID, "permission denied")
        else:
            self.sendAnswer(requestID, collection)

    def _get_collection(self, name, domain, password):
        """
        Get the collection for the given name, domain, and password.
        """
        if domain not in self.domains:
            return None

import sublime
import sublime_plugin
import os

try:
  from FileList.file_list import FileList, get_short_path, open_file
  from QuickSearchEnhanced import quick_search
  from StatusMessage import status_message
except ImportError as error:
  sublime.error_message("Dependency import failed; please read readme for " +
   "FolderFiles plugin for installation instructions; to disable this " +
   "message remove this plugin; message: " + str(error))
  raise error

class FolderFiles():
  def __init__(self, path, open = None, preview = None, status = '',
    list_args = {}, callers = [], on_create = None):

    self.updown_path = self.path = path
    self.open = open
    self.callers = callers
    self.list_args = list_args
    self.status = status
    self.preview = preview
    self.on_create = on_create
    self.status_view = None

  def get_status(self):
    return self.status

  def get_files(self):
    files = []
    for file_name in os.listdir(self.path):
      files.append([self.path + '/' +file_name, file_name])

    return files

  def get_path(self):
    return self.path

  def show(self):
    self.status_view = sublime.active_window().active_view()
    self._set_status()
    self._create_list().show()

  def goto(self, path):
    if self.updown_path != None and path != self.updown_path[0:len(path)]:
      self.updown_path = path

    self.path = path
    self.list.refresh()
    self._set_status()

  def goto_up(self):
    self.goto(os.path.dirname(self.path))

  def goto_down(self):
    if self.updown_path == None:
      return

    new_path = self.updown_path[0:len(self.path)]
    next_part = self.updown_path[len(self.path) + 1:].split('/')[0]
    if next_part != '':
      new_path = (new_path + '/' + next_part)

    if new_path == self.path:
      return

    self.goto(new_path)

  def get_current_path(self):
    return self.path

  def _open(self, result):
    path = result.get_current_value()
    if path == None:
      return False

    if os.path.isdir(path):
      self.goto(path)

      # have to recreate list because current list is closed by sublime
      self.list_args['text'] = None
      self._create_list().show()

      return True

    return False

  def _preview(self, panel):
    if self.preview == False:
      self.status_view = sublime.active_window().active_view()
      return True

    self.status_view = self.list.preview_file(panel)
    self._set_status()

    if self.preview != None and self.preview(panel) == True:
      return True

    return True

  def _set_status(self):
    if self.status_view == None:
      return

    path, is_short = get_short_path(self.path)
    if is_short and path == '':
      path = '@'

    status_message.set(self.status_view, 'folder_files_status',
      self.status + path)

  def _create_list(self):
    args = {
      "callback": self.get_files,
      "open": self._open,
      "preview": self._preview,
      "open_if_one_file": False,
      "callers": [['folder_files', self]] + self.callers,
      "on_create": self.on_create,
    }

    list_args = dict(list(self.list_args.items()) + list(args.items()))
    self.list = FileList(**list_args)

    return self.list

def open_file_or_folder(path, args = {}):
  if os.path.isdir(path):
    args['path'] = path
    return FolderFiles(**args).show()

  return open_file(path)

def open_file_or_folder_by_panel(panel, value = None, args = {}):
  path = value or panel.get_current_value()
  if path == None:
    sublime.active_window().focus_view(panel.opener)
    return None

  if os.path.isdir(path):
    open_folder_by_panel(panel, path)

  panel.close()
  return open_file(path)

def open_folder_by_panel(panel, path = None, args = {}):
  if path == None:
    path = panel.get_current_value()

  panel.set_text('')
  caller = panel.get_caller('folder_files')
  if caller != None:
    caller.goto(path)
    return caller

  args['path'] = path
  return FolderFiles(**args).show()

class StatusResetter(sublime_plugin.EventListener):
  def on_activated(self, view):
    status_message.erase(view, 'folder_files_status')
import sublime
import sublime_plugin
import os
import re

from FolderFiles.folder_files import(FolderFiles, open_file_or_folder_by_panel,
  open_folder_by_panel)

try:
  from FileList.file_list import open_file, get_short_path
  from QuickSearchEnhanced import quick_search
  from OpenPath.open_path import open_path
except ImportError:
  sublime.error_message("Dependency import failed; please read readme for " +
   "FolderFiles plugin for installation instructions; to disable this " +
   "message remove this plugin")

class FolderFilesHelper(sublime_plugin.TextCommand):
  def _get_panels(self):
    panel = quick_search.panels.get_current()
    folder_files = panel and panel.get_caller('folder_files')
    return panel, folder_files

  def _get_file_list_panels(self):
    panel = quick_search.panels.get_current()
    folder_files = panel and panel.get_caller('file_list')
    return panel, folder_files

class OpenFolderInList(FolderFilesHelper):
  def run(self, edit):
    panel, _ = self._get_file_list_panels()
    if panel == None:
      return

    open_file_or_folder_by_panel(panel)

class OpenFileManagerForFolderInList(FolderFilesHelper):
  def run(self, edit):
    _, folder_files = self._get_panels()
    if folder_files == None:
      return

    open_path(folder_files.get_current_path())

class OpenExactFileInList(FolderFilesHelper):
  def run(self, edit):
    panel, folder_files = self._get_panels()
    if folder_files == None:
      return

    path = panel.get_current_text()
    if path[0:1] != '/':
      path = folder_files.get_current_path() + '/' + path

    open_file_or_folder_by_panel(panel, path)

class OpenFileInList(FolderFilesHelper):
  def run(self, edit):
    panel, folder_files = self._get_panels()
    if folder_files == None:
      return

    sublime.active_window().open_file(panel.get_current_value())

class PreviewFileInList(FolderFilesHelper):
  def run(self, edit):
    panel, folder_files = self._get_panels()
    if folder_files == None:
      return

    sublime.active_window().open_file(panel.get_current_value(),
      sublime.TRANSIENT)

class GotoFolderInList(FolderFilesHelper):
  def run(self, edit, path):
    _, folder_files = self._get_panels()
    if folder_files == None:
      return

    match = re.match(r'\$(\d)', path)
    if match != None:
      folder_files.goto(self.view.window().folders()[int(match.group(1))])
    elif path == '$ROOT':
      path = folder_files.get_current_path()
      for folder in self.view.window().folders():
        if folder == path[0:len(folder)]:
          folder_files.goto(folder)
          break
    elif path == '$UP':
      folder_files.goto_up()
    elif path == '$DOWN':
      folder_files.goto_down()
    else:
      folder_files.goto(os.path.expanduser(path))

class CreateFolderInList(FolderFilesHelper):
  def run(self, edit):
    panel = quick_search.panels.get_current()
    folder_files = panel and panel.get_caller('folder_files')
    if folder_files == None:
      return

    path = folder_files.get_path() + '/' +panel.get_current_text()
    os.mkdir(path)
    folder_files.goto(path)
    panel.set_text('')

class FindInCurrentFileFolder(FolderFilesHelper):
  def run(self, edit):
    panel, folder_files = self._get_panels()
    panel.close(False, None)
    sublime.active_window().focus_view(panel.get_opener())

    path, _ = get_short_path(folder_files.get_path())
    sublime.active_window().run_command('show_panel', {"panel": "find_in_files",
      "where": path + '/'})